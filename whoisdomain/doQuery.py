import sys
import os

from typing import (
    cast,
    Optional,
    List,
    Dict,
    Tuple,
    Any,
)

from .exceptions import (
    UnknownTld,
    WhoisPrivateRegistry,
)

from ._0_init_tld import (
    TLD_RE,
    filterTldToSupportedPattern,
)

from .doWhoisCommand import (
    doWhoisAndReturnString,
)

from .doParse import (
    do_parse,
)


from .domain import Domain
from .parameterContext import ParameterContext


WHOISDOMAIN: str = ""
if os.getenv("WHOISDOMAIN"):
    WHOISDOMAIN = str(os.getenv("WHOISDOMAIN"))

WD = WHOISDOMAIN.upper().split(":")

SIMPLISTIC = False
if "SIMPISTIC" in WD:
    SIMPLISTIC = True

CACHE_FILE = None
SLOW_DOWN = 0

LastWhois: Dict[str, Any] = {
    "Try": [],
}


def get_last_raw_whois_data() -> Dict[str, Any]:
    global LastWhois
    return LastWhois


def _internationalizedDomainNameToPunyCode(d: List[str]) -> List[str]:
    return [k.encode("idna").decode() or k for k in d]


def _fromDomainStringToTld(
    domain: str,
    pc: ParameterContext,
) -> Tuple[Optional[str], Optional[List[str]]]:
    domain = domain.lower().strip().rstrip(".")  # Remove the trailing dot to support FQDN.

    dList: List[str] = domain.split(".")
    if pc.verbose:
        print(dList, file=sys.stderr)

    if dList[0] == "www":
        dList = dList[1:]

    if len(dList) == 1:
        return None, None

    tldString: str = filterTldToSupportedPattern(domain, dList, pc.verbose)  # may raise UnknownTld
    if pc.verbose:
        print(f"filterTldToSupportedPattern returns tld: {tldString}", file=sys.stderr)

    if pc.internationalized and isinstance(pc.internationalized, bool):
        dList = _internationalizedDomainNameToPunyCode(dList)

    if pc.verbose:
        print(tldString, dList, file=sys.stderr)

    return tldString, dList


def _validateWeKnowTheToplevelDomain(
    tldString: str,
    pc: ParameterContext,
) -> Optional[str]:
    # may raise UnknownTld
    if pc.return_raw_text_for_unsupported_tld:
        # we dont raise we return None so we can handle unsupported domains anyway
        return None

    a = f"The TLD {tldString} is currently not supported by this package."
    b = "Use validTlds() to see what toplevel domains are supported."
    msg = f"{a} {b}"
    return msg


def _verifyPrivateRegistry(
    thisTld: Dict[str, Any],
    pc: ParameterContext,
) -> bool:
    # may raise WhoisPrivateRegistry
    # signal we know the tld but it has no whos or does not respond with any information
    if thisTld.get("_privateRegistry"):
        if pc.simplistic is False:
            msg = "WhoisPrivateRegistry"
            raise WhoisPrivateRegistry(msg)
        return True
    return False


def _doServerHintsForThisTld(
    tldString: str,
    thisTld: Dict[str, Any],
    pc: ParameterContext,
) -> Optional[str]:
    # note _server hints currently are not passes down when using "extend", that may have been my error during the initial implementation
    # allow server hints using "_server" from the tld_regexpr.py file
    thisTldServer = thisTld.get("_server")
    if pc.server is None and thisTldServer:
        pc.server = thisTldServer
        if pc.verbose:
            print(f"using _server hint {pc.server} for tld: {tldString}", file=sys.stderr)
        return str(pc.server)
    return None


def _doSlowdownHintForThisTld(
    tldString: str,
    thisTld: Dict[str, Any],
    pc: ParameterContext,
) -> int:
    # allow a configrable slowdown for some tld's
    slowDown = thisTld.get("_slowdown")
    if slowDown:
        if pc.slow_down == 0 and slowDown > 0:
            pc.slow_down = slowDown
            if pc.verbose:
                print(f"using _slowdown hint {slowDown} for tld: {tldString}", file=sys.stderr)
    return int(pc.slow_down)


def _doUnsupportedTldAnyway(
    tldString: str,
    dList: List[str],
    pc: ParameterContext,
) -> Optional[Domain]:
    pc.include_raw_whois_text = True

    # we will not hunt for possible valid first level domains as we have no actual feedback

    whoisStr = doWhoisAndReturnString(
        dList=dList,
        pc=pc,
    )

    # we will only return minimal data
    data = {
        "tld": tldString,
        "domain_name": [],
    }
    data["domain_name"] = [".".join(dList)]  # note the fields are default all array, except tld

    if pc.verbose:
        print(data, file=sys.stderr)

    pc.return_raw_text_for_unsupported_tld = (True,)
    return Domain(
        data=data,
        pc=pc,
        whoisStr=whoisStr,
    )


def _doOneLookup(
    tldString: str,
    dList: List[str],
    pc: ParameterContext,
) -> Optional[Domain]:

    try:
        whoisStr = doWhoisAndReturnString(
            dList=dList,
            pc=pc,
        )
    except Exception as e:
        if pc.simplistic:
            return Domain(
                data={},
                pc=pc,
                whoisStr=None,
                exeptionStr=f"{e}",
            )

        raise e

    LastWhois["Try"].append(
        {
            "Domain": ".".join(dList),
            "rawData": whoisStr,
            "server": pc.server,
        }
    )

    data = do_parse(
        whoisStr=whoisStr,
        tldString=tldString,
        dList=dList,
        pc=pc,
    )

    if isinstance(data, Domain):
        return data

    # do we have a result and does it have a domain name
    if data and data["domain_name"][0]:
        return Domain(
            data=data,
            pc=pc,
            whoisStr=whoisStr,
        )
    return None


def query(
    domain: str,
    force: bool = False,
    cache_file: Optional[str] = None,
    cache_age: int = 60 * 60 * 48,
    slow_down: int = 0,
    ignore_returncode: bool = False,
    server: Optional[str] = None,
    verbose: bool = False,
    with_cleanup_results: bool = False,
    internationalized: bool = False,
    include_raw_whois_text: bool = False,
    return_raw_text_for_unsupported_tld: bool = False,
    timeout: Optional[float] = None,
    parse_partial_response: bool = False,
    cmd: str = "whois",
    simplistic: bool = False,
    withRedacted: bool = False,
    pc: Optional[ParameterContext] = None,
) -> Optional[Domain]:
    # see documentation about paramaters in parameterContext.py

    if pc is None:
        pc = ParameterContext(
            force=force,
            cache_file=cache_file,
            cache_age=cache_age,
            slow_down=slow_down,
            ignore_returncode=ignore_returncode,
            server=server,
            verbose=verbose,
            with_cleanup_results=with_cleanup_results,
            internationalized=internationalized,
            include_raw_whois_text=include_raw_whois_text,
            return_raw_text_for_unsupported_tld=return_raw_text_for_unsupported_tld,
            timeout=float(timeout) if timeout else float(0),
            parse_partial_response=parse_partial_response,
            cmd=cmd,
            simplistic=simplistic,
            withRedacted=withRedacted,
        )
    # else:

    global LastWhois
    LastWhois["Try"] = []  # init on start of query

    assert isinstance(domain, str), Exception("`domain` - must be <str>")
    return_raw_text_for_unsupported_tld = bool(return_raw_text_for_unsupported_tld)

    # =================================================
    try:
        tldString, dList = _fromDomainStringToTld(  # may raise UnknownTld
            domain,
            pc=pc,
        )
        if tldString is None:
            return None

    except Exception as e:
        if pc.simplistic:
            return Domain(
                data={},
                pc=pc,
                whoisStr=None,
                exeptionStr="UnknownTld",
            )

        raise (e)

    # =================================================
    dList = cast(List[str], dList)
    if tldString not in TLD_RE.keys():
        msg = _validateWeKnowTheToplevelDomain(
            tldString=tldString,
            pc=pc,
        )

        if msg is None:
            return _doUnsupportedTldAnyway(
                tldString=tldString,
                dList=dList,
                pc=pc,
            )
        if pc.simplistic:
            return Domain(
                data={},
                pc=pc,
                whoisStr=None,
                exeptionStr="UnknownTld",
            )

        raise UnknownTld(msg)

    # =================================================
    thisTld = cast(Dict[str, Any], TLD_RE.get(tldString))

    if _verifyPrivateRegistry(
        thisTld=thisTld,
        pc=pc,
    ):  # may raise WhoisPrivateRegistry
        msg = "This tld has either no whois server or responds only with minimal information"
        return Domain(
            data={},
            pc=pc,
            whoisStr=None,
            exeptionStr=msg,
        )

    # =================================================
    pc.server = _doServerHintsForThisTld(
        tldString=tldString,
        thisTld=thisTld,
        pc=pc,
    )

    pc.slow_down = pc.slow_down or SLOW_DOWN
    pc.slow_down = _doSlowdownHintForThisTld(
        tldString=tldString,
        thisTld=thisTld,
        pc=pc,
    )

    # if the tld is a multi level we should not move further down than the tld itself
    # we currently allow progressive lookups until we find something:
    # so xxx.yyy.zzz will try both xxx.yyy.zzz and yyy.zzz
    # but if the tld is yyy.zzz we should only try xxx.yyy.zzz

    pc.cache_file = pc.cache_file or CACHE_FILE
    tldLevel = tldString.split(".")
    while 1:
        result = _doOneLookup(
            tldString=tldString,
            dList=dList,
            pc=pc,
        )
        if result:
            return result

        if len(dList) > (len(tldLevel) + 1):
            dList = dList[1:]  # strip one element from the front and try again
            if verbose:
                print(f"try again with {dList}, {len(dList)}, {len(tldLevel) + 1}", file=sys.stderr)
            continue

        # no result or no domain but we can not reduce any further so we have None
        return None

    return None
