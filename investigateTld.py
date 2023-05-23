#! /usr/bin/env python3

# should run after a valida database is created with analizeIanaTld.py

from typing import (
    Optional,
    List,
    Dict,
    Any,
    Tuple,
)

import sys
import io
import re
import time
import json
import sqlite3

from whoisdomain import tld_regexpr


class IanaDatabase:
    verbose: bool = False
    conn: Any = None

    def __init__(
        self,
        verbose: bool = False,
    ):
        self.verbose = verbose

    def connectDb(
        self,
        fileName: str,
    ) -> None:
        self.conn: Any = sqlite3.connect(fileName)
        self.testValidConnection()

    def testValidConnection(self) -> None:
        if self.conn is None:
            raise Exception("No valid connection to the database exist")

    def selectSql(
        self,
        sql: str,
        data: Any = None,
    ) -> Tuple[Any, Any]:
        self.testValidConnection()
        cur: Any = self.conn.cursor()

        try:
            if data:
                result = cur.execute(sql, data)
            else:
                result = cur.execute(sql)

        except Exception as e:
            print(sql, data, e, file=sys.stderr)
            exit(101)
        return result, cur

    def doSql(
        self,
        sql: str,
        data: Any = None,
        withCommit: bool = True,
    ) -> Any:
        self.testValidConnection()
        cur = self.conn.cursor()

        try:
            if data:
                result = cur.execute(sql, data)
            else:
                result = cur.execute(sql)

            if withCommit:
                self.conn.commit()

        except Exception as e:
            print(sql, data, e, file=sys.stderr)
            exit(101)
        return result


def extractServers(aDict: Dict[str, Any]) -> Dict[str, Any]:
    servers: Dict[str, Any] = {}
    k = "_server"
    for key in aDict.keys():
        if k in aDict[key]:
            server = aDict[key][k]
            if server not in servers:
                servers[server] = []
            servers[server].append(key)
    return servers


def xMain() -> None:
    verbose = False
    dbFileName = "IanaDb.sqlite"

    iad = IanaDatabase(verbose=verbose)
    iad.connectDb(dbFileName)
    ss = extractServers(tld_regexpr.ZZ)

    # investigate all known iana tld and see if we have them

    sql = """
SELECT
    Link,
    Domain,
    Type,
    TLD_Manager,
    Whois,
    `DnsResolve-A`,
    RegistrationUrl
FROM
    IANA_TLD
"""

    rr, cur = iad.selectSql(sql)
    for row in cur:
        tld = row[0].replace("'", "")
        manager = row[3]
        w = row[4]
        resolve = row[5]
        reg = row[6]

        if tld in tld_regexpr.ZZ:
            continue

        if manager == "NULL":
            print(f'ZZ["{tld}"] = ' + '{"_privateRegistry": True}')
            continue

        mm = {
            "com": [
                "whois.afilias-srs.net",
                "whois2.afilias-grs.net",
                "whois.nic.google",
                "whois.nic.gmo",
                "whois.gtld.knet.cn",
                "whois.registry.in",
                "whois.ngtld.cn",
            ],
            "sg": [
                "whois.sgnic.sg",
            ],
            "_teleinfo": [
                "whois.teleinfo.cn",
            ],
            "tw": [
                "whois.twnic.net.tw",
            ],
            "_centralnic": [
                "whois.centralnic.com",
            ],
        }

        found = False
        for key, value in mm.items():
            for n in value:
                if n in resolve:
                    print(f'ZZ["{tld}"] = ' + '{"_server": "' + n + '", "extend": "' + key + '"}')
                    found = True

                if found:
                    break
            if found:
                break

        if found:
            continue

        if reg == "NULL" and w == "NULL":
            continue  # unclear, we have existing ns records indicating some tld's actually exist but have no whois, lets skip for now
            print(f'ZZ["{tld}"] = ' + '{"_privateRegistry": True}')

        if w == "NULL":
            continue

        w = w.replace("'", "")
        if w in ss:
            print(f'ZZ["{tld}"] = ' + '{"_server": "' + w + '", "extend": "' + ss[w][0] + '"}')
            print("# ", w, ss[w])
            continue

        print("# MISSING", tld, manager.replace("\n", ";"), w, resolve, reg)


xMain()
