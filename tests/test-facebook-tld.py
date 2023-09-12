#! /usr/bin/env python3

import sys
import requests

sys.path.append("..")
import whoisdomain

from typing import (
    List,
    Dict,
    Optional,
    cast,
)


def getDomains(
    url: str,
    verbose: bool = False,
) -> List[str]:
    return [
        "facebook.cn",
        "facebook.com",
        "facebook.fr",
        "facebook.de",
        "facebook.co.uk",
        "facebook.net",
        "facebook.gr",
        "facebook.nl",
        "facebook.se",
        "facebook.fi",
        "facebook.ae",
        "facebook.cm",
        "facebook.co",
        "facebook.it",
        "facebook.es",
        "facebook.za",
        "facebook.ca",
        "facebook.pl",
        "facebook.su",
        "facebook.ru",
        "facebook.tw",
        "facebook.jp",
        "facebook.au",
        "facebook.nz",
        "facebook.ar",
        "facebook.mx",
        "facebook.is",
        "facebook.io",
    ]


def getOneRegistrant(
    domain: str,
    registrants: Dict[str | None, List[str]],
    verbose: bool = False,
) -> None:
    try:
        print(f"\n### ===: try: {domain}")
        w = whoisdomain.query(domain)
    except Exception as e:
        print(domain, e, file=sys.stderr)
        print(whoisdomain.get_last_raw_whois_data())
        return

    if w is None:
        print(whoisdomain.get_last_raw_whois_data())
        print(w)
        return

    k = "registrant"
    w2 = w.__dict__
    if k not in w2:
        print(f"no {k} for {domain}")
        print(whoisdomain.get_last_raw_whois_data())
        return

    z = w2[k]
    print(f"Registrant: {z}")

    if z not in registrants:
        registrants[z] = [domain]
    else:
        registrants[z].append(domain)


def xMain() -> None:
    verbose: bool = True
    url: str = "https://www.google.com/supported_domains"

    domains: List[str] = getDomains(url, verbose)
    registrants: Dict[str | None, List[str]] = {}

    for domain in domains:
        getOneRegistrant(domain, registrants, verbose)

    ll = cast(List[str], registrants.keys())
    for k in sorted(ll):
        print(k, registrants[k])


xMain()
