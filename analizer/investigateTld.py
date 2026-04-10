#! /usr/bin/env python3

# should run after a valid database is created with analizeIanaTld.py

import sys
from typing import (
    Any,
)

import idna as idna2

from ianaDatabase import IanaDatabase
from oneTld import OneTld

# the next 2 belong together
sys.path.append("..")
from whoisdomain.tldDb import tld_regexpr


def extract_server_hints(aDict: dict[str, Any]) -> dict[str, Any]:
    # key will be the whois server, data will be the list of tld's using this server
    servers: dict[str, Any] = {}
    k = "_server"
    for key, value in aDict.items():
        if k in value:
            server = value[k]
            if server not in servers:
                servers[server] = []
            servers[server].append(key)
    # print(servers)
    return servers


def look_for_missing_in_iana_web(allTld: list[str], tld: str):
    if "." in tld:  # not a real tld a pseudo tld
        return

    if tld.startswith("_"):  # magic collector tld
        return

    try:
        tld2 = idna2.encode(tld).decode() or tld
    except Exception as e:
        print(f"{tld} {e} ", file=sys.stderr)
        tld2 = tld

    if tld not in allTld and tld2 not in allTld:
        print(f"# currently defined in ZZ but missing in iana: {tld}, {tld2}")


def xMain() -> None:
    verbose = True
    dbFileName = "IanaDb.sqlite"
    allTld: list[str] = []

    # print(tld_regexpr.ZZ)
    # sys.exit(0)
    server_hints = extract_server_hints(tld_regexpr.ZZ)

    iad = IanaDatabase(verbose=verbose)
    iad.connectDb(dbFileName)
    _, cur = iad.getAllDataTld()

    forest: dict[str, Any] = {}
    for row in cur:
        ot = OneTld(tld_regexpr.ZZ, verbose=verbose)
        ot.processRow(row, allTld, server_hints)
        tld = ot.tld
        forest[tld] = ot

    for tld, data in forest.items():
        if data.rdap_info != "NULL":
            print(tld, data.rdap_info)

    allTld = sorted(allTld)
    for tld in tld_regexpr.ZZ:
        look_for_missing_in_iana_web(allTld, tld)


xMain()
