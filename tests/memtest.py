#! /usr/bin/env python3

from typing import (
    Optional,
    List,
)
import sys
import gc
import re

re._MAXCACHE = 1

from memory_profiler import profile
from collections import defaultdict

sys.path.append("..")
import whoisdomain

domains = [
    "google.com",
    "microsoft.com",
    "apple.com",
    "dell.com",
    "hp.com",
    "ab.com",
    "xy.com",
    "tld.com",
    "samsung.com",
    "ibm.com",
    "lg.com",
    "python.com",
    "git.com",
    "netflix.com",
    "cisco.com",
    "kfc.com",
    "nasa.com",
    "esa.com",
    "amazon.com",
    "meta.com",
    "godaddy.com",
    "ovh.com",
    "uber.com",
    "siemens.com",
]


def getAllCurrentTld() -> List[str]:
    return whoisdomain.validTlds()


def appendHint(
    rr: List[str],
    allRegex: Optional[str],
    tld: str,
) -> None:
    hint = whoisdomain.getTestHint(tld)
    if hint:
        rr.append(f"{hint}")


def makeTestAllCurrentTld(
    allRegex: Optional[str] = None,
) -> List[str]:
    rr: List[str] = []
    for tld in getAllCurrentTld():
        if allRegex is None:
            appendHint(rr, allRegex, tld)
            continue
        if re.search(allRegex, tld):
            appendHint(rr, allRegex, tld)

    return rr


def check() -> None:
    # gc.set_debug(gc.DEBUG_LEAK)
    gc.set_debug(gc.DEBUG_UNCOLLECTABLE)
    domains = makeTestAllCurrentTld(None)
    n: int = 0

    before = defaultdict(int)
    for i in gc.get_objects():
        before[type(i)] += 1

    for item in domains:
        n += 1
        print(f"Checking domain: {item}")
        b2 = defaultdict(int)
        for i in gc.get_objects():
            # print(i, type(i))
            b2[type(i)] += 1

        whoisdomain_call(item)
        re._cache.clear()
        print(gc.collect(0))  # The number of unreachable objects found is returned.
        print(gc.collect(1))  # The number of unreachable objects found is returned.
        print(gc.collect(2))  # The number of unreachable objects found is returned.

        after = defaultdict(int)

        z = []
        for i in gc.get_objects():
            if str(type(i)) == "<class 're.Pattern'>":
                if str(i) in z:
                    print(f"DUPLICATE: {i}")
                else:
                    z.append(str(i))
            after[type(i)] += 1

        n = 0
        for i in sorted(z):
            n += 1
            print(n, i)

        z = [(k, after[k] - before[k]) for k in after if (after[k] - before[k]) > 0]
        for item in z:
            print("since start", item)  # (<class 're.Pattern'>, 46) is growing to 288

        z = [(k, after[k] - b2[k]) for k in after if (after[k] - b2[k]) > 0]
        for item in z:
            print("since previous", item)  # (<class 're.Pattern'>, 46) is growing to 288

        n = 0
        for item in gc.get_stats():
            print(n, item)
            n += 1

        print(gc.get_referrers())

        for item in gc.garbage:
            print("garbage:", item)


@profile
def whoisdomain_call(domain: str) -> None:
    try:
        d = whoisdomain.query(domain)
        del d
    except whoisdomain.WhoisPrivateRegistry:
        return
    except whoisdomain.WhoisCommandFailed:
        return
    except whoisdomain.WhoisQuotaExceeded:
        return
    except whoisdomain.FailedParsingWhoisOutput:
        return
    except whoisdomain.UnknownTld:
        return
    except whoisdomain.UnknownDateFormat:
        return
    except whoisdomain.WhoisCommandTimeout:
        return


check()
