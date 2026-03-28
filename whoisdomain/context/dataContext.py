import logging
import os
from typing import (
    Any,
)

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class DataContext:
    def __init__(
        self,
        domain: str,
        hasLibTld: bool = False,
    ) -> None:
        self.originalDomain: str = domain  # the requested domain before cleanup
        self.hasLibTld = hasLibTld

        # the working domain splitted on '.' ,
        # may change as we try to find a one that gets a response from whois
        self.dList: list[str] = []
        self.domain: str = domain  # the working domain , may change after cleanup (e.g.www)

        self.tldString: str | None = None  # the detected toplevel 'aaa' or 'aaa.bbb'
        self.publicSuffixStr: str | None = None  # the detected public Suffix if we can import tld
        self.hasPublicSuffix: bool = False

        self.rawWhoisStr: str = ""  # the result string from whois cli before clean
        self.whoisStr: str = ""  # the result string from whois cli after clean

        self.data: dict[str, Any] = {}  # the data we need to build the domain object
        self.exeptionStr: str | None = None  # if we handle exceptions as result string instead of throw
        self.thisTld: dict[str, Any] = {}  # the dict of regex and info as defined by ZZ and parsed by TldInfo
        self.servers: list[str] = []  # extract whois servers from the whois output (may need --verbose on rfc1036/whois)
