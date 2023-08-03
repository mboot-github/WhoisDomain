#! /usr/bin/env python3

import re
import sys

from typing import (
    cast,
    Any,
    Dict,
    Optional,
    List,
    Tuple,
)

from .exceptions import (
    FailedParsingWhoisOutput,
    WhoisQuotaExceeded,
)

from ._0_init_tld import TLD_RE

from .domain import Domain


from .parameterContext import ParameterContext

Verbose: bool = True

NONESTRINGS: List[str] = [
    "the domain has not been registered",
    "no match found for",
    "no matching record",
    "no match",
    "not found",
    "no data found",
    "no entries found",
    # "status: free", # we should not interprete the result if there is a result
    "no such domain",
    "the queried object does not exist",
    "domain you requested is not known",
    # "status: available", # we should not interprete the result if there is a result
    "no whois server is known for this kind of object",
    "nameserver not found",
    "malformed request",  # this means this domain is not in whois as it is on top of a registered domain
    "registration of this domain is restricted",
    "restricted",
    "this domain is currently available",
]


def NoneStrings() -> List[str]:
    return NONESTRINGS


def NoneStringsAdd(aString: str) -> None:
    if aString and isinstance(aString, str) and len(aString) > 0:
        NONESTRINGS.append(aString)


QUOTASTRINGS: List[str] = [
    "limit exceeded",
    "quota exceeded",
    "try again later",
    "please try again",
    "exceeded the maximum allowable number",
    "can temporarily not be answered",
    "please try again.",
    "queried interval is too short",
    "number of allowed queries exceeded",
]


def QuotaStrings() -> List[str]:
    return QUOTASTRINGS


def QuotaStringsAdd(aString: str) -> None:
    if aString and isinstance(aString, str) and len(aString) > 0:
        NONESTRINGS.append(aString)


def _handleShortResponse(
    tldString: str,
    dList: List[str],
    whoisStr: str,
    pc: ParameterContext,
) -> Optional[Domain]:
    if pc.verbose:
        d = ".".join(dList)
        print(f"line count < 5:: {tldString} {d} {whoisStr}", file=sys.stderr)

    # TODO: some short responses are actually valid:
    # lookfor Domain: and Status but all other fields are missing so the regexec could fail
    # this domain is taken already or reserved

    # whois syswow.64-b.it
    # [Querying whois.nic.it]
    # [whois.nic.it]
    # Domain:             syswow.64-b.it
    # Status:             UNASSIGNABLE

    s = whoisStr.strip().lower()

    # NOTE: from here s is lowercase only
    # ---------------------------------
    noneStrings = NoneStrings()
    for i in noneStrings:
        if i in s:
            return None

    # ---------------------------------
    # is there any error string in the result
    if s.count("error"):
        if pc.verbose:
            print("i see 'error' in the result, return: None", file=sys.stderr)
        return None

    # ---------------------------------
    quotaStrings = QuotaStrings()
    for i in quotaStrings:
        if i in s:
            if pc.simplistic:
                msg = "WhoisQuotaExceeded"
                return Domain(
                    data={},
                    pc=pc,
                    whoisStr=whoisStr,
                    exeptionStr=msg,
                )
            raise WhoisQuotaExceeded(whoisStr)

    if pc.simplistic:
        msg = "FailedParsingWhoisOutput"
        return Domain(
            data={},
            pc=pc,
            whoisStr=whoisStr,
            exeptionStr=msg,
        )

    raise FailedParsingWhoisOutput(whoisStr)


def _doDnsSec(
    whoisStr: str,
    pc: ParameterContext,
) -> bool:
    whoisDnsSecList: List[str] = whoisStr.split("DNSSEC:")
    if len(whoisDnsSecList) >= 2:
        if pc.verbose:
            msg = "i have seen dnssec: {whoisDnsSecStr}"
            print(msg, file=sys.stderr)

        whoisDnsSecStr: str = whoisDnsSecList[1].split("\n")[0]
        if whoisDnsSecStr.strip() == "signedDelegation" or whoisDnsSecStr.strip() == "yes":
            return True
    return False


def _doIfServerNameLookForDomainName(
    whoisStr: str,
    pc: ParameterContext,
) -> str:
    # not often available anymore
    if re.findall(r"Server Name:\s?(.+)", whoisStr, re.IGNORECASE):
        if pc.verbose:
            msg = "i have seen Server Name:, looking for Domain Name:"
            print(msg, file=sys.stderr)
        whoisStr = whoisStr[whoisStr.find("Domain Name:") :]
    return whoisStr


def _doExtractPattensIanaFromWhoisString(
    tldString: str,
    r: Dict[str, Any],
    whoisStr: str,
    pc: ParameterContext,
) -> Dict[str, Any]:
    # now handle the actual format if this whois response
    iana = {
        "domain_name": r"domain:\s?([^\n]+)",
        "registrar": r"organisation:\s?([^\n]+)",
        "creation_date": r"created:\s?([^\n]+)",
    }
    for k, v in iana.items():
        zz = re.findall(v, whoisStr)
        if zz:
            if pc.verbose:
                print(f"parsing iana data only for tld: {tldString}, {zz}", file=sys.stderr)
            r[k] = zz
    return r


def _doExtractPattensFromWhoisString(
    tldString: str,
    r: Dict[str, Any],
    whoisStr: str,
    pc: ParameterContext,
) -> Dict[str, Any]:
    for k, v in TLD_RE.get(tldString, TLD_RE["com"]).items():  # use TLD_RE["com"] as default if a regex is missing
        if k.startswith("_"):  # skip meta element like: _server or _privateRegistry
            continue

        # Historical: here we use 'empty string' as default, not None
        if v is None:
            r[k] = [""]
        else:
            r[k] = v.findall(whoisStr) or [""]

    return r


def _doSourceIana(
    tldString: str,
    r: Dict[str, Any],
    whoisStr: str,
    pc: ParameterContext,
) -> Tuple[str, Optional[Dict[str, Any]]]:
    # here we can handle the example.com and example.net permanent IANA domains
    k = "source:       IANA"

    if pc.verbose:
        msg = f"i have seen {k}"
        print(msg, file=sys.stderr)

    whois_splitted = whoisStr.split(k)
    z = len(whois_splitted)
    if z > 2:
        return k.join(whois_splitted[1:]), None

    if z == 2 and whois_splitted[1].strip() != "":
        # if we see source: IANA and the part after is not only whitespace
        if pc.verbose:
            msg = f"after: {k} we see not only whitespace: {whois_splitted[1]}"
            print(msg, file=sys.stderr)

        return whois_splitted[1], None

    # try to parse this as a IANA domain as after is only whitespace
    r = _doExtractPattensFromWhoisString(
        tldString,
        r,
        whoisStr,
        pc=pc,
    )  # set default values

    # now handle the actual format if this whois response
    r = _doExtractPattensIanaFromWhoisString(
        tldString,
        r,
        whoisStr,
        pc=pc,
    )

    return whoisStr, r


# PUBLIC


def cleanupWhoisResponse(
    whoisStr: str,
    verbose: bool = False,
    with_cleanup_results: bool = False,
    withRedacted: bool = False,
    # pc: ParameterContext, # later as this func can be used from outside tha package
) -> str:
    tmp2: List[str] = []

    # note we cannot do yet rstrip() on the lines as many registrars use \r and even trailing whitespace after entries
    # as the resulting matches are all stripped of leading and trailing whitespace this currently is fixed there
    # and relaxes the regexes: you will often see a capture with (.*)
    # we would have to fix all regexes to allow stripping all trailing whitespace
    # it would make many matches easier though.

    skipFromHere = False
    tmp: List[str] = whoisStr.split("\n")
    for line in tmp:
        if skipFromHere is True:
            continue

        # some servers respond with: % Quota exceeded in the comment section (lines starting with %)
        if "quota exceeded" in line.lower():
            raise WhoisQuotaExceeded(whoisStr)

        if with_cleanup_results is True and line.startswith("%"):  # only remove if requested
            continue

        if withRedacted is False:
            if "REDACTED FOR PRIVACY" in line:  # these lines contibute nothing so ignore
                continue

        if "Please query the RDDS service of the Registrar of Record" in line:  # these lines contibute nothing so ignore
            continue

        # regular responses may at the end have meta info starting with a line >>> some texte <<<
        # similar trailing info exists with lines starting with -- but we wil handle them later
        # unfortunalery we have domains (google.st) that have this early at the top
        if 0:
            if line.startswith(">>>"):
                skipFromHere = True
                continue

        if line.startswith("Terms of Use:"):  # these lines contibute nothing so ignore
            continue

        tmp2.append(line.strip("\r"))

    return "\n".join(tmp2)


def do_parse(
    whoisStr: str,
    tldString: str,
    dList: List[str],
    pc: ParameterContext,
) -> Any:

    whoisStr = cleanupWhoisResponse(
        whoisStr=whoisStr,
        verbose=pc.verbose,
        with_cleanup_results=pc.with_cleanup_results,
        withRedacted=pc.withRedacted,
    )

    if whoisStr.count("\n") < 5:
        result = _handleShortResponse(  # may raise:    FailedParsingWhoisOutput,    WhoisQuotaExceeded,
            tldString=tldString,
            dList=dList,
            whoisStr=whoisStr,
            pc=pc,
        )
        return result

    # this is the beginning of the return data
    r: Dict[str, Any] = {
        "tld": tldString,
        "DNSSEC": _doDnsSec(whoisStr=whoisStr, pc=pc),
    }

    if "source:       IANA" in whoisStr:  # prepare for handling historical IANA domains
        whoisStr, ianaDomain = _doSourceIana(
            tldString,
            r=r,
            whoisStr=whoisStr,
            pc=pc,
        )
        if ianaDomain is not None:
            ianaDomain = cast(
                Optional[Dict[str, Any]],
                ianaDomain,
            )
            return ianaDomain

    if "Server Name" in whoisStr:  # handle old type Server Name (not very common anymore)
        whoisStr = _doIfServerNameLookForDomainName(
            whoisStr,
            pc.verbose,
        )

    return _doExtractPattensFromWhoisString(
        tldString=tldString,
        r=r,
        whoisStr=whoisStr,
        pc=pc,
    )
