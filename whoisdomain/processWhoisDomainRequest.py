import sys

from typing import (
    Optional,
    List,
    Tuple,
)

# from .exceptions import WhoisPrivateRegistry
from .exceptions import UnknownTld

from .context.dataContext import DataContext
from .context.parameterContext import ParameterContext

from .helpers import filterTldToSupportedPattern
from .helpers import get_TLD_RE

from .doWhoisCommand import doWhoisAndReturnString
from .whoisParser import WhoisParser
from .domain import Domain
from .lastWhois import updateLastWhois


class ProcessWhoisDomainRequest:
    def __init__(
        self,
        pc: ParameterContext,
        dc: DataContext,
        parser: WhoisParser,
    ) -> None:
        self.pc = pc
        self.dc = dc
        self.parser: WhoisParser = parser

    def _analyzeDomainStringAndValidate(
        self,
    ) -> None:
        def _internationalizedDomainNameToPunyCode(d: List[str]) -> List[str]:
            return [k.encode("idna").decode() or k for k in d]

        # Prep the domain ================
        self.dc.domain = self.dc.domain.lower().strip().rstrip(".")  # Remove the trailing dot to support FQDN.
        self.dc.dList = self.dc.domain.split(".")

        if len(self.dc.dList) == 0:
            self.dc.tldString = None
            self.dc.dList = []
            return

        if self.dc.dList[0] == "www":
            self.dc.dList = self.dc.dList[1:]

        if len(self.dc.dList) == 0:
            self.dc.tldString = None
            self.dc.dList = []
            return

        # we currently do not support raw tld's so we cannot lookup 'com' for example
        if len(self.dc.dList) == 1:
            self.dc.tldString = None
            self.dc.dList = []
            return

        # Is it a supported domain =======
        self.dc.tldString = filterTldToSupportedPattern(
            self.dc.domain,
            self.dc.dList,
            self.pc.verbose,
        )

        if self.dc.tldString is None:
            # if not fail
            tld = f"{self.dc.dList[-1]}"
            a = f"The TLD {tld} is currently not supported by this package."
            b = "Use validTlds() to see what toplevel domains are supported."
            msg = f"{a} {b}"
            raise UnknownTld(msg)

        # Internationalized domains: Idna translate
        if self.pc.internationalized:
            self.dc.dList = _internationalizedDomainNameToPunyCode(self.dc.dList)

    def makeMessageForUnsupportedTld(
        self,
    ) -> Optional[str]:
        if self.pc.return_raw_text_for_unsupported_tld:
            return None

        a = f"The TLD {self.dc.tldString} is currently not supported by this package."
        b = "Use validTlds() to see what toplevel domains are supported."
        msg = f"{a} {b}"
        return msg

    def _doUnsupportedTldAnyway(
        self,
    ) -> None:
        if self.dc.dList is not None:
            # we will not hunt for possible valid first level domains as we have no actual feedback
            self.pc.include_raw_whois_text = True

            # now use the cache interface to fetch the whois str from cli whois
            self.dc.whoisStr = doWhoisAndReturnString(
                dList=self.dc.dList,
                pc=self.pc,
                dc=self.dc,
            )

            # we will only return minimal data
            self.dc.data = {
                "tld": self.dc.tldString,
                "domain_name": [],
            }

            z: str = ".".join(self.dc.dList)
            self.dc.data["domain_name"] = [z]  # note the fields are default all array, except tld
            self.pc.return_raw_text_for_unsupported_tld = True

    def doOneLookup(
        self,
    ) -> Optional[Domain]:
        if self.pc.verbose:
            print(f"DEBUG: ### lookup: tldString: {self.dc.tldString}; dList: {self.dc.dList}", file=sys.stderr)

        if self.dc.dList is None:  # mainly to please mypy
            return None

        try:
            # now use the cache interface to fetch the whois str from cli whois
            self.dc.whoisStr = doWhoisAndReturnString(
                dList=self.dc.dList,
                pc=self.pc,
                dc=self.dc,
            )
        except Exception as e:
            if self.pc.simplistic is False:
                raise e

            self.dc.exeptionStr = f"{e}"
            return Domain(
                pc=self.pc,
                dc=self.dc,
            )

        self.dc.whoisStr = str(self.dc.whoisStr)

        if self.pc.verbose:
            print("DEBUG: Raw: ", self.dc.whoisStr, file=sys.stderr)

        self.dc.lastWhoisStr = self.dc.whoisStr  # keep the original whois string for reference
        updateLastWhois(
            dList=self.dc.dList,
            whoisStr=self.dc.lastWhoisStr,
            pc=self.pc,
        )

        self.parser.init()
        data = self.parser.parse()

        if self.pc.verbose:
            print("DEBUG: Clean:", self.dc.whoisStr, file=sys.stderr)

        if data is None:
            return None

        if isinstance(data, Domain):
            return data

        # do we have a result and does it have a domain name
        self.dc.data = data
        if self.dc.data["domain_name"][0]:
            return Domain(
                pc=self.pc,
                dc=self.dc,
            )

        return None

    def prepRequest(self) -> Tuple[Optional[Domain], bool]:
        result: Optional[Domain] = None
        finished: bool = True

        try:
            self._analyzeDomainStringAndValidate()  # may raise UnknownTld
            if self.dc.tldString is None:
                return result, finished
        except Exception as e:
            if self.pc.simplistic is False:
                raise (e)

            self.dc.exeptionStr = "UnknownTld"
            result = Domain(
                pc=self.pc,
                dc=self.dc,
            )
            return result, finished

        # force mypy to process ok
        self.dc.tldString = str(self.dc.tldString)
        if self.dc.dList is []:
            return None, True

        # =================================================
        if self.dc.tldString not in get_TLD_RE().keys():
            msg = self.makeMessageForUnsupportedTld()
            if msg is None:
                self._doUnsupportedTldAnyway()
                result = Domain(
                    pc=self.pc,
                    dc=self.dc,
                )
                return result, finished

            if self.pc.simplistic is False:
                raise UnknownTld(msg)

            self.dc.exeptionStr = msg  # was: self.dc.exeptionStr = "UnknownTld"
            result = Domain(
                pc=self.pc,
                dc=self.dc,
            )
            return result, finished

        # find my compiled info under key: tld and use {} as the default
        # self.dc.thisTld = get_TLD_RE().get(self.dc.tldString, {})
        self.parser.getThisTld(self.dc.tldString)

        if self.parser.verifyPrivateRegistry():  # may raise WhoisPrivateRegistry
            msg = "This tld has either no whois server or responds only with minimal information"
            self.dc.exeptionStr = msg
            result = Domain(
                pc=self.pc,
                dc=self.dc,
            )
            return result, finished

        self.parser.doServerHintsForThisTld()
        self.parser.doSlowdownHintForThisTld()

        return None, False

    def processRequest(self) -> Optional[Domain]:
        result, finished = self.prepRequest()
        if finished is True:
            return result

        # if the tld is a multi level we should not move further down than the tld itself
        # we currently allow progressive lookups until we find something:
        # so xxx.yyy.zzz will try both xxx.yyy.zzz and yyy.zzz
        # but if the tld is yyy.zzz we should only try xxx.yyy.zzz

        # self.dc.tldString is now a supported <tld> and never changes
        # self.dc.dList is the cleaned up domain query in list form:
        # so ".".join(self.dc.dList) would be like: aaa.<tld> or perhaps aaa.bbb.<tld>
        # and may change if we find no data in cli whois

        tldLevel: List[str] = str(self.dc.tldString).split(".")
        while len(self.dc.dList) > len(tldLevel):
            result = self.doOneLookup()
            if result:
                return result

            self.dc.dList = self.dc.dList[1:]  # strip one element from the front and try again

        return None
