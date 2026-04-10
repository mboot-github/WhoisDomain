#! /usr/bin/env python3
import json
import sqlite3
import sys
from typing import (
    # Dict,
    Any,
)


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
        self.conn = sqlite3.connect(fileName)
        self.testValidConnection()

    def testValidConnection(self) -> None:
        if self.conn is None:
            msg = "No valid connection to the database exist"
            raise Exception(msg)

    def selectSql(
        self,
        sql: str,
        data: Any = None,
    ) -> tuple[Any, Any]:
        self.testValidConnection()
        cur: Any = self.conn.cursor()

        try:
            result = cur.execute(sql, data) if data else cur.execute(sql)

        except Exception as e:
            print(sql, data, e, file=sys.stderr)
            sys.exit(101)
        return result, cur

    def doSql(
        self,
        sql: str,
        data: Any = None,
        withCommit: bool = True,
    ) -> Any:
        self.testValidConnection()
        cur: Any = self.conn.cursor()

        try:
            result = cur.execute(sql, data) if data else cur.execute(sql)

            if withCommit:
                self.conn.commit()

        except Exception as e:
            print(sql, e, file=sys.stderr)
            sys.exit(101)
        return result

    def createTableTld(self) -> None:
        sql = """
CREATE TABLE IF NOT EXISTS IANA_TLD (
    Link            TEXT PRIMARY KEY,
    Domain          TEXT NOT NULL UNIQUE,
    Type            TEXT NOT NULL,
    TLD_Manager     TEXT,
    Whois           TEXT,
    RegistrationUrl TEXT,
    Rdap            TEXT,
    'DnsResolve-A'  TEXT
);
"""
        return self.doSql(sql)

    def createTablePsl(self) -> None:
        sql = """
CREATE TABLE IF NOT EXISTS IANA_PSL (
    Tld             TEXT NOT NULL,
    Psl             TEXT UNIQUE,
    Level           INTEGER NOT NULL,
    Type            TEXT NOT NULL,
    Comment         TEXT,
    PRIMARY KEY (Tld, Psl)
);
"""
        return self.doSql(sql)

    def prepData(
        self,
        columns: list[str],
        values: list[str],
    ) -> tuple[str, str, list[Any]]:
        cc = "`" + "`,`".join(columns) + "`"

        data = []
        vvv = []
        i = 0
        while i < len(values):
            v = "NULL"
            if values[i] is not None:
                v = values[i]
                if not isinstance(v, str) and not isinstance(v, int):
                    v = json.dumps(v, ensure_ascii=False)
                if isinstance(v, str):
                    v = "'" + v + "'"
                if isinstance(v, int):
                    v = int(v)
            data.append(v)
            vvv.append("?")
            i += 1

        vv = ",".join(vvv)
        return cc, vv, data

    def makeInsOrUpdSqlTld(
        self,
        columns: list[str],
        values: list[str],
    ) -> tuple[str, list[Any]]:
        cc, vv, data = self.prepData(columns, values)
        return (
            f"""
INSERT OR REPLACE INTO IANA_TLD (
    {cc}
) VALUES(
    {vv}
);
""",
            data,
        )

    def makeDelSqlTld(
        self,
        tld: str,
    ) -> tuple[str, list[Any]]:
        return f"DELETE FROM IANA_TLD WHERE Link = '{tld}';"

    def makeInsOrUpdSqlPsl(
        self,
        columns: list[str],
        values: list[str],
    ) -> tuple[str, list[Any]]:
        cc, vv, data = self.prepData(columns, values)

        return (
            f"""
INSERT OR REPLACE INTO IANA_PSL (
    {cc}
) VALUES(
    {vv}
);
""",
            data,
        )

    def makeDelSqlPsl(
        self,
        tld: str,
    ) -> tuple[str, list[Any]]:
        return f"DELETE FROM IANA_PSL WHERE Tld = '{tld}';"

    def getAllDataTld(self) -> tuple[Any, Any]:
        sql = """
SELECT
    Link,
    Domain,
    Type,
    TLD_Manager,
    RegistrationUrl,
    Whois,
    Rdap,
    `DnsResolve-A`
FROM
    IANA_TLD
    """

        result, cursor = self.selectSql(sql)
        return result, cursor
