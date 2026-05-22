# pylint: disable=duplicate-code
"""
Module providing all public accessible functions and data for the whoisdomain package.

## optional modules supported:

- if the tld library is installed you can use the `withPublicSuffix:bool` option

All public data is vizible via the __all__ List
"""

import logging
import os
import sys
from functools import wraps
from typing import Any

from .cache.dbmCache import DBMCache
from .cache.dummyCache import DummyCache
from .cache.simpleCacheBase import SimpleCacheBase
from .cache.simpleCacheWithFile import SimpleCacheWithFile
from .context.dataContext import DataContext
from .context.parameterContext import ParameterContext
from .domain import Domain
from .doWhoisCommand import setMyCache
from .exceptions import (
    FailedParsingWhoisOutputError,
    UnknownDateFormatError,
    UnknownTldError,
    WhoisCommandFailedError,
    WhoisCommandTimeoutError,
    WhoisPrivateRegistryError,
    WhoisQuotaExceededError,
)
from .helpers import (
    cleanupWhoisResponse,
    filterTldToSupportedPattern,
    get_TLD_RE,
    getTestHint,
    getVersion,
    mergeExternalDictWithRegex,
    validTlds,
)
from .lastWhois import (
    get_last_raw_whois_data,
    initLastWhois,
)
from .processWhoisDomainRequest import ProcessWhoisDomainRequest
from .procFunc import ProcFunc
from .strings.noneStrings import NoneStrings, NoneStringsAdd
from .strings.quotaStrings import QuotaStrings, QuotaStringsAdd
from .tldDb.tld_regexpr import ZZ
from .tldInfo import TldInfo
from .version import VERSION
from .whois_rdap import WhoisRdap
from .whoisCliInterface import WhoisCliInterface
from .whoisParser import WhoisParser

log = logging.getLogger(__name__)

HAS_REDIS = False
try:
    import redis  # noqa: F401

    HAS_REDIS = True
except ImportError as e:
    _ = e

WHOISDOMAIN: str = ""
if os.getenv("WHOISDOMAIN"):
    WHOISDOMAIN = str(os.getenv("WHOISDOMAIN"))

WD = WHOISDOMAIN.upper().split(":")

SIMPLISTIC = False
if "SIMPLISTIC" in WD:
    SIMPLISTIC = True

TLD_LIB_PRESENT: bool = False
try:
    import tld as lib_tld  # noqa: F401

    TLD_LIB_PRESENT = True
except ImportError as e:
    _ = e  # ignore any error


__all__ = [
    "VERSION",
    "ZZ",
    "DBMCache",
    "DummyCache",
    "FailedParsingWhoisOutputError",
    "NoneStrings",
    "NoneStringsAdd",
    "ParameterContext",
    "ProcFunc",
    "QuotaStrings",
    "QuotaStringsAdd",
    "RedisCache",
    "SimpleCacheBase",
    "SimpleCacheWithFile",
    "TldInfo",
    "UnknownDateFormatError",
    "UnknownTldError",
    "WhoisCommandFailedError",
    "WhoisCommandTimeoutError",
    "WhoisPrivateRegistryError",
    "WhoisQuotaExceededError",
    "WhoisRdap",
    "cleanupWhoisResponse",
    "filterTldToSupportedPattern",
    "getTestHint",
    "getVersion",
    "get_TLD_RE",
    "get_last_raw_whois_data",
    "mergeExternalDictWithRegex",
    "q2",
    "query",
    "setMyCache",
    "validTlds",
]

if HAS_REDIS:
    from .cache.redisCache import RedisCache

    __all__ += ["RedisCache"]


def _result2dict(
    func: Any,
) -> Any:
    @wraps(func)
    def _inner(*args: str, **kw: Any) -> dict[str, Any]:
        r = func(*args, **kw)
        return (r and vars(r)) or {}

    return _inner


def remoteQ2(
    conn: Any,
    max_requests: int,
    *,
    verbose: bool = False,
) -> None:
    n: int = 0
    while True:
        n += 1
        reply: dict[str, Any] = {}

        try:
            # unpicle the request
            request = conn.recv()
            if verbose:
                print("remoteQ2:Receive:", request, file=sys.stderr)

            pc: ParameterContext = ParameterContext()
            pc.from_json(request["pc"])

            # call the func
            allOk = True
            try:
                d = q2(domain=request["domain"], pc=pc)
                # pickle the result
                reply["result"] = d.__dict__
            except Exception as e:
                allOk = False

                # catch exceptions and picle them also
                reply["exception"] = e

            # pickle the status
            reply["status"] = allOk

            # add some remote info
            reply["remote"] = {
                "pid": os.getpid(),
                "count": n,
                "maxCount": max_requests,
            }

            if verbose:
                print("remoteQ2:Reply:", reply, file=sys.stderr)

            conn.send(reply)
        except EOFError as e:
            # if the caller is done so are we
            _ = e
            sys.exit(0)

        if n >= max_requests:
            break


def q2(
    domain: str,
    pc: ParameterContext,
) -> Domain | None:
    dc = DataContext(
        domain=domain,
        hasLibTld=TLD_LIB_PRESENT,
    )

    if pc.whoisOnly is False:
        wr = WhoisRdap()
        dd = wr.do_one_domain(domain)
        if dd.status:
            with_rdap_whois = True
            d: dict[str, Any] = wr.map_data_to_whoisdomain(dd.data, with_rdap_whois=with_rdap_whois)

            rr = Domain(pc=pc, dc=dc)
            rr.from_whodap_dict(d)
            msg = f"lookup: {domain} using whodap"
            log.info(msg)
            return rr  # also show the raw data from whodap

        log.warning(dd)  # no proper answer from rdap try whois
        if pc.rdapOnly is True:
            return None

    initLastWhois()

    dom = Domain(
        pc=pc,
        dc=dc,
    )

    parser = WhoisParser(
        pc=pc,
        dc=dc,
    )

    wci = WhoisCliInterface(
        pc=pc,
        dc=dc,
    )

    pwdr = ProcessWhoisDomainRequest(
        pc=pc,
        dc=dc,
        dom=dom,
        wci=wci,
        parser=parser,
    )

    return pwdr.processRequest()


def query(
    domain: str,
    *,
    pc: ParameterContext | None = None,
    verbose: bool = False,
    **kwargs: Any,
    # see documentation about parameters in context/parameterContext.py
    #    force: bool = False,
    #    cache_file: str | None = None,
    #    cache_age: int = 60 * 60 * 48,
    #    slow_down: int = 0,
    #    ignore_returncode: bool = False,
    #    server: str | None = None,
    #    verbose: bool = False,
    #    with_cleanup_results: bool = False,
    #    internationalized: bool = False,
    #    include_raw_whois_text: bool = False,
    #    return_raw_text_for_unsupported_tld: bool = False,
    #    timeout: float | None = None,
    #    parse_partial_response: bool = False,
    #    cmd: str = "whois",
    #    simplistic: bool = False,
    #    withRedacted: bool = False,
    #    tryInstallMissingWhoisOnWindows: bool = False,
    #    shortResponseLen: int = 5,
    #    withPublicSuffix: bool = False,
    #    extractServers: bool = False,
    #    stripHttpStatus: bool = False,
    #    noIgnoreWww: bool = False,
    #    rdapOnly: bool = false,
    #    whoisOnly: bool = false,
) -> Domain | None:
    assert isinstance(domain, str), Exception("`domain` - must be <str>")
    _ = verbose  # ha_ck
    if pc is None:
        pc = ParameterContext(**kwargs)

    msg = f"{pc}"
    log.debug(msg)

    return q2(domain=domain, pc=pc)


# Add get function to support return result in dictionary form
get = _result2dict(query)

# CLAUDE: logging changes
# Calling logging.basicConfig(level="DEBUG") inside library code mutates the application's root logger
# and is widely considered bad library citizenship.
# If the caller's app uses logging, you've just overridden their config.
# Use a per-package logger and let the caller configure the level:
#  logging.getLogger("whoisdomain").setLevel("DEBUG"),
#  or document a setup_logging(verbose=) helper that callers can opt into.

#  CLAUDE: memoryleak:
# Three calls — gc.collect(0); gc.collect(1); gc.collect(2) — once on entry and once on exit.
# gc.collect(2) already does generations 0 and 1, so the other two are redundant.
# More importantly, manual GC in library code imposes work on callers who don't need it
# (Python's GC is generational and usually correct without help).
# The del spam right above isn't doing anything either
# — locals are about to go out of scope.
# If you're chasing a real leak, profile it with tracemalloc;
# otherwise this is cargo-culted overhead.
