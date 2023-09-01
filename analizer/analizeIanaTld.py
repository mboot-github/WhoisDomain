#! /usr/bin/env python3

"""
Analyze all tld's currently in the iana root db
"""

# from typing import (    Any)

import io
import re
from dns.resolver import (
    Resolver,
    LRUCache,
)

# import json

from ianaCrawler import IanaCrawler
from pslGrabber import PslGrabber
from ianaDatabase import IanaDatabase


def prepDb(
    dbFileName: str,
    verbose: bool = False,
) -> IanaDatabase:
    iad: IanaDatabase = IanaDatabase(verbose=verbose)
    iad.connectDb(dbFileName)
    iad.createTableTld()
    iad.createTablePsl()
    return iad


def prepResolver() -> Resolver:
    resolver: Resolver = Resolver()
    resolver.cache = LRUCache()  # type: ignore


def updateAllIanaTldData(
    resolver: Resolver,
    verbose: bool = False,
) -> IanaCrawler:
    iac = IanaCrawler(verbose=verbose, resolver=resolver)
    iac.getTldInfoAllFromIanaUrl()
    iac.addInfoToAllTld()
    return iac


def doOnePslEntry(
    iad: IanaDatabase,
    z: str,
    section: str,
    pg: PslGrabber,
    verbose: bool = False,
) -> None:
    n = 0
    z = z.split()[0]
    if "." in z:
        tld = z.split(".")[-1]
        n = len(z.split("."))
    else:
        tld = z

    sql, data = iad.makeInsOrUpdSqlPsl(
        pg.ColumnsPsl(),
        [
            tld,
            z,
            n,
            section,
            None,
        ],
    )
    iad.doSql(sql, data)


def getAllPslDataAndProcess(iad: IanaDatabase, verbose: bool = False) -> None:
    pg: PslGrabber = PslGrabber()
    response = pg.getData(pg.getUrl())
    text = response.text
    buf = io.StringIO(text)

    section = ""
    while True:
        line = buf.readline()
        if not line:
            return

        z = line.strip()
        if len(z) == 0:
            continue

        if "// ===END " in z:
            section = ""

        if "// ===BEGIN ICANN" in z:
            section = "ICANN"
            continue

        if "// ===BEGIN PRIVATE" in z:
            section = "PRIVATE"
            continue

        if section == "PRIVATE":
            continue

        if re.match(r"^\s*//", z):
            # comment line
            continue

        doOnePslEntry(
            iad,
            z,
            section,
            pg,
            verbose,
        )


def xMain() -> None:
    verbose: bool = True
    dbFileName: str = "IanaDb.sqlite"

    resolver: Resolver = prepResolver()
    iac = updateAllIanaTldData(resolver, verbose)

    iad = prepDb(dbFileName, verbose)

    # process deleted tld's (not currently active)
    xx = iac.getDeleted()
    for tld in xx:
        sql = iad.makeDelSqlTld(tld)
        iad.doSql(sql)
        sql = iad.makeDelSqlPsl(tld)
        iad.doSql(sql)

    # process all known tld's
    xx = iac.getResults()
    for item in xx["data"]:
        sql, data = iad.makeInsOrUpdSqlTld(xx["header"], item)
        iad.doSql(sql, data)

    getAllPslDataAndProcess(
        iad,
        verbose,
    )


xMain()
