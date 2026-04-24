import re
import sys
from typing import (
    Any,
)

import idna as idna2

# the next 2 belong together
sys.path.append("..")

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
    allKnownTldDict: dict[str, Any] = {}

    row: Any = None
    allTld: dict[str, Any] = {}
    server_hints: list[str] = []

    tld = None
    tld2 = None
    tld3 = None
    tld4 = None

    manager: str = ""
    whois_hint: str = ""
    resolved_whois_servers: str = ""
    registration_url: str = ""
    rdap_info: str = ""
    thisTld: dict[str, Any] = {}

    def __init__(
        self,
        allKnownTldDict: dict[str, Any],
        verbose: bool = False,
    ):
        self.verbose = verbose
        self.allKnownTldDict = allKnownTldDict

    def _normalizeRow(self) -> None:
        # print("row:", self.row, file=sys.stderr)

        # 0: Link
        # 1: Domain
        # 2: Type
        # 3: TldManager
        # 4: REgistrationUrl
        # 5: Whois
        # 6: RDap
        # 7: whois resolved
        self.tld = self.row[0]
        self.tld2 = "".join(map(lambda s: s and re.sub(r"[^\w\s]", "", s), self.row[1]))  # noqa: C417
        self.tld3 = self.row[1].replace(".", "").replace("\u200f", "").replace("\u200e", "")  # utf8 right to left
        self.tld4 = self.tld3

        self.manager = self.row[3]
        self.registration_url = self.row[4]
        self.whois_hint = self.row[5]
        self.resolved_whois_servers = self.row[7]
        self.rdap_info = self.row[6]

    def _doCentralNic(self, s1: str, TLD: dict[str, Any]) -> bool:
        return True

        kk = "_centralnic"
        if s1 == self.whois_hint and "extend" in TLD and TLD["extend"] in [kk, "com"]:
            return True

        s = f'ZZ[\'{self.tld}\'] = {{"extend": {kk}, "_server":"{self.whois_hint}"}} # < suggest ### '

        if "extend" in TLD:
            print(s, "# current > ", s1, self.whois_hint, TLD["extend"], TLD)
        else:
            print(s, "# current > ", s1, self.whois_hint, "_no_extend_", TLD)

        return True

    def _doDonuts(self, s1: str, TLD: dict[str, Any]) -> bool:
        # currently not used
        return True

        kk = "_donuts"
        if s1 == self.whois_hint and "extend" in TLD and TLD["extend"] in [kk, "com"]:
            return True

        s = f'ZZ[\'{self.tld}\'] = {{"extend": {kk}, "_server":"{self.whois_hint}"}} # suggest ### '

        if "extend" in TLD:
            print(s, "# current ", s1, self.whois_hint, TLD["extend"], TLD)
        else:
            print(s, "# current ", s1, self.whois_hint, "_no_extend_", TLD)

        return True

    def _doUnknownTld(self):
        if not self.whois_hint or self.whois_hint == "NULL":  # no whois server defined
            print(f'# ZZ["{self.tld}"] = ' + '{"_privateRegistry": True} # no whois server found in iana')
        else:
            print(f"# unknown tld {self.tld}, {self.tld2}, {self.tld3}, {self.tld4}, {self.whois_hint},")

    def _getServerHint(self):
        k = "_server"
        serverHint = ""
        if k in self.thisTld:
            serverHint = self.thisTld[k]
        return serverHint

    def _skipSpecialResolve(self):
        serverHint = self._getServerHint()

        if "whois.centralnicregistry.com." in self.resolved_whois_servers and self._doCentralNic(
            serverHint, self.thisTld
        ):
            return True

        return "whois.donuts.co" in self.resolved_whois_servers and self._doCentralNic(serverHint, self.thisTld)

    def _doUtf8Preparations(self):
        try:
            self.tld3 = idna2.encode(self.tld3).decode() or self.tld3
        except Exception as e:
            print(f"## {self.tld} {self.tld2} {self.tld3} {e}")
            return None

        self.tld4 = self.tld4.encode("idna").decode()
        if self.tld != self.tld3:
            print(f"#SKIP {self.tld} {self.tld2} {self.tld3}")
            return True

        return False

    def _skipKnowTld(self):
        z = self.allKnownTldDict.get(self.tld, {}).get("_privateRegistry")
        if z is not None:
            return False

        if self.tld2 == self.tld and self.tld in self.allKnownTldDict:
            return True

        return self.tld2 in self.allKnownTldDict and self.tld in self.allKnownTldDict

    def _doNoManagerTld(self):
        if self.manager == "NULL":
            print(f"no manager for tld: {self.tld}")
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
                if n in self.resolved_whois_servers:
                    if self.tld not in self.allKnownTldDict:
                        print(f'ZZ["{self.tld}"] = ' + '{"_server": "' + n + '", "extend": "' + key + '"}')
                    if self.tld2 != self.tld:
                        if self.tld2 not in self.allKnownTldDict:
                            print(f'ZZ["{self.tld2}"] = ' + '{"_server": "' + n + '", "extend": "' + key + '"}')
                    return True
        return False

    def _doNoWhois(self):
        if self.registration_url == "NULL" and self.whois_hint == "NULL":
            print(f"{self.tld} has no whois and no reg server", file=sys.stderr)
            return True

        if self.whois_hint == "NULL":
            if self.tld not in self.allKnownTldDict:
                print(f'# ZZ["{self.tld}"] = ' + '{"_privateRegistry": True} # noWhois ')

        return self.whois_hint == "NULL"

    def _do_cleanup_whois_info(self):
        def xx(zz):
            if zz not in self.allKnownTldDict:
                x = '{"_server": "' + self.whois_hint + f'", "extend": {self.server_hints[self.whois_hint][0]}' + '"}'
                y = f"# {self.whois_hint} {self.server_hints[self.whois_hint]}"
                print(f'ZZ["{zz}"] = ', x, y)

        self.whois_hint = self.whois_hint.replace("'", "")
        if self.whois_hint in self.server_hints:
            xx(self.tld)
            if self.tld2 != self.tld:
                xx(self.tld2)
            return True
        return False

    def processRow(
        self,
        row: Any,
        allTld: dict[str, Any],
        server_hints: list[str],
    ):
        self.allTld = allTld
        self.server_hints = server_hints

        self.row = list(row)  # from tuple to list and cleanup the strings
        for index, data in enumerate(self.row):
            data = data.replace("'", "")
            self.row[index] = data

        # ---------------------------------
        self._normalizeRow()
        if self.tld not in self.allTld:
            self.allTld.append(self.tld)

        if self.allKnownTldDict.get(self.tld) is None:
            if self.verbose:
                print(f"|{self.tld}|", file=sys.stderr)
            self._doUnknownTld()
            return

        self.thisTld = self.allKnownTldDict[self.tld]

        # run a sequence of functions are return if we have a value
        sequence = [
            self._skipSpecialResolve,
            self._doUtf8Preparations,
            self._skipKnowTld,
            self._doNoManagerTld,
            self._doFoundTld,
            self._doNoWhois,
            self._do_cleanup_whois_info,
        ]

        for n in sequence:
            if n():
                return

        if "whois.identitydigital.services" in self.resolved_whois_servers:
            return

        if "tucowsregistry.net" in self.resolved_whois_servers:
            return

        print(
            "# MISSING",
            self.tld,
            self.tld2,
            self.tld3,
            self.manager.replace("\n", ";"),
            self.whois_hint,
            self.resolved_whois_servers,
            self.registration_url,
        )
