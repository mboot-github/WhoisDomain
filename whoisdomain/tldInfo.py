# import re

from typing import (
    Dict,
    List,
    Any,
    Optional,
)


class TldInfo:
    def __init__(
        self,
        zzDict: Dict[str, Any],
        verbose: bool = False,
    ) -> None:
        self.verbose = verbose
        self.tldRegexDb: Dict[str, Dict[str, Any]] = {}
        # self.regexDbByKey: Dict[str, Any] = {}
        self.zzDictRef = zzDict

    #     def _oneTldOneKey(self, name: str, key: str, reg: Optional[str]) -> None:
    #         if reg is None:
    #             return
    #
    #         if key is None:
    #             return
    #
    #         if key.startswith("_"):  # skip meta keys, they are not regexes
    #             return
    #
    #         if key in ["extend"]:  # this actually should have been a meta key: "_extend"
    #             return
    #
    #         if reg in self.regexDbByKey:
    #             return
    #
    #         self.regexDbByKey[reg] = None
    #         if isinstance(reg, str):
    #             self.regexDbByKey[reg] = re.compile(reg, flags=re.IGNORECASE)

    def _get_tld_re(
        self,
        tldString: str,
        override: bool = False,
    ) -> Dict[str, Any]:
        if override is False:
            if tldString in self.tldRegexDb:
                return self.tldRegexDb[tldString]

        tldDict = self.zzDictRef[tldString]

        # do we need to propagate "extend"
        hasExtend = tldDict.get("extend")
        if hasExtend:
            e = self._get_tld_re(hasExtend)  # call recursive
            tmp = e.copy()
            # and merge results in tmp with caller data in tldDict
            # The update() method updates the dictionary with the elements
            # from another dictionary object or from an iterable of key/value pairs.
            tmp.update(tldDict)
        else:
            tmp = tldDict

        # finally we dont want to propagate the extend data
        # as it is only used to recursivly populate the dataset
        if "extend" in tmp:
            del tmp["extend"]

        # we want now to exclude andy key starting with _ like _server,_test, ...
        # dont recompile each re by themselves, reuse existing compiled re

        tld_re: Dict[str, Any] = {}
        for key, val in tmp.items():
            # keys starting with _ we just copy,
            # this means we inhert [ '_server', '_test',  '_privateREgistry' ]
            tld_re[key] = val

        # meta domains start with _: examples _centralnic and _donuts
        if tldString[0] != "_":
            self.tldRegexDb[tldString] = tld_re

        return tld_re

    def _initOne(
        self,
        tld: str,
        override: bool = False,
    ) -> None:
        if tld[0] == "_":  # skip meta domain patterns , these are not domains just handles we reuse
            return

        what = self._get_tld_re(tld, override)

        # test if the string is identical after idna conversion
        d = tld.split(".")
        j = [k.encode("idna").decode() or k for k in d]

        tld2 = ".".join(j)
        if tld == tld2:
            return

        self.tldRegexDb[tld2] = what

    # public

    def init(self) -> None:
        # build the database of all tld
        for tld in self.zzDictRef.keys():
            self._initOne(tld, override=False)

    def filterTldToSupportedPattern(
        self,
        domain: str,
        dList: List[str],
        verbose: bool = False,
    ) -> Optional[str]:
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
        aDict: Dict[str, Any] = {},
    ) -> None:
        # merge in ZZ, this extends ZZ with new tld's and overrides existing tld's
        for tld in aDict.keys():
            self.zzDictRef[tld] = aDict[tld]

        # reprocess the regexes we newly defined or overrode
        override = True
        for tld in aDict.keys():
            self._initOne(tld, override)

    def validTlds(self) -> List[str]:
        return sorted(self.tldRegexDb.keys())

    def TLD_RE(self) -> Dict[str, Dict[str, Any]]:
        # this returns the currenly prepared list of all tlds ane theyr compiled regexes
        return self.tldRegexDb
