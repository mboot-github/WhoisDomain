#! /usr/bin/env python3

import time
import sys

# import os
# import json


from typing import (
    Dict,
    Optional,
    Tuple,
    # TypeVar,
)


class SimpleCacheBase:
    verbose: bool = False
    memCache: Dict[str, Tuple[float, str]] = {}
    cacheMaxAge: int = 60 * 60 * 48

    def __init__(
        self,
        verbose: bool = False,
        cacheMaxAge: int = (60 * 60 * 48),
    ) -> None:
        self.verbose = verbose
        self.memCache = {}
        self.cacheMaxAge = cacheMaxAge

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

    def cacheExpired(self, keyString: str) -> Optional[bool]:
        if self.verbose:
            print(f"cacheExpired: {keyString}", file=sys.stderr)

        cData = self.memCache.get(keyString)
        if cData is None:
            return None

        hasExpired = cData[0] < (time.time() - self.cacheMaxAge)
        return hasExpired


# CacheBased = TypeVar("CacheBased", bound=CacheBase)


if __name__ == "__main__":
    pass
