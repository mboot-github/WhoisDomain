import sys
from typing import Any

import tld
import whodap

import whoisdomain


class WhoisRdap:
    def __init__(self) -> None:
        self.dnsc = whodap.DNSClient.new_client()  # make sure we cache the primary looup for the tld rdap servers

    def do_one_domain(self, domain: str) -> dict[str, Any] | None:
        try:
            fld = tld.get_fld(domain, fix_protocol=True, fail_silently=True)
            a = fld.split(".")
            dom = ".".join(a[:-1])
            xtld = a[-1]
            resp = self.dnsc.lookup(dom, xtld)
            return resp.to_whois_dict()
        except Exception as e:
            print(f"Exception: {e}", file=sys.stderr)

        return None


def xmain() -> None:
    rr = {}

    wr = WhoisRdap()
    for k, v in whoisdomain.tldDb.tld_regexpr.ZZ.items():
        server = v.get("_server")
        test = v.get("_test")
        if not server:
            continue

        print("##", k, server, test)
        fld = tld.get_fld(server, fix_protocol=True, fail_silently=True)
        if fld in rr:
            continue

        rr[fld] = wr.do_one_domain(server)
        if rr[fld]:
            print(fld, rr[fld])


xmain()
