#! /usr/bin/env python3
from typing import (
    Optional,
    List,
    Dict,
    Any,
)

import sys
import io
import re
import time
import requests_cache
import dns.resolver
import json
import sqlite3
from bs4 import BeautifulSoup


class IanaDatabase:
    verbose: bool = False
    conn = None

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
            raise Exception("No valid connection to the database exist")

    def doSql(
        self,
        sql: str,
        data: Any = None,
    ):
        self.testValidConnection()
        cur = self.conn.cursor()
        try:
            if data:
                result = cur.execute(sql, data)
            else:
                result = cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(sql, e, file=sys.stderr)
            exit(101)
        return result

    def createTableTld(self) -> None:
        sql = """
CREATE TABLE IF NOT EXISTS IANA_TLD (
    Link            TEXT PRIMARY KEY,
    Domain          TEXT NOT NULL UNIQUE,
    Type            TEXT NOT NULL,
    TLD_Manager     TEXT,
    Whois           TEXT,
    'DnsResolve-A'  TEXT,
    RegistrationUrl TEXT
);
"""
        rr = self.doSql(sql)
        if self.verbose:
            print(rr, file=sys.stderr)

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
        rr = self.doSql(sql)
        if self.verbose:
            print(rr, file=sys.stderr)

    def prepData(
        self,
        columns: List[str],
        values: List[str],
    ):
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
        columns: List[str],
        values: List[str],
    ):
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

    def makeInsOrUpdSqlPsl(
        self,
        columns: List[str],
        values: List[str],
    ):
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


class IanaCrawler:
    URL: str = "https://www.iana.org/domains/root/db"
    CacheTime = 3600 * 24  # default 24 hours
    Session = None
    cacheName = ".iana_cache"
    verbose: bool = False
    cacheBackend: str = "filesystem"
    records = []
    columns = []

    resolver = None

    def __init__(
        self,
        verbose: bool = False,
        resolver=None,
    ):
        self.verbose = verbose
        self.resolver = resolver
        self.Session = requests_cache.CachedSession(
            self.cacheName,
            backend=self.cacheBackend,
        )

    def getUrl(self) -> str:
        return self.URL

    def getBasicBs(
        self,
        url: str,
    ) -> BeautifulSoup:
        try:
            response = self.Session.get(url)
        except Exception as e:
            # in case of no data, sleep and try again
            print(e, file=sys.stderr)
            time.sleep(15)
            response = self.Session.get(url)

        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def getAdditionalItem(
        self,
        what: str,
        data: List,
    ) -> Optional[str]:
        for i in [0, 1]:
            try:
                z: str = f"{what}:"
                if z in data[i]:
                    return data[i].replace(z, "").strip()
            except Exception as _:
                _ = _
                return None
        return None

    def getTldInfo(self) -> None:
        soup = self.getBasicBs(self.getUrl())
        table = soup.find("table")  # the first table has the tld data

        self.records = []
        self.columns = []
        n = 0
        for tr in table.findAll("tr"):
            n += 1
            # extract header info if present
            ths = tr.findAll("th")
            if ths != []:
                for each in ths:
                    self.columns.append(each.text)
                continue

            # extrct data
            trs = tr.findAll("td")
            record = []
            for each in trs:
                try:
                    link = each.find("a")["href"]
                    aa = link.split("/")
                    record.append(aa[-1].replace(".html", ""))
                    record.append(each.text.strip())
                except Exception as _:
                    _ = _
                    record.append(each.text)
            self.records.append(record)

        self.columns.insert(0, "Link")

    def getTldWhois(
        self,
        url: str,
    ) -> Optional[str]:
        soup = self.getBasicBs(url)
        text: str = "WHOIS"
        gfg = soup.find_all(lambda tag: tag.name == "p" and text in tag.text)
        if len(gfg):
            return gfg[0].text.strip()
        return None

    def resolveWhois(
        self,
        whois: str,
    ) -> List[Any]:
        ll = []
        if self.resolver:
            answer = list(self.resolver.resolve(whois, "A").response.answer)
            for a in answer:
                s = str(a)
                if "\n" in s:
                    ss = s.split("\n")
                    ll.append(ss)
                else:
                    ll.append(s)

                if self.verbose:
                    print(a)
        return ll

    def addInfoToOneTld(
        self,
        tldItem: List[str],
    ) -> List[str]:
        url = tldItem[0]
        print(url, file=sys.stderr)

        if tldItem[3] == "Not assigned":
            tldItem[3] = None

        regData = self.getTldWhois(self.getUrl() + "/" + url + ".html")
        if regData:
            regData = regData.replace("URL for registration services", "RegistrationUrl")
            regData = regData.replace("WHOIS Server", "Whois")
            regDataA = regData.split("\n")
            for s in ["Whois", "RegistrationUrl"]:
                tldItem.append(self.getAdditionalItem(s, regDataA))
        else:
            tldItem.append(None)
            tldItem.append(None)

        if tldItem[4]:
            ll = self.resolveWhois(tldItem[4])
            tldItem.append(ll)
        else:
            tldItem.append(None)

        return tldItem

    def addInfoToAllTld(self) -> None:
        records2 = []
        for tldItem in self.records:
            rr = self.addInfoToOneTld(tldItem)
            if self.verbose:
                print(len(rr), rr)
            records2.append(rr)
        self.columns.insert(4, "Whois")
        self.columns.insert(5, "RegistrationUrl")
        self.columns.insert(6, "DnsResolve-A")
        self.records = records2
        self.columns[3] = self.columns[3].replace(" ", "_")

    def getResults(self) -> Dict[str, Any]:
        ll = list(self.columns)
        ll[3] = ll[3].replace(" ", "_")
        return {
            "header": ll,
            "data": self.records,
        }


class PslGrabber:
    # notes: https://github.com/publicsuffix/list/wiki/Format

    URL: str = "https://publicsuffix.org/list/public_suffix_list.dat"
    CacheTime = 3600 * 24  # default 24 hours
    Session = None
    cacheName = ".psl_cache"
    verbose: bool = False
    cacheBackend: str = "filesystem"

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.Session = requests_cache.CachedSession(
            self.cacheName,
            backend=self.cacheBackend,
        )

    def getUrl(self) -> str:
        return self.URL

    def getData(
        self,
        url: str,
    ):
        response = self.Session.get(url)
        return response

    def ColumnsPsl(self):
        return [
            "Tld",
            "Psl",
            "Level",
            "Type",
            "Comment",
        ]


def xMain():
    verbose = False
    dbFileName = "IanaDb.sqlite"

    iad = IanaDatabase(verbose=verbose)
    iad.connectDb(dbFileName)
    iad.createTableTld()
    iad.createTablePsl()

    resolver = dns.resolver.Resolver()
    resolver.cache = dns.resolver.Cache(cleaning_interval=3600)  # does not cache to file only in memory, currently

    iac = IanaCrawler(verbose=verbose, resolver=resolver)
    iac.getTldInfo()
    iac.addInfoToAllTld()

    xx = iac.getResults()

    for item in xx["data"]:
        sql, data = iad.makeInsOrUpdSqlTld(xx["header"], item)
        rr = iad.doSql(sql, data)

    print(json.dumps(iac.getResults(), indent=2, ensure_ascii=False))

    pg = PslGrabber()
    response = pg.getData(pg.getUrl())
    text = response.text
    buf = io.StringIO(text)

    section = ""
    while True:
        line = buf.readline()
        if not line:
            break

        z = line.strip()
        if len(z):
            if "// ===END " in z:
                section = ""

            if "// ===BEGIN ICANN" in z:
                section = "ICANN"

            if "// ===BEGIN PRIVATE" in z:
                section = "PRIVATE"

            if section == "PRIVATE":
                continue

            if re.match(r"^\s*//", z):
                # print("SKIP", z)
                continue

            n = 0
            z = z.split()[0]
            if "." in z:
                tld = z.split(".")[-1]
                n = len(z.split("."))
            else:
                tld = z

            sql, data = iad.makeInsOrUpdSqlPsl(pg.ColumnsPsl(), [tld, z, n, section, None])
            print(data)
            r = iad.doSql(sql, data)


xMain()
