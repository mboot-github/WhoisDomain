#! /usr/bin/env python3

import sys

import whoisdomain

from typing import (
    Optional,
)


class DummyCache:
    def __init__(
        self,
        verbose: bool = False,
    ) -> None:
        self.verbose = verbose
        if self.verbose:
            print(f"DummyCache verbose: {self.verbose}", file=sys.stderr)

    def get(
        self,
        keyString: str,
    ) -> Optional[str]:
        if self.verbose:
            print(f"DummyCache get: {keyString}", file=sys.stderr)
        return None

    def put(
        self,
        keyString: str,
        data: str,
    ) -> str:
        if self.verbose:
            print(f"DummyCache put: {keyString}", file=sys.stderr)
        return data


print("TEST: manually setup a cache", file=sys.stderr)
verbose: bool = True

# start a parameter context
pc = whoisdomain.ParameterContext(verbose=verbose)
whoisdomain.setMyCache(DummyCache(verbose=verbose))

# do a lookup
d = whoisdomain.q2("google.com", pc)

# print results
print(d.__dict__)
