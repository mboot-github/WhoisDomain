#! /usr/bin/env python3

# should run after a valid database is created with analizeIanaTld.py

from typing import (
    Dict,
    Any,
    List,
    Tuple,
)

import re
import sys

import idna as idna2

from ianaDatabase import IanaDatabase

# the next 2 belong together
sys.path.append("..")
from whoisdomain.tldDb import tld_regexpr  # noqa: E402

MM = {
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


class OneTld:
    verbose: bool = True
    allKnownTldDict: Dict[str, Any] = {}

    row: Any = None
    allTld: Dict[str, Any] = {}
    ss: List[str] = []

    tld = None
    tld2 = None
    tld3 = None
    tld4 = None

    manager = None
    w = None
    resolve = None
    reg = None

    thisTld: Dict[str, Any] = {}

    def __init__(
        self,
        allKnownTldDict: Dict[str, Any],
        verbose: bool = False,
    ):
        self.verbose = verbose
        self.allKnownTldDict = allKnownTldDict

    def _normalizeRow(self) -> None:
        self.tld = self.row[0].replace("'", "")
        self.tld2 = "".join(map(lambda s: s and re.sub(r"[^\w\s]", "", s), self.row[1]))
        self.tld3 = self.row[1].replace(".", "").replace("'", "").replace("\u200f", "").replace("\u200e", "")
        self.tld4 = self.tld3

        self.manager = self.row[3]
        self.w = self.row[4].replace("'", "")
        self.resolve = self.row[5]
        self.reg = self.row[6]

    def _doCentralNic(self, s1: str, TLD: Dict[str, Any]) -> bool:
        return True

        kk = "_centralnic"
        if s1 == self.w and "extend" in TLD and TLD["extend"] in [kk, "com"]:
            return True

        s = f"ZZ['{self.tld}']" + ' = {"extend": ' + f"{kk}, " + '"_server":' + f'"{self.w}"' + "} # < suggest ### "

        if "extend" in TLD:
            print(s, "# current > ", s1, self.w, TLD["extend"], TLD)
        else:
            print(s, "# current > ", s1, self.w, "_no_extend_", TLD)

        return True

    def _doDonuts(self, s1: str, TLD: Dict[str, Any]) -> bool:
        # currently not used
        return True

        kk = "_donuts"
        if s1 == self.w and "extend" in TLD and TLD["extend"] in [kk, "com"]:
            return True

        s = f"ZZ['{self.tld}']" + ' = {"extend": ' + f"{kk}, " + '"_server":' + f'"{self.w}"' + "} # suggest ### "

        if "extend" in TLD:
            print(s, "# current ", s1, self.w, TLD["extend"], TLD)
        else:
            print(s, "# current ", s1, self.w, "_no_extend_", TLD)

        return True

    def _doUnknownTld(self):
        if not self.w or self.w == "NULL":  # no whois server defined
            print(f'# ZZ["{self.tld}"] = ' + '{"_privateRegistry": True} # no whois server found in iana')
        else:
            print(f"# unknown tld {self.tld}, {self.tld2}, {self.tld3}, {self.tld4}, {self.w},")

    def _getServerHint(self):
        k = "_server"
        serverHint = ""
        if k in self.thisTld:
            serverHint = self.thisTld[k]
        return serverHint

    def _skipSpecialResolve(self):
        serverHint = self._getServerHint()

        if "whois.centralnicregistry.com." in self.resolve and self._doCentralNic(serverHint, self.thisTld):
            return True

        if "whois.donuts.co" in self.resolve and self._doCentralNic(serverHint, self.thisTld):
            return True

        return False

    def _doUtf8Preparations(self):
        try:
            self.tld3 = idna2.encode(self.tld3).decode() or self.tld3
        except Exception as e:
            print(f"## {self.tld} {self.tld2} {self.tld3} {e}")
            return

        self.tld4 = self.tld4.encode("idna").decode()
        if self.tld != self.tld2:
            if 0 and self.tld2 not in self.ss:
                print("# idna", self.tld, self.tld2, self.tld3, self.tld4, self.tld.encode("idna"))

        if self.tld != self.tld3:
            print(f"#SKIP {self.tld} {self.tld2} {self.tld3}")
            return True

        return False

    def _skipKnowTld(self):
        if self.tld2 == self.tld and self.tld in self.allKnownTldDict:
            return True

        if self.tld2 in self.allKnownTldDict and self.tld in self.allKnownTldDict:
            return True

        return False

    def _doNoManagerTld(self):
        if self.manager == "NULL":
            if self.tld not in self.allKnownTldDict:
                print(f'# ZZ["{self.tld}"] = ' + '{"_privateRegistry": True} # no manager')

            if self.tld2 != self.tld:
                if self.tld2 not in self.allKnownTldDict:
                    print(f'# ZZ["{self.tld2}"] = ' + '{"_privateRegistry": True} # no manager')

            return True

        return False

    def _doFoundTld(self):
        for key, value in MM.items():
            for n in value:
                if n in self.resolve:
                    if self.tld not in self.allKnownTldDict:
                        print(f'ZZ["{self.tld}"] = ' + '{"_server": "' + n + '", "extend": "' + key + '"}')
                    if self.tld2 != self.tld:
                        if self.tld2 not in self.allKnownTldDict:
                            print(f'ZZ["{self.tld2}"] = ' + '{"_server": "' + n + '", "extend": "' + key + '"}')
                    return True
        return False

    def _doNoWhois(self):
        if self.reg == "NULL" and self.w == "NULL":
            return True
            # unclear,
            # we have existing ns records indicating some self.tld's actually exist
            # but have no whois, lets skip for now
            # TODO add ns records
            if self.tld not in self.allKnownTldDict:
                print(f'# ZZ["{self.tld}"] = ' + '{"_privateRegistry": True} # noWhois ')

        if self.w == "NULL":
            return True

        return False

    def _doCleanuphois(self):
        def xx(zz):
            if zz not in self.allKnownTldDict:
                print(
                    f'ZZ["{zz}"] = ' + '{"_server": "' + self.w + '", "extend": "' + self.ss[self.w][0] + '"}',
                    "# ",
                    self.w,
                    self.ss[self.w],
                )

        self.w = self.w.replace("'", "")
        if self.w in self.ss:
            xx(self.tld)
            if self.tld2 != self.tld:
                xx(self.tld2)
            return True
        return False

    def processRow(
        self,
        row: Any,
        allTld: Dict[str, Any],
        ss: List[str],
    ):
        sequence = [
            self._skipSpecialResolve,
            self._doUtf8Preparations,
            self._skipKnowTld,
            self._doNoManagerTld,
            self._doFoundTld,
            self._doNoWhois,
            self._doCleanuphois,
        ]

        self.row = row
        self.allTld = allTld
        self.ss = ss

        self._normalizeRow()
        if self.tld not in self.allTld:
            self.allTld.append(self.tld)

        if self.allKnownTldDict.get(self.tld) is None:
            if self.verbose:
                print(f"|{self.tld}|", file=sys.stderr)
            self._doUnknownTld()
            return

        self.thisTld = self.allKnownTldDict[self.tld]

        for n in sequence:
            if n():
                return

        print("# MISSING", self.tld, self.tld2, self.tld3, self.manager.replace("\n", ";"), self.w, self.resolve, self.reg)


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


def getAllDataTld(iad: Any) -> Tuple[Any, Any]:
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

    result, cursor = iad.selectSql(sql)
    return result, cursor


def postProcessingOne(allTld: List[str], tld: str):
    if "." in tld:
        return
    if "_" == tld[0]:
        return

    try:
        tld2 = idna2.encode(tld).decode() or tld
    except Exception as e:
        print(f"{tld} {e} ", file=sys.stderr)
        tld2 = tld

    if tld not in allTld and tld2 not in allTld:
        print(f"# currently defined in ZZ but missing in iana: {tld}")


def postProcessing(allTld: List[str]):
    allTld = sorted(allTld)
    for tld in tld_regexpr.ZZ:
        postProcessingOne(allTld, tld)


def xMain() -> None:
    verbose = True
    dbFileName = "IanaDb.sqlite"
    allTld: List[str] = []

    ss = extractServers(tld_regexpr.ZZ)

    iad = IanaDatabase(verbose=verbose)
    iad.connectDb(dbFileName)
    rr, cur = getAllDataTld(iad)
    for row in cur:
        ot = OneTld(tld_regexpr.ZZ, verbose=verbose)
        ot.processRow(row, allTld, ss)

    postProcessing(allTld)


xMain()
