#! /usr/bin/env python3

from typing import (
    List,
    Dict,
    Any,
    Optional,
)


class DataContext:
    def __init__(
        self,
        domain: str,
    ) -> None:
        self.originalDomain: str = domain  # the requested domain before cleanup
        self.domain: str = domain  # the working domain , may change after cleanup (e.g.www)

        # the working domain splitted on '.' ,
        # may change as we try to find a one that gets a response from whois
        self.dList: List[str] = []
        self.tldString: Optional[str] = None  # the detected toplevel 'aaa' or 'aaa.bbb'

        self.lastWhoisStr: str = ""  # the result string from whois cli before clean
        self.whoisStr: str = ""  # the result string from whois cli after clean

        self.data: Dict[str, Any] = {}  # the data we need to build the domain object
        self.exeptionStr: Optional[str] = None  # if we handle exceptions as result string instead of throw
        self.thisTld: Dict[str, Any] = {}  # the dict of regex and info as defined by ZZ and parsed by TldInfo
