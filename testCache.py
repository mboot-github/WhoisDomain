#! /usr/bin/env python3

import sys

import whoisdomain


print("TEST: manually setup a cache", file=sys.stderr)
verbose: bool = True

# start a parameter context
pc = whoisdomain.ParameterContext(
    verbose=verbose,
)
whoisdomain.setMyCache(
    whoisdomain.DummyCache(
        verbose=verbose,
    ),
)
whoisdomain.setMyCache(
    whoisdomain.DBMCache(
        dbmFile="testfile.dbm",
        verbose=verbose,
    ),
)

# do a lookup
d = whoisdomain.q2(
    "google.com",
    pc,
)

# print results
print(d.__dict__)
