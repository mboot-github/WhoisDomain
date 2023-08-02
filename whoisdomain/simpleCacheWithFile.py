#! /usr/bin/env python3

import sys
import os
import json


from typing import (
    Optional,
    Tuple,
)

from .simpleCacheBase import (
    SimpleCacheBase,
)


class SimpleCacheWithFile(SimpleCacheBase):
    cacheFilePath: Optional[str] = None

    def __init__(
        self,
        verbose: bool = False,
        cacheFilePath: Optional[str] = None,
        cacheMaxAge: int = (60 * 60 * 48),
    ) -> None:
        super().__init__(verbose=verbose, cacheMaxAge=cacheMaxAge)
        self.cacheFilePath = cacheFilePath

    def _cacheFileLoad(
        self,
    ) -> None:
        if self.cacheFilePath is None:
            return

        if not os.path.isfile(self.cacheFilePath):
            return

        if self.verbose:
            print(f"cacheFileLoad: {self.cacheFilePath}", file=sys.stderr)

        with open(self.cacheFilePath, "r") as f:
            try:
                self.memCache = json.load(f)
            except Exception as e:
                print(f"ignore json load err: {e}", file=sys.stderr)

    def _cacheFileSave(
        self,
    ) -> None:
        if self.cacheFilePath is None:
            return

        if self.verbose:
            print(f"_cacheFileSave: {self.cacheFilePath}", file=sys.stderr)

        with open(self.cacheFilePath, "w") as f:
            json.dump(self.memCache, f)

    def cachePut(
        self,
        keyString: str,
        data: str,
    ) -> None:
        super().cachePut(keyString=keyString, data=data)
        self._cacheFileSave()

    def cacheGet(
        self,
        keyString: str,
    ) -> Optional[Tuple[float, str]]:
        self._cacheFileLoad()
        return super().cacheGet(keyString=keyString)

    def cacheExpired(
        self,
        keyString: str,
    ) -> Optional[bool]:
        if keyString not in self.memCache:
            self.cacheGet(keyString=keyString)

        return super().cacheExpired(keyString=keyString)

    def cacheGetData(
        self,
        keyString: str,
    ) -> Optional[str]:
        if self.verbose:
            print(f"cacheGetData: {keyString}", file=sys.stderr)

        tData: Optional[Tuple[float, str]] = self.cacheGet(keyString)
        if tData is None:
            return None

        return tData[1]


if __name__ == "__main__":
    pass
