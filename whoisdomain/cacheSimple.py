#! /usr/bin/env python3

import time
import sys
import os
import json


from typing import (
    Dict,
    Optional,
    Tuple,
)


class CacheBase:
    verbose: bool = False
    memCache: Dict[str, Tuple[float, str]] = {}
    CACHE_MAX_AGE: int = 60 * 60 * 48  # 48h

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self.memCache = {}

    def cachePut(self, keyString: str, data: str) -> None:
        if self.verbose:
            print(f"cachePut: {keyString}", file=sys.stderr)

        # store the currentTime and data tuple (time, data)
        self.memCache[keyString] = (
            int(time.time()),
            data,
        )

    def cacheGet(self, keyString: str) -> Optional[Tuple[float, str]]:
        if self.verbose:
            print(f"cacheGet: {keyString}", file=sys.stderr)

        return self.memCache.get(keyString)


class CacheSimpleWithFile(CacheBase):
    def __init__(self, verbose: bool = False) -> None:
        super().__init__(verbose=verbose)

    def cacheFileLoad(self, cacheFilePath: str) -> None:
        if self.verbose:
            print(f"cacheFileLoad: {cacheFilePath}", file=sys.stderr)

        if not os.path.isfile(cacheFilePath):
            return

        with open(cacheFilePath, "r") as f:
            try:
                self.memCache = json.load(f)
            except Exception as e:
                print(f"ignore json load err: {e}", file=sys.stderr)

    def cacheFileSave(self, cacheFilePath: str) -> None:
        if self.verbose:
            print(f"cacheFileSave: {cacheFilePath}", file=sys.stderr)

        with open(cacheFilePath, "w") as f:
            json.dump(self.memCache, f)


if __name__ == "__main__":
    pass
