import sys
import time
from typing import (
    Any,
    # Tuple,
)

import requests_cache
from bs4 import BeautifulSoup


class IanaCrawler:
    URL: str = "https://www.iana.org/domains/root/db"

    CacheTime: int = 3600 * 24  # default 24 hours
    Session: Any = None
    cacheName: str = ".iana_cache"
    verbose: bool = False
    cacheBackend: str = "filesystem"

    records: list[Any] = []
    columns: list[Any] = []
    toDelete: list[str] = []

    resolver: Any = None

    def __init__(
        self,
        verbose: bool = False,
        resolver: Any = None,
    ):
        self.verbose = verbose
        self.resolver = resolver
        self.Session = requests_cache.CachedSession(
            self.cacheName,
            backend=self.cacheBackend,
        )

    def _getUrl(self) -> str:
        return self.URL

    """
    get the data from the url , with retry N times
    return the data as soup
    """

    def _getPageFromUrlIntoSoupWithRetry(
        self,
        url: str,
    ) -> BeautifulSoup:
        maxTry: int = 5
        n: int = 0
        response = None
        while n < maxTry:
            n += 1
            try:
                response = self.Session.get(url)
            except Exception as e:
                # in case of no data, sleep and try again
                print(e, file=sys.stderr)
                time.sleep(15)

        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def _getAdditionalItem(
        self,
        what: str,
        data: list[str],
    ) -> str | None:
        for i in [0, 1]:
            try:
                z: str = f"{what}:"
                if z in data[i]:
                    return data[i].replace(z, "").strip()
            except Exception as _:
                _ = _
                return None
        return None

    def _getTldParagraphWithString(
        self,
        soup: BeautifulSoup,
        text: str,
    ) -> str | None:
        gfg: list[Any] = soup.find_all(lambda tag: tag.name == "p" and text in tag.text)
        if len(gfg):
            s: str = gfg[0].text.strip()
            return s
        return None

    def _resolveWhois(
        self,
        whois: str,
    ) -> list[Any]:
        ll: list[Any] = []
        if self.resolver:
            answer: list[Any] = []

            n: int = 3
            while n:
                try:
                    answer = list(self.resolver.resolve(whois, "A").response.answer)
                    break
                except Exception as e:
                    print(whois, e, n, file=sys.stderr)
                    time.sleep(5)
                    n = n - 1

            for a in answer:
                s = str(a)
                if "\n" in s:
                    ss = s.split("\n")
                    ll.append(ss)
                else:
                    ll.append(s)

        return ll

    def extractInfoFromPageSoup(
        self,
        soup: BeautifulSoup,
        tldItem: list[Any],
    ) -> None:
        zz = {
            "Whois": "WHOIS Server",
            "RegistrationUrl": "URL for registration services",
        }

        for key, val in zz.items():
            regDataW: str | None = self._getTldParagraphWithString(soup, val)
            if not regDataW:
                tldItem.append(None)
                continue

            regDataW = regDataW.replace(val, key)
            regDataA = regDataW.split("\n")
            for s in [key]:
                tldItem.append(self._getAdditionalItem(s, regDataA))

    def doWhoisServerResolve_DoesItExist(
        self,
        server: str | None,
        tldItem: list[Any],
    ) -> None:
        if server is None:
            tldItem.append(None)
            return

        ll = self._resolveWhois(server)  # try to resolve the whois server, does it actually exist
        tldItem.append(ll)

    def _addInfoToOneTld(
        self,
        tldItem: list[Any],
    ) -> list[str]:
        tldName = tldItem[0]

        if tldItem[3] == "Not assigned":
            tldItem[3] = None
            return None

        tldUrl: str = self._getUrl() + "/" + tldName + ".html"
        soup = self._getPageFromUrlIntoSoupWithRetry(tldUrl)

        self.extractInfoFromPageSoup(soup, tldItem)
        self.doWhoisServerResolve_DoesItExist(tldItem[4], tldItem)

        return tldItem

    def _processOneTableData(self, trs: list[str]) -> list[str]:
        record: list[str] = []
        for each in trs:
            try:
                link = each.find("a")["href"]
                aa = link.split("/")
                record.append(aa[-1].replace(".html", ""))
                record.append(each.text.strip())
            except Exception as _:
                _ = _
                record.append(each.text)
        return record

    def _processOneTableRow(self, tr: str) -> None:
        # extract header info if present
        ths = tr.findAll("th")  # Table Header
        if ths != []:
            for each in ths:
                self.columns.append(each.text)
            return

        trs = tr.findAll("td")  # Table Data
        record = self._processOneTableData(trs)
        self.records.append(record)

    def getTldInfoAllFromIanaUrl(self) -> None:
        """
        Extract all current defined tld names from the main iana root db page

        """
        soup = self._getPageFromUrlIntoSoupWithRetry(self._getUrl())
        table: Any = soup.find("table")  # the first table has the tld data

        self.records: list[Any] = []
        self.columns: list[Any] = []

        for tr in table.findAll("tr"):  # Table Row
            self._processOneTableRow(tr)

        self.columns.insert(0, "Link")

    def addInfoToAllTld(self) -> None:
        records2: list[str] = []
        toDelete: list[str] = []

        self.columns[3] = self.columns[3].replace(" ", "_")
        self.columns.insert(4, "Whois")  # is there a whois server defined
        self.columns.insert(5, "RegistrationUrl")  # is there a registration url defined
        self.columns.insert(6, "DnsResolve-A")  # if we have a whois server does it actually resolve to sometething real

        for tldItem in self.records:  # tldItem is a list
            rr = self._addInfoToOneTld(tldItem)
            if rr is None:  # tld is not assigned any more
                toDelete.append(tldItem[0])
                continue
            records2.append(rr)

        self.records = records2
        self.toDelete = toDelete

    def getDeleted(
        self,
    ) -> list[str]:
        return self.toDelete

    def getResults(self) -> dict[str, Any]:
        ll = list(self.columns)
        # ll[3] = ll[3].replace(" ", "_")
        return {
            "header": ll,
            "data": self.records,
        }
