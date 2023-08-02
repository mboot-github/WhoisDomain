import sys
import os
from functools import wraps
from typing import (
    cast,
    Optional,
    List,
    Dict,
    Tuple,
    Any,
    Callable,
)


from ._1_query import (
    do_query,
    CACHE_STUB,
)

from ._2_parse import (
    do_parse,
    NoneStrings,
    NoneStringsAdd,
    QuotaStrings,
    QuotaStringsAdd,
    cleanupWhoisResponse,
)

from ._3_adjust import (
    Domain,
)

from .tld_regexpr import (
    ZZ,
)

from ._0_init_tld import (
    TLD_RE,
    validTlds,
    filterTldToSupportedPattern,
    mergeExternalDictWithRegex,
)

from .exceptions import (
    UnknownTld,
    FailedParsingWhoisOutput,
    UnknownDateFormat,
    WhoisCommandFailed,
    WhoisPrivateRegistry,
    WhoisQuotaExceeded,
    WhoisCommandTimeout,
)

from .version import (
    VERSION,
)

from .parameterContext import ParameterContext

TLD_LIB_PRESENT: bool = False
try:
    import tld as libTld

    TLD_LIB_PRESENT = True
except Exception as e:
    _ = e  # ignore any error

__all__ = [
    # from exceptions
    "UnknownTld",
    "FailedParsingWhoisOutput",
    "UnknownDateFormat",
    "WhoisCommandFailed",
    "WhoisPrivateRegistry",
    "WhoisQuotaExceeded",
    "WhoisCommandTimeout",
    # from init_tld
    "validTlds",
    "TLD_RE",
    # from version
    "VERSION",
    # from this file
    "get_last_raw_whois_data",
    "getVersion",
    "getTestHint",
    "query",
    # from query
    "CACHE_STUB",
    # from parse
    "NoneStrings",
    "NoneStringsAdd",
    "QuotaStrings",
    "QuotaStringsAdd",
    "cleanupWhoisResponse",
]

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


# PRIVATE


def _internationalizedDomainNameToPunyCode(d: List[str]) -> List[str]:
    return [k.encode("idna").decode() or k for k in d]


def _result2dict(func: Any) -> Any:
    @wraps(func)
    def _inner(*args: str, **kw: Any) -> Dict[str, Any]:
        r = func(*args, **kw)
        return r and vars(r) or {}

    return _inner


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

    whoisStr = do_query(
        dList=dList,
        slow_down=pc.slow_down,
        ignore_returncode=pc.ignore_returncode,
        server=pc.server,
        verbose=pc.verbose,
        wh=pc.cmd,
        simplistic=pc.simplistic,
    )

    # we will only return minimal data
    data = {
        "tld": tldString,
        "domain_name": [],
    }
    data["domain_name"] = [".".join(dList)]  # note the fields are default all array, except tld

    if pc.verbose:
        print(data, file=sys.stderr)

    return Domain(
        data=data,
        whoisStr=whoisStr,
        verbose=pc.verbose,
        include_raw_whois_text=pc.include_raw_whois_text,
        return_raw_text_for_unsupported_tld=True,
    )


def _doOneLookup(
    tldString: str,
    dList: List[str],
    pc: ParameterContext,
) -> Optional[Domain]:

    try:
        whoisStr = do_query(
            dList=dList,
            force=pc.force,
            cache_file=pc.cache_file,
            cache_age=pc.cache_age,
            slow_down=pc.slow_down,
            ignore_returncode=pc.ignore_returncode,
            server=pc.server,
            verbose=pc.verbose,
            timeout=pc.timeout,
            parse_partial_response=pc.parse_partial_response,
            wh=pc.cmd,
            simplistic=pc.simplistic,
        )
    except Exception as e:
        if pc.simplistic:
            return Domain(
                data={},
                whoisStr=None,
                verbose=pc.verbose,
                include_raw_whois_text=pc.include_raw_whois_text,
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
        verbose=pc.verbose,
        with_cleanup_results=pc.with_cleanup_results,
        simplistic=pc.simplistic,
        include_raw_whois_text=pc.include_raw_whois_text,
        withRedacted=pc.withRedacted,
    )

    if isinstance(data, Domain):
        return data

    # do we have a result and does it have a domain name
    if data and data["domain_name"][0]:
        return Domain(
            data=data,
            whoisStr=whoisStr,
            verbose=pc.verbose,
            include_raw_whois_text=pc.include_raw_whois_text,
        )
    return None


def get_last_raw_whois_data() -> Dict[str, Any]:
    global LastWhois
    return LastWhois


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
) -> Optional[Domain]:
    """
    force=True          Don't use cache.
    cache_file=<path>   Use file to store cache not only memory.
    cache_age=172800    Cache expiration time for given domain, in seconds
    slow_down=0         Time [s] it will wait after you query WHOIS database.
                        This is useful when there is a limit to the number of requests at a time.
    server:             if set use the whois server explicitly for making the query:
                        propagates on linux to "whois -h <server> <domain>"
                        propagates on Windows to whois.exe <domain> <server>
    with_cleanup_results: cleanup lines starting with % and REDACTED FOR PRIVACY
    internationalized:  if true convert with internationalizedDomainNameToPunyCode().
    ignore_returncode:  if true and the whois command fails with code 1, still process the data returned as normal.
    verbose:            if true, print relevant information on steps taken to standard error
    include_raw_whois_text:
                        if reqested the full response is also returned.
    return_raw_text_for_unsupported_tld:
                        if the tld is unsupported, just try it anyway but return only the raw text.
    timeout:            timeout in seconds for the whois command to return a result.
    parse_partial_response:
                        try to parse partial response when cmd timed out (stdbuf should be in PATH for best results)
    cmd:                explicitly specify the path to the whois you want to use.
    simplistic:         when simplistic is True we return None for most exceptions and dont pass info why we have no data.
    withRedacted:       show redacted output , default no redacted data is shown
    """

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

    global LastWhois
    LastWhois["Try"] = []  # init on start of query

    # wh: str = cmd  # make it compatible with python-whois-extended

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
                whoisStr=None,
                verbose=verbose,
                include_raw_whois_text=include_raw_whois_text,
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
                whoisStr=None,
                verbose=verbose,
                include_raw_whois_text=include_raw_whois_text,
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
            whoisStr=None,
            verbose=verbose,
            include_raw_whois_text=include_raw_whois_text,
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

    cache_file = cache_file or CACHE_FILE
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


# Add get function to support return result in dictionary form
get = _result2dict(query)


def getVersion() -> str:
    return VERSION


def getTestHint(tldString: str) -> Optional[str]:
    if tldString not in ZZ:
        return None

    k: str = "_test"
    if k not in ZZ[tldString]:
        return None

    return str(ZZ[tldString][k])
