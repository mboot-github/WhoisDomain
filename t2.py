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

    def fld(self, domain: str) -> str | None:
        return tld.get_fld(domain, fix_protocol=True, fail_silently=True)

    def do_one_domain(self, domain: str) -> DataResponse:
        try:
            xfld = str(self.fld(domain))
            a = xfld.split(".")
            dom = ".".join(a[:-1])
            xtld = a[-1]
            resp = self.dnsc.lookup(dom, xtld)
            return DataResponse(status=True, data=resp.to_whois_dict())
        except Exception as e:
            print(f"Exception: {e}", file=sys.stderr)
            return DataResponse(status=False, message=str(e))

    @classmethod
    def get_registrant(cls, data: dict[str, Any]) -> tuple[str, str]:
        registrant = ""
        registrant_country = ""

        ll = [
            "registrant_email",
            "registrant_organization",
            "registrant_name",
        ]
        for k in ll:
            if not registrant and data[k]:
                registrant = data[k]
                break

        mm = [
            "registrant_address",
            "registrant_phone",
        ]
        for k in mm:
            if not registrant_country and data[k]:
                registrant_country = data[k]
                break

        return registrant, registrant_country

    @classmethod
    def get_registrar(cls, data: dict[str, Any]) -> str:
        ll = [
            "registrar_email",
            "registrar_name",
            "registrar_phone",
        ]
        for k in ll:
            if data[k]:
                return str(data[k])

        return ""

    @classmethod
    def get_emails(cls, data: dict[str, Any]) -> list[str]:
        r: list[str] = []
        email_fields: list[str] = [
            "abuse_email",
            "admin_email",
            "billing_email",
            "registrant_email",
            "registrar_email",
            "technical_email",
        ]
        for k in email_fields:
            if data[k] and "@" in data[k]:
                email = str(data[k])
                if email not in r:
                    r.append(email)

        return r

    @classmethod
    def map_data_to_whoisdomain(
        cls,
        data: dict[str, Any],
        *,
        with_rdap_whois: bool = False,
    ) -> dict[str, Any]:
        rr: dict[str, Any] = {}
        rr["name"] = data["domain_name"]
        rr["dnssec"] = data["dnssec"] == "signed"
        if data["abuse_email"]:
            rr["abuse_contact"] = data["abuse_email"]
        if data["admin_email"]:
            rr["admin"] = data["admin_email"]
        if data["nameservers"]:
            rr["name_servers"] = data["nameservers"]

        if data["created_date"]:
            rr["creation_date"] = data["created_date"]
        if data["updated_date"]:
            rr["updated_date"] = data["updated_date"]
        if data["expires_date"]:
            rr["expiration_date"] = data["expires_date"]

        rr["statuses"] = []
        rr["status"] = ""
        if data["status"]:
            rr["statuses"] = data["status"]
        if len(rr["statuses"]):
            rr["status"] = rr["statuses"][0]

        rr["emails"] = cls.get_emails(data)

        rr["registrant"], rr["registrant_country"] = cls.get_registrant(data)
        rr["registrar"] = cls.get_registrar(data)

        if with_rdap_whois:
            rr["_rdap_"] = data

        return rr


def xmain() -> None:
    rr = {}

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
                    print(wr.map_data_to_whoisdomain(dd.data, with_raw=True))
        if test and test != xfld:
            dd = wr.do_one_domain(test)
            print("Test:", test, dd.data if dd.status else dd.message)
            if dd.status:
                print(wr.map_data_to_whoisdomain(dd.data, with_rdap_whois=True))


xmain()

"""
#
domain_name -> name

abuse_contact

admin
owner
reseller

registrant
registrant_country
registrar

status -> statuses[0] if len(statuses) > 0 else ""
statuses []
name_servers []
emails []

creation_date
expiration_date
updated_date

dnssec: bool

{
    'name': 'google.com', # actual domain used (www.google.com -> google.com)
    'tld': 'com',
    'fld': '',          # new
    'registrar': 'MarkMonitor, Inc.',
    'registrant': 'Google LLC',
    'registrant_country': 'US',

    'creation_date': datetime.datetime(1997, 9, 15, 9, 0),
    'expiration_date': datetime.datetime(2028, 9, 13, 9, 0),
    'last_updated': datetime.datetime(2019, 9, 9, 17, 39, 4),

    'status': 'clientUpdateProhibited (https://www.icann.org/epp#clientUpdateProhibited)', # statuses[0] if exists.
    'statuses': [
        'clientDeleteProhibited (https://www.icann.org/epp#clientDeleteProhibited)',
        'clientTransferProhibited (https://www.icann.org/epp#clientTransferProhibited)',
        'clientUpdateProhibited (https://www.icann.org/epp#clientUpdateProhibited)',
        'serverDeleteProhibited (https://www.icann.org/epp#serverDeleteProhibited)',
        'serverTransferProhibited (https://www.icann.org/epp#serverTransferProhibited)',
        'serverUpdateProhibited (https://www.icann.org/epp#serverUpdateProhibited)'
    ],

    'dnssec': False,

    'name_servers': [
        'ns1.google.com',
        'ns2.google.com',
        'ns3.google.com',
        'ns4.google.com'
    ],

    'emails': [
        'abusecomplaints@markmonitor.com',
        'whoisrequest@markmonitor.com'
    ]
}
"""
