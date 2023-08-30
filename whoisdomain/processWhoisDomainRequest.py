import sys

from typing import (
    cast,
    Optional,
    List,
    Dict,
    Any,
    Tuple,
)

from .exceptions import WhoisPrivateRegistry
from .exceptions import UnknownTld
from ._0_init_tld import filterTldToSupportedPattern
from ._0_init_tld import TLD_RE
from .doWhoisCommand import doWhoisAndReturnString
from .whoisParser import WhoisParser
from .domain import Domain
from .lastWhois import updateLastWhois

from .context.dataContext import DataContext
from .context.parameterContext import ParameterContext


class ProcessWhoisDomainRequest:
    def __init__(
        self,
        pc: ParameterContext,
        dc: DataContext,
    ) -> None:
        self.pc = pc
        self.dc = dc

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
        )  # may raise UnknownTld

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

    def _verifyPrivateRegistry(
        self,
    ) -> bool:
        # may raise WhoisPrivateRegistry
        # signal we know the tld but it has no whos or does not respond with any information
        if not self.dc.thisTld.get("_privateRegistry"):
            return False

        if self.pc.simplistic is False:
            msg = "WhoisPrivateRegistry"
            raise WhoisPrivateRegistry(msg)

        return True

    def _doServerHintsForThisTld(
        self,
    ) -> None:
        # note _server hints currently are not passes down when using "extend",
        # that may have been my error during the initial implementation
        # allow server hints using "_server" from the tld_regexpr.py file
        thisTldServer = self.dc.thisTld.get("_server")
        if self.pc.server is None and thisTldServer:
            self.pc.server = thisTldServer

    def _doSlowdownHintForThisTld(
        self,
    ) -> int:
        self.pc.slow_down = self.pc.slow_down or 0

        slowDown = self.dc.thisTld.get("_slowdown")
        if slowDown:
            if self.pc.slow_down == 0 and int(slowDown) > 0:
                self.pc.slow_down = int(slowDown)

        if self.pc.verbose and int(self.pc.slow_down):
            print(f"DEBUG: using _slowdown hint {self.pc.slow_down} for tld: {self.dc.tldString}", file=sys.stderr)

        return int(self.pc.slow_down)

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

        wp = WhoisParser(
            pc=self.pc,
            dc=self.dc,
        )
        data = wp.parse()

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
        if self.dc.tldString not in TLD_RE.keys():
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

        self.dc.thisTld = cast(Dict[str, Any], TLD_RE.get(self.dc.tldString))
        # thisTld is the result of TLD_RE (and ZZ), a dict with regex to match the whoisStr

        if self._verifyPrivateRegistry():  # may raise WhoisPrivateRegistry
            msg = "This tld has either no whois server or responds only with minimal information"
            self.dc.exeptionStr = msg
            result = Domain(
                pc=self.pc,
                dc=self.dc,
            )
            return result, finished

        self._doServerHintsForThisTld()
        self._doSlowdownHintForThisTld()

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
