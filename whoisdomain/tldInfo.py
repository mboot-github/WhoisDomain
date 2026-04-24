# import re
import logging
from typing import (
    Any,
)

log = logging.getLogger(__name__)


class TldInfo:
    def __init__(
        self,
        zzDict: dict[str, Any],
        *,
        verbose: bool = False,
    ) -> None:
        self.verbose = verbose
        if verbose:
            logging.basicConfig(level="DEBUG")

        # a reference to the external ZZ database of all TLD info
        self.zzDictRef = zzDict

        # do we want to store the processed data or will be do all on the fly
        self.withStore: bool = True

        # the database of processed tld entries (if withStoe is True)
        self.tldRegexDb: dict[str, dict[str, Any]] = {}

    def _initOne(
        self,
        tld: str,
        *,
        override: bool = False,
    ) -> None:
        # meta domains start with _: examples _centralnic and _donuts
        if tld[0] == "_":  # skip meta domain patterns , these are not domains just handles we reuse
            return

        if not override and tld in self.tldRegexDb:
            return

        what = self.flattenMasterTldEntry(tld)
        if self.withStore:
            self.tldRegexDb[tld] = what

        # test if the string is identical after idna conversion
        d = tld.split(".")
        j = [k.encode("idna").decode() or k for k in d]

        tld2 = ".".join(j)
        if tld == tld2:
            return

        if self.withStore:
            self.tldRegexDb[tld2] = what

    @classmethod
    def _cleanupResultDict(
        cls,
        resultDict: dict[str, Any],
    ) -> dict[str, Any]:
        # we dont want to propagate the extend data
        resultDict.pop("extend", None)
        resultDict.pop("_extend", None)

        # we inhert all except extend or _extend
        cleanResultDict: dict[str, Any] = {}
        for key, val in resultDict.items():
            cleanResultDict[key] = val  # noqa: PERF403

        return cleanResultDict

    # public

    def flattenMasterTldEntry(
        self,
        tldString: str,
    ) -> dict[str, Any]:
        tldDict = self.zzDictRef[tldString]
        hasExtend: str | None = tldDict.get("extend") or tldDict.get("_extend")
        if hasExtend:
            eDict = self.flattenMasterTldEntry(hasExtend)  # call recursive
            tmpDict = eDict.copy()
            # entries in the current tldDict take precedence
            # over the origin data of the extend entry
            tmpDict.update(tldDict)
            return self._cleanupResultDict(tmpDict)

        return self._cleanupResultDict(tldDict)

    def init(
        self,
    ) -> None:
        # build the database of all tld
        for tld in self.zzDictRef:
            self._initOne(tld, override=False)

    def filterTldToSupportedPattern(
        self,
        dList: list[str],
    ) -> str | None:
        # we have max 2 levels so first check if the last 2 are in our list
        tld = f"{dList[-2]}.{dList[-1]}"
        if tld in self.zzDictRef:
            return tld

        # if not check if the last item  we have
        tld = f"{dList[-1]}"
        if tld in self.zzDictRef:
            return tld

        return None

    def mergeExternalDictWithRegex(
        self,
        aDict: dict[str, Any] | None = None,
    ) -> None:
        if aDict is None:
            return

        if len(aDict) == 0:
            return

        # merge in ZZ, this extends ZZ with new tld's and overrides existing tld's
        for tld in aDict:
            self.zzDictRef[tld] = aDict[tld]

        # reprocess the regexes we newly defined or overrode
        override = True
        for tld in aDict:
            self._initOne(tld, override=override)

    def validTlds(
        self,
    ) -> list[str]:
        return sorted(self.tldRegexDb.keys())

    def TLD_RE(
        self,
    ) -> dict[str, dict[str, Any]]:
        # this returns the currenly prepared list of all tlds and the compiled regexes
        return self.tldRegexDb
