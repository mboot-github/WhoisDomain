import sys
import os

from typing import (
    cast,
    Optional,
    List,
    Dict,
    Any,
)

from .exceptions import (
    UnknownTld,
)

from ._0_init_tld import TLD_RE
from .domain import Domain
from .parameterContext import ParameterContext
from .processWhoisDomainRequest import ProcessWhoisDomainRequest
from .lastWhois import initLastWhois


WHOISDOMAIN: str = ""
if os.getenv("WHOISDOMAIN"):
    WHOISDOMAIN = str(os.getenv("WHOISDOMAIN"))

WD = WHOISDOMAIN.upper().split(":")

SIMPLISTIC = False
if "SIMPISTIC" in WD:
    SIMPLISTIC = True

# CACHE_FILE = None


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
    # if you use pc as argument all above params (except domain are ignored)
) -> Optional[Domain]:
    # see documentation about paramaters in parameterContext.py

    assert isinstance(domain, str), Exception("`domain` - must be <str>")

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

    # pc.cache_file = pc.cache_file or None

    initLastWhois()

    pwdr = ProcessWhoisDomainRequest(
        domain=domain,
        pc=pc,
    )
    # =================================================
    try:
        domain, tldString, dList = pwdr._fromDomainStringToTld()  # may raise UnknownTld
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
        else:
            raise (e)

    pwdr.setThisTldSring(tldString)

    # =================================================
    dList = cast(List[str], dList)
    if tldString not in TLD_RE.keys():
        msg = pwdr.makeMessageForUnsupportedTld()
        if msg is None:
            return pwdr._doUnsupportedTldAnyway(
                dList=dList,
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
    pwdr.setThisTldEntry(cast(Dict[str, Any], TLD_RE.get(tldString)))

    if pwdr._verifyPrivateRegistry():  # may raise WhoisPrivateRegistry
        msg = "This tld has either no whois server or responds only with minimal information"
        return Domain(
            data={},
            pc=pc,
            whoisStr=None,
            exeptionStr=msg,
        )

    # =================================================
    pwdr._doServerHintsForThisTld()
    pwdr._doSlowdownHintForThisTld()

    # if the tld is a multi level we should not move further down than the tld itself
    # we currently allow progressive lookups until we find something:
    # so xxx.yyy.zzz will try both xxx.yyy.zzz and yyy.zzz
    # but if the tld is yyy.zzz we should only try xxx.yyy.zzz

    tldLevel = tldString.split(".")
    while True:  # loop until we decide we are done
        result = pwdr.doOneLookup(
            tldString=tldString,
            dList=dList,
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
