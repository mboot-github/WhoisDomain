#! /usr/bin/env python3
from typing import (
    Optional,
    List,
    Dict,
    Any,
)

import sys
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

    def createTable(self) -> None:
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

    def makeInsOrUpdSql(
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
            if values[i]:
                v = values[i]
                if not isinstance(v, str):
                    v = json.dumps(v, ensure_ascii=False)
                v = "'" + v + "'"
            data.append(v)
            vvv.append("?")
            i += 1

        vv = ",".join(vvv)

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


def xMain():
    verbose = False
    dbFileName = "IanaDb.sqlite"

    iad = IanaDatabase(verbose=verbose)
    iad.connectDb(dbFileName)
    iad.createTable()

    resolver = dns.resolver.Resolver()
    resolver.cache = dns.resolver.Cache(
        cleaning_interval=3600
    )  # does not cache to file only in memory, currently

    iac = IanaCrawler(verbose=verbose, resolver=resolver)
    iac.getTldInfo()
    iac.addInfoToAllTld()

    xx = iac.getResults()

    for item in xx["data"]:
        sql, data = iad.makeInsOrUpdSql(xx["header"], item)
        rr = iad.doSql(sql, data)
        print(rr)

    print(json.dumps(iac.getResults(), indent=2, ensure_ascii=False))


xMain()
