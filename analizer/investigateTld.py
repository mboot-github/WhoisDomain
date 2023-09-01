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
from whoisdomain.tldDb import tld_regexpr


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


def normalizeRow(row: Any) -> Tuple[str, str, str, str, str, str, str, str]:
    tld = row[0].replace("'", "")

    tld2 = "".join(map(lambda s: s and re.sub(r"[^\w\s]", "", s), row[1]))

    tld3 = row[1].replace(".", "").replace("'", "").replace("\u200f", "").replace("\u200e", "")
    tld4 = tld3

    manager = row[3]
    w = row[4].replace("'", "")
    resolve = row[5]
    reg = row[6]

    return tld, tld2, tld3, tld4, manager, w, resolve, reg


def doOneRow(
    row: Any,
    allTld: List[str],
    ss: Dict[str, Any],
    verbose: bool = False,
):
    if verbose:
        print(row, file=sys.stderr)

    tld, tld2, tld3, tld4, manager, w, resolve, reg = normalizeRow(row)

    if tld not in allTld:
        allTld.append(tld)

    # look for a whois server in iana with a different or no server in the list
    if not w or w == "NULL":
        # we can create a privateRegistry when there is no whois server
        if tld not in tld_regexpr.ZZ:
            print(f'ZZ["{tld}"] = ' + '{"_privateRegistry": True} # no whois server found in iana')
        return

    if tld not in tld_regexpr.ZZ:
        print(f"# unknown tld {tld}, {tld2}, {tld3}, {tld4}, {w},")
        return
    k = "_server"
    s1 = ""

    TLD = tld_regexpr.ZZ[tld]
    if k in TLD:
        s1 = TLD[k]

    if "whois.centralnicregistry.com." in resolve:
        return

        kk = "_centralnic"
        if s1 == w and "extend" in TLD and TLD["extend"] in [kk, "com"]:
            return

        s = f"ZZ['{tld}']" + ' = {"extend": ' + f"{kk}, " + '"_server":' + f'"{w}"' + "} # < suggest ### "

        if "extend" in TLD:
            print(s, "# current > ", s1, w, TLD["extend"], TLD)
        else:
            print(s, "# current > ", s1, w, "_no_extend_", TLD)

        return

    if "whois.donuts.co" in resolve:
        return
        kk = "_donuts"
        if s1 == w and "extend" in TLD and TLD["extend"] in [kk, "com"]:
            return

        s = f"ZZ['{tld}']" + ' = {"extend": ' + f"{kk}, " + '"_server":' + f'"{w}"' + "} # suggest ### "

        if "extend" in TLD:
            print(s, "# current ", s1, w, TLD["extend"], TLD)
        else:
            print(s, "# current ", s1, w, "_no_extend_", TLD)

        return

    try:
        tld3 = idna2.encode(tld3).decode() or tld3
    except Exception as e:
        print(f"## {tld} {tld2} {tld3} {e}")
        return

    tld4 = tld4.encode("idna").decode()
    if tld != tld2:
        if 0 and tld2 not in ss:
            print("# idna", tld, tld2, tld3, tld4, tld.encode("idna"))

    if tld != tld3:
        print(f"#SKIP {tld} {tld2} { tld3}")
        return

    if tld2 == tld and tld in tld_regexpr.ZZ:
        return

    if tld2 in tld_regexpr.ZZ and tld in tld_regexpr.ZZ:
        return

    if manager == "NULL":
        if tld not in tld_regexpr.ZZ:
            print(f'ZZ["{tld}"] = ' + '{"_privateRegistry": True}')

        if tld2 != tld:
            if tld2 not in tld_regexpr.ZZ:
                print(f'ZZ["{tld2}"] = ' + '{"_privateRegistry": True}')

        return

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
                if tld not in tld_regexpr.ZZ:
                    print(f'ZZ["{tld}"] = ' + '{"_server": "' + n + '", "extend": "' + key + '"}')
                if tld2 != tld:
                    if tld2 not in tld_regexpr.ZZ:
                        print(f'ZZ["{tld2}"] = ' + '{"_server": "' + n + '", "extend": "' + key + '"}')
                found = True

            if found:
                break
        if found:
            break

    if found:
        return

    if reg == "NULL" and w == "NULL":
        return  # unclear,
        # we have existing ns records indicating some tld's actually exist
        # but have no whois, lets skip for now
        # TODO add ns records
        if tld not in tld_regexpr.ZZ:
            print(f'ZZ["{tld}"] = ' + '{"_privateRegistry": True}')

    if w == "NULL":
        return

    w = w.replace("'", "")
    if w in ss:
        if tld not in tld_regexpr.ZZ:
            print(
                f'ZZ["{tld}"] = ' + '{"_server": "' + w + '", "extend": "' + ss[w][0] + '"}',
                "# ",
                w,
                ss[w],
            )

        if tld2 != tld:
            if tld2 not in tld_regexpr.ZZ:
                print(
                    f'ZZ["{tld2}"] = ' + '{"_server": "' + w + '", "extend": "' + ss[w][0] + '"}',
                    "# ",
                    w,
                    ss[w],
                )
        return

    print("# MISSING", tld, tld2, tld3, manager.replace("\n", ";"), w, resolve, reg)


def xMain() -> None:
    verbose = False
    dbFileName = "IanaDb.sqlite"

    ss = extractServers(tld_regexpr.ZZ)
    allTld: List[str] = []

    iad = IanaDatabase(verbose=verbose)
    iad.connectDb(dbFileName)
    rr, cur = getAllDataTld(iad)

    for row in cur:
        doOneRow(row, allTld, ss)

    allTld = sorted(allTld)
    for tld in tld_regexpr.ZZ:
        if "." in tld:
            continue
        if "_" == tld[0]:
            continue

        try:
            tld2 = idna2.encode(tld).decode() or tld
        except Exception as e:
            print(f"{tld} {e} ", file=sys.stderr)
            tld2 = tld

        if tld not in allTld and tld2 not in allTld:
            print(f"# currently defined in ZZ but missing in iana: {tld}")


xMain()
