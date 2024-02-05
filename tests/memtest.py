#! /usr/bin/env python3

from typing import (
    Optional,
    List,
)
import sys
import gc
import re

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
    # domains = makeTestAllCurrentTld(None)
    n: int = 0

    before = defaultdict(int)
    for i in gc.get_objects():
        before[type(i)] += 1

    for item in domains:
        n += 1
        print(f"Checking domain: {item}")

        whoisdomain_call(item)
        after = defaultdict(int)
        for i in gc.get_objects():
            after[type(i)] += 1

        z = [(k, after[k] - before[k]) for k in after if after[k] - before[k]]
        for item in z:
            print(item)

        print(gc.collect())
        print(gc.get_stats())
        print(gc.get_referrers())
        # print(gc.garbage)
        if n > 3:
            break

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
