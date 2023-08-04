#! /usr/bin/env python3

from typing import (
    Any,
    Dict,
    Optional,
    List,
    Tuple,
)

import re
import sys

from .exceptions import (
    FailedParsingWhoisOutput,
    WhoisQuotaExceeded,
)

from ._0_init_tld import TLD_RE
from .domain import Domain
from .parameterContext import ParameterContext
from .noneStrings import NoneStrings
from .quotaStrings import QuotaStrings


class WhoisParser:
    tldString: str
    dList: List[str]
    whoisStr: str
    pc: ParameterContext
    resultDict: Dict[str, Any]

    def __init__(
        self,
        tldString: str,
        dList: List[str],
        whoisStr: str,
        pc: ParameterContext,
    ) -> None:
        self.tldString = tldString
        self.dList = dList
        self.whoisStr = whoisStr
        self.pc = pc
        self.resultDict: Dict[str, Any] = {
            "tld": tldString,
            "DNSSEC": self._doDnsSec(),
        }

    def _doExtractPattensIanaFromWhoisString(
        self,
        # resultDict: Dict[str, Any],
    ) -> Dict[str, Any]:
        # now handle the actual format if this whois response
        iana = {
            "domain_name": r"domain:\s?([^\n]+)",
            "registrar": r"organisation:\s?([^\n]+)",
            "creation_date": r"created:\s?([^\n]+)",
        }
        for k, v in iana.items():
            zz = re.findall(v, self.whoisStr)
            if zz:
                if self.pc.verbose:
                    print(f"parsing iana data only for tld: {self.tldString}, {zz}", file=sys.stderr)
                self.resultDict[k] = zz
        return self.resultDict

    def _doExtractPattensFromWhoisString(
        self,
        # resultDict: Dict[str, Any],
    ) -> Dict[str, Any]:
        for k, v in TLD_RE.get(self.tldString, TLD_RE["com"]).items():  # use TLD_RE["com"] as default if a regex is missing
            if k.startswith("_"):  # skip meta element like: _server or _privateRegistry
                continue

            # Historical: here we use 'empty string' as default, not None
            if v is None:
                self.resultDict[k] = [""]
            else:
                self.resultDict[k] = v.findall(self.whoisStr) or [""]

        return self.resultDict

    def _doSourceIana(
        self,
        # resultDict: Dict[str, Any],
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        # here we can handle the example.com and example.net permanent IANA domains
        k: str = "source:       IANA"

        if self.pc.verbose:
            msg: str = f"i have seen {k}"
            print(msg, file=sys.stderr)

        whois_splitted: List[str] = self.whoisStr.split(k)
        z: int = len(whois_splitted)
        if z > 2:
            return k.join(whois_splitted[1:]), None

        if z == 2 and whois_splitted[1].strip() != "":
            # if we see source: IANA and the part after is not only whitespace
            if self.pc.verbose:
                msg = f"after: {k} we see not only whitespace: {whois_splitted[1]}"
                print(msg, file=sys.stderr)

            return whois_splitted[1], None

        # try to parse this as a IANA domain as after is only whitespace
        self.resultDict = self._doExtractPattensFromWhoisString()  # self.resultDict,

        # now handle the actual format if this whois response
        self.resultDict = self._doExtractPattensIanaFromWhoisString()  # self.resultDict,

        return self.whoisStr, self.resultDict

    def _doIfServerNameLookForDomainName(self) -> None:
        # not often available anymore
        if re.findall(r"Server Name:\s?(.+)", self.whoisStr, re.IGNORECASE):
            if self.pc.verbose:
                msg = "i have seen Server Name:, looking for Domain Name:"
                print(msg, file=sys.stderr)
            self.whoisStr = self.whoisStr[self.whoisStr.find("Domain Name:") :]
        # return self.whoisStr

    def _doDnsSec(
        self,
    ) -> bool:
        whoisDnsSecList: List[str] = self.whoisStr.split("DNSSEC:")
        if len(whoisDnsSecList) >= 2:
            if self.pc.verbose:
                msg = "i have seen dnssec: {whoisDnsSecStr}"
                print(msg, file=sys.stderr)

            whoisDnsSecStr: str = whoisDnsSecList[1].split("\n")[0]
            if whoisDnsSecStr.strip() == "signedDelegation" or whoisDnsSecStr.strip() == "yes":
                return True
        return False

    def _handleShortResponse(
        self,
    ) -> Optional[Domain]:
        if self.pc.verbose:
            d = ".".join(self.dList)
            print(f"line count < 5:: {self.tldString} {d} {self.whoisStr}", file=sys.stderr)

        # TODO: some short responses are actually valid:
        # lookfor Domain: and Status but all other fields are missing so the regexec could fail
        # this domain is taken already or reserved

        # whois syswow.64-b.it
        # [Querying whois.nic.it]
        # [whois.nic.it]
        # Domain:             syswow.64-b.it
        # Status:             UNASSIGNABLE

        s = self.whoisStr.strip().lower()

        # NOTE: from here s is lowercase only
        # ---------------------------------
        noneStrings = NoneStrings()
        for i in noneStrings:
            if i in s:
                return None

        # ---------------------------------
        # is there any error string in the result
        if s.count("error"):
            if self.pc.verbose:
                print("i see 'error' in the result, return: None", file=sys.stderr)
            return None

        # ---------------------------------
        quotaStrings = QuotaStrings()
        for i in quotaStrings:
            if i in s:
                if self.pc.simplistic:
                    msg = "WhoisQuotaExceeded"
                    return Domain(
                        data={},
                        pc=self.pc,
                        whoisStr=self.whoisStr,
                        exeptionStr=msg,
                    )
                raise WhoisQuotaExceeded(self.whoisStr)

        if self.pc.simplistic:
            msg = "FailedParsingWhoisOutput"
            return Domain(
                data={},
                pc=self.pc,
                whoisStr=self.whoisStr,
                exeptionStr=msg,
            )

        raise FailedParsingWhoisOutput(self.whoisStr)
