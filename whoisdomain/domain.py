import logging
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import datetime

from .context.dataContext import DataContext
from .context.parameterContext import ParameterContext
from .handleDateStrings import str_to_date

log = logging.getLogger(__name__)


class Domain:
    def __init__(
        self,
        pc: ParameterContext,
        dc: DataContext,
    ) -> None:
        _ = pc
        _ = dc

        self.name: str = ""
        self.tld: str = ""
        self.registrar: str = ""
        self.registrant: str = ""
        self.registrant_country: str = ""
        self.status: str = ""

        self.abuse_contact: str = ""
        self.admin: str = ""

        self.statuses: list[str] = []
        self.emails: list[str] = []
        self.name_servers: list[str] = []

        self.dnssec: bool = False

        self.updated_date: datetime.datetime | None = None
        self.expiration_date: datetime.datetime | None = None
        self.creation_date: datetime.datetime | None = None
        self._rdap_: dict[str, Any] = {}

    @classmethod
    def _cleanupArray(
        cls,
        data: list[str],
    ) -> list[str]:
        if "" in data:
            index = data.index("")
            data.pop(index)
        return data

    @classmethod
    def cleanStatus(
        cls,
        item: str,
    ) -> str:
        if "icann.org/epp#" in item:
            res = re.split(r"\s*\(?https?://(www\.)?icann\.org/epp#\s*", item)
            if res and res[0]:
                return res[0].strip()

        if "identitydigital.au/get-au/whois-status-codes#" in item:
            res = re.split(r"\s*https://identitydigital\.au/get-au/whois-status-codes#\s*", item)
            if res and res[0]:
                return res[0].strip()

        return item

    def _doNameservers(
        self,
        *,
        dc: DataContext,
    ) -> None:
        tmp: list[str] = []
        for x in dc.data["name_servers"]:
            if isinstance(x, str):
                tmp.append(x.strip().lower())
                continue

            # not a string but an array
            tmp.extend(y.strip().lower() for y in x)

        for x in tmp:
            xx = x.strip(" .")  # remove any leading or trailing spaces and/or dots
            if xx:
                if " " in xx:
                    xx, _ = xx.split(" ", 1)
                    xx = xx.strip(" .")

                xx = xx.lower()
                if xx not in self.name_servers:
                    self.name_servers.append(xx)

        self.name_servers = sorted(self.name_servers)

    def _doStatus(
        self,
        pc: ParameterContext,
        dc: DataContext,
    ) -> None:
        self.status = dc.data["status"][0].strip()

        if pc.stripHttpStatus:
            self.status = self.cleanStatus(self.status)

        # sorted added to get predictable output during test
        # deduplicate results with set comprehension {}

        self.statuses = sorted(
            {s.strip() for s in dc.data["status"]},
        )
        if "" in self.statuses:
            self.statuses = self._cleanupArray(self.statuses)

        if pc.stripHttpStatus:
            z = []
            for item in self.statuses:
                xitem = self.cleanStatus(item)
                z.append(xitem)
            self.statuses = z

    def _doOptionalFields(
        self,
        data: dict[str, Any],
    ) -> None:
        # optional fields

        if "owner" in data:
            self.owner = data["owner"][0].strip()

        if "abuse_contact" in data:
            self.abuse_contact = data["abuse_contact"][0].strip()

        if "reseller" in data:
            self.reseller = data["reseller"][0].strip()

        if "registrant" in data:
            if "registrant_organization" in data:
                self.registrant = data["registrant_organization"][0].strip()
            else:
                self.registrant = data["registrant"][0].strip()

        if "admin" in data:
            self.admin = data["admin"][0].strip()

        if "emails" in data:
            # sorted added to get predictable output during test
            # list(set(...))) to deduplicate results

            self.emails = sorted(
                {s.strip() for s in data["emails"]},
            )
            if "" in self.emails:
                self.emails = self._cleanupArray(self.emails)

    def _parseData(
        self,
        pc: ParameterContext,
        dc: DataContext,
    ) -> None:
        # process mandatory fields that we expect always to be present
        # even if we have None or ''
        self.registrar = dc.data["registrar"][0].strip()
        self.registrant_country = dc.data["registrant_country"][0].strip()

        # date time items
        self.creation_date = str_to_date(dc.data["creation_date"][0], tld=self.tld)
        self.expiration_date = str_to_date(dc.data["expiration_date"][0], tld=self.tld)
        self.last_updated = str_to_date(dc.data["updated_date"][0], tld=self.tld)

        self.dnssec = bool(dc.data["DNSSEC"])
        self._doStatus(pc, dc)
        self._doNameservers(dc=dc)

        # optional fields
        self._doOptionalFields(dc.data)

    def from_whodap_dict(
        self,
        d: dict[str, Any],
    ) -> None:
        for name, value in d.items():
            super().__setattr__(name, value)

    def init(
        self,
        pc: ParameterContext,
        dc: DataContext,
    ) -> None:
        if pc.include_raw_whois_text and dc.whoisStr is not None:
            self.text = dc.whoisStr

        if dc.exeptionStr is not None:
            self._exception = dc.exeptionStr
            return

        if dc.data == {}:
            return

        msg = f"{dc.data}"
        log.debug(msg)

        k = "domain_name"
        if k in dc.data:
            self.name = dc.data["domain_name"][0].strip().lower()

        k = "tld"
        if k in dc.data:
            self.tld = dc.data[k].lower()

        if pc.withPublicSuffix and dc.hasPublicSuffix:
            self.public_suffix: str = str(dc.publicSuffixStr)

        if pc.extractServers:
            self.servers = dc.servers
            self.server = ""
            if self.servers:
                self.server = self.servers[-1]

        if pc.return_raw_text_for_unsupported_tld is True:
            return

        self._parseData(pc, dc)
