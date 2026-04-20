import logging
import os
from typing import (
    Any,
)

from .context.parameterContext import ParameterContext
from .exceptions import WhoisQuotaExceeded
from .tldDb.tld_regexpr import ZZ
from .tldInfo import TldInfo
from .version import VERSION

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def filterTldToSupportedPattern(
    domain: str,
    dList: list[str],
    *,
    verbose: bool = False,
) -> str | None:
    global tldInfo
    return tldInfo.filterTldToSupportedPattern(domain, dList, verbose=verbose)


def mergeExternalDictWithRegex(
    aDict: dict[str, Any] | None = None,
) -> None:
    global tldInfo
    if aDict is None:
        return
    if len(aDict) == 0:
        return

    tldInfo.mergeExternalDictWithRegex(aDict)


def validTlds() -> list[str]:
    global tldInfo
    return tldInfo.validTlds()


def get_TLD_RE() -> dict[str, dict[str, Any]]:
    global tldInfo
    return tldInfo.TLD_RE()


def getVersion() -> str:
    return VERSION


def getTestHint(tldString: str) -> str | None:
    k: str = "_test"
    if tldString in ZZ and k in ZZ[tldString] and ZZ[tldString][k]:
        return str(ZZ[tldString][k])

    return None


def cleanupWhoisResponse(
    whoisStr: str,
    *,
    verbose: bool = False,
    with_cleanup_results: bool = False,
    withRedacted: bool = False,
    pc: ParameterContext | None = None,
) -> str:
    tmp2: list[str] = []

    if pc is None:
        pc = ParameterContext(
            verbose=verbose,
            withRedacted=withRedacted,
            with_cleanup_results=with_cleanup_results,
        )

    tmp: list[str] = whoisStr.split("\n")
    for line in tmp:
        # some servers respond with: % Quota exceeded in the comment section (lines starting with %)
        if "quota exceeded" in line.lower():
            raise WhoisQuotaExceeded(whoisStr)

        if pc.with_cleanup_results is True and line.startswith("%"):  # only remove if requested
            continue

        if pc.withRedacted is False and "REDACTED FOR PRIVACY" in line:  # these lines contibute nothing so ignore
            continue

        if "Please query the RDDS service of the Registrar of Record" in line:  # these lines contibute nothing so ignore
            continue

        if line.startswith("Terms of Use:"):  # these lines contibute nothing so ignore
            continue

        tmp2.append(line.strip("\r").rstrip())

    return "\n".join(tmp2)


VERBOSE: bool = False

# Here we focre load on import the processing of the ZZ database
tldInfo = TldInfo(ZZ, verbose=VERBOSE)
tldInfo.init()  # must run on import
