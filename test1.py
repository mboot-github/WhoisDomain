#! /usr/bin/env python3

import whoisdomain

print("TEST1: query")
d = whoisdomain.query("google.com")
print(d.__dict__)

print("TEST1: q2")
pc = whoisdomain.ParameterContext()
d = whoisdomain.q2("google.com", pc)
print(d.__dict__)

print("TEST1: manually setup a cache")
whoisdomain.CACHE_STUB = None
pc = whoisdomain.ParameterContext(verbose=True)
whoisdomain.CACHE_STUB = whoisdomain.SimpleCacheBase(verbose=True)
d = whoisdomain.q2("google.com", pc)
print(d.__dict__)
