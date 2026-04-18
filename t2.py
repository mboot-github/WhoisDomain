import sys
from typing import Any

import tld
import whodap

import whoisdomain


class DataResponse:  # noqa: B903
    status: bool  # if status is True we have data else a message
    data: Any
    message: str

    def __init__(
        self,
        *,
        status: bool = False,
        data: Any = None,
        message: str = "",
    ) -> None:
        self.status = status
        self.data = data
        self.message = message


class WhoisRdap:
    def __init__(self) -> None:
        self.dnsc = whodap.DNSClient.new_client()  # make sure we cache the primary looup for the tld rdap servers

    def fld(self, domain: str) -> str:
        return tld.get_fld(domain, fix_protocol=True, fail_silently=True)

    def do_one_domain(self, domain: str) -> DataResponse:
        try:
            xfld = self.fld(domain)
            a = xfld.split(".")
            dom = ".".join(a[:-1])
            xtld = a[-1]
            resp = self.dnsc.lookup(dom, xtld)
            return DataResponse(status=True, data=resp.to_whois_dict())
        except Exception as e:
            print(f"Exception: {e}", file=sys.stderr)
            return DataResponse(status=False, message=e)


def xmain() -> None:
    rr = {}

    wr = WhoisRdap()
    for k, v in whoisdomain.tldDb.tld_regexpr.ZZ.items():
        server = v.get("_server")
        test = v.get("_test")
        if not server:
            continue

        print("##", k, server, test)

        xfld = wr.fld(server)
        if xfld not in rr:
            dd = wr.do_one_domain(server)
            rr[xfld] = dd.data if dd.status else dd.message
            if rr[xfld]:
                print("Server:", xfld, rr[xfld])

        if test:
            dd = wr.do_one_domain(test)
            print("Test:", test, dd.data if dd.status else dd.message)


xmain()
