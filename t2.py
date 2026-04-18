import sys
from typing import Any

import httpx
import tld
import whodap

import whoisdomain

client = httpx.Client(follow_redirects=True, timeout=10)
dns_client = whodap.DNSClient.new_client(client)


def do_one_domain(domain: str) -> dict[str, Any] | None:
    d = None
    try:
        fld = tld.get_fld(domain, fix_protocol=True, fail_silently=True)
        a = fld.split(".")
        dom = ".".join(a[:-1])
        xtld = a[-1]
        resp = dns_client.lookup(dom, xtld)
        d = resp.to_whois_dict()
    except Exception as e:
        print(f"Exception: {e}", file=sys.stderr)

    return d


def xmain() -> None:
    for k, v in whoisdomain.tldDb.tld_regexpr.ZZ.items():
        server = v.get("_server")
        test = v.get("_test")
        if not server:
            continue

        print("##", k, server, test)
        fld = tld.get_fld(server, fix_protocol=True, fail_silently=True)
        rr = {}
        if fld not in rr:
            rr[fld] = do_one_domain(server)
            if rr[fld]:
                print(fld, rr[fld])


xmain()
