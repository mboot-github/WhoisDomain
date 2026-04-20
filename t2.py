import logging

import whoisdomain
from whois_rdap import WhoisRdap

logger = logging.getLogger(__name__)

def xmain() -> None:
    rr = {}

    logging.basicConfig(
        filename="myapp.log",
        level=logging.WARNING,
    )

    wr = WhoisRdap()
    for k, v in whoisdomain.ZZ.items():
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
                print("Server:", server, xfld, rr[xfld])
                if dd.status:
                    print(wr.map_data_to_whoisdomain(dd.data, with_rdap_whois=True))
        if test and test != xfld:
            dd = wr.do_one_domain(test)
            print("Test:", test, dd.data if dd.status else dd.message)
            if dd.status:
                print(wr.map_data_to_whoisdomain(dd.data, with_rdap_whois=True))


xmain()
