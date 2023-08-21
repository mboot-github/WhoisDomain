import sys

from typing import (
    cast,
    Optional,
    List,
    Dict,
    # Tuple,
    Any,
)

from .exceptions import WhoisPrivateRegistry
from .exceptions import UnknownTld

from ._0_init_tld import filterTldToSupportedPattern
from ._0_init_tld import TLD_RE

from .doWhoisCommand import doWhoisAndReturnString

from .whoisParser import WhoisParser
from .domain import Domain
from .parameterContext import ParameterContext
from .lastWhois import updateLastWhois
from .dataContext import DataContext


class ProcessWhoisDomainRequest:
    def __init__(
        self,
        domain: str,
        pc: ParameterContext,
        dc: DataContext,
    ) -> None:
        self.domain = domain
        self.pc = pc
        self.dc = dc
        self.tldString: Optional[str] = None

    def setThisTldEntry(
        self,
        thisTld: Dict[str, str],
    ) -> None:
        self.thisTld = thisTld

    def _fromDomainStringToTld(
        self,
    ) -> Optional[List[str]]:
        def _internationalizedDomainNameToPunyCode(d: List[str]) -> List[str]:
            return [k.encode("idna").decode() or k for k in d]

        # Prep the domain ================
        self.domain = self.domain.lower().strip().rstrip(".")  # Remove the trailing dot to support FQDN.
        dList: List[str] = self.domain.split(".")
        if dList[0] == "www":
            dList = dList[1:]
        if len(dList) == 1:
            self.tldString = None
            return None

        if self.pc.verbose:
            print(f"from domain to list: {self.domain}, {dList}", file=sys.stderr)

        # Is it a supported domain =======
        self.tldString = filterTldToSupportedPattern(
            self.domain,
            dList,
            self.pc.verbose,
        )  # may raise UnknownTld

        if self.pc.verbose:
            print(f"filterTldToSupportedPattern returns tld: {self.tldString}", file=sys.stderr)

        # Internationalized domains: Idna translate
        if self.pc.internationalized:
            dList = _internationalizedDomainNameToPunyCode(dList)

        return dList

    def makeMessageForUnsupportedTld(
        self,
    ) -> Optional[str]:
        if self.pc.return_raw_text_for_unsupported_tld:
            return None

        a = f"The TLD {self.tldString} is currently not supported by this package."
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
            )

            # we will only return minimal data
            self.dc.data = {
                "tld": self.tldString,
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
        if self.thisTld.get("_privateRegistry"):
            if self.pc.simplistic is False:
                msg = "WhoisPrivateRegistry"
                raise WhoisPrivateRegistry(msg)
            return True
        return False

    def _doServerHintsForThisTld(
        self,
    ) -> None:
        # note _server hints currently are not passes down when using "extend", that may have been my error during the initial implementation
        # allow server hints using "_server" from the tld_regexpr.py file
        thisTldServer = self.thisTld.get("_server")
        if self.pc.server is None and thisTldServer:
            self.pc.server = thisTldServer

    def _doSlowdownHintForThisTld(
        self,
    ) -> int:
        self.pc.slow_down = self.pc.slow_down or 0

        slowDown = self.thisTld.get("_slowdown")
        if slowDown:
            if self.pc.slow_down == 0 and int(slowDown) > 0:
                self.pc.slow_down = int(slowDown)

        if self.pc.verbose and int(self.pc.slow_down):
            print(f"using _slowdown hint {self.pc.slow_down} for tld: {self.tldString}", file=sys.stderr)

        return int(self.pc.slow_down)

    def doOneLookup(
        self,
        # dList: List[str],
    ) -> Optional[Domain]:
        if self.dc.dList is None:
            return None

        try:
            # now use the cache interface to fetch the whois str from cli whois
            self.dc.whoisStr = doWhoisAndReturnString(
                dList=self.dc.dList,
                pc=self.pc,
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
        self.dc.lastWhoisStr = self.dc.whoisStr

        if self.pc.verbose:
            print("Raw: ", self.dc.whoisStr, file=sys.stderr)

        updateLastWhois(
            dList=self.dc.dList,
            whoisStr=self.dc.lastWhoisStr,
            pc=self.pc,
        )

        wp = WhoisParser(
            tldString=str(self.tldString),
            dList=self.dc.dList,
            pc=self.pc,
            dc=self.dc,
        )
        data, self.dc.whoisStr = wp.parse()

        if self.pc.verbose:
            print("Clean:", self.dc.whoisStr, file=sys.stderr)

        if isinstance(data, Domain):
            return data

        # do we have a result and does it have a domain name
        if data is None:
            return None

        self.dc.data = data
        if self.dc.data["domain_name"][0]:
            return Domain(
                pc=self.pc,
                dc=self.dc,
            )

        return None

    def processRequest(self) -> Optional[Domain]:
        dList: Optional[List[str]]

        # =================================================
        try:
            dList = self._fromDomainStringToTld()  # may raise UnknownTld
            if self.tldString is None:
                return None
        except Exception as e:
            if self.pc.simplistic is False:
                raise (e)

            self.dc.exeptionStr = "UnknownTld"
            return Domain(
                pc=self.pc,
                dc=self.dc,
            )

        # force mypy to process ok
        self.tldString = str(self.tldString)
        self.dc.dList = dList
        if self.dc.dList is None:
            return None

        # =================================================
        if self.tldString not in TLD_RE.keys():
            msg = self.makeMessageForUnsupportedTld()
            if msg is None:
                self._doUnsupportedTldAnyway()
                return Domain(
                    pc=self.pc,
                    dc=self.dc,
                )

            if self.pc.simplistic is False:
                raise UnknownTld(msg)

            self.dc.exeptionStr = msg  # was: self.dc.exeptionStr = "UnknownTld"
            return Domain(
                pc=self.pc,
                dc=self.dc,
            )

        # =================================================
        self.setThisTldEntry(cast(Dict[str, Any], TLD_RE.get(self.tldString)))

        if self._verifyPrivateRegistry():  # may raise WhoisPrivateRegistry
            msg = "This tld has either no whois server or responds only with minimal information"
            self.dc.exeptionStr = msg
            return Domain(
                pc=self.pc,
                dc=self.dc,
            )

        # =================================================
        self._doServerHintsForThisTld()
        self._doSlowdownHintForThisTld()

        # if the tld is a multi level we should not move further down than the tld itself
        # we currently allow progressive lookups until we find something:
        # so xxx.yyy.zzz will try both xxx.yyy.zzz and yyy.zzz
        # but if the tld is yyy.zzz we should only try xxx.yyy.zzz

        tldLevel = self.tldString.split(".")
        while len(self.dc.dList):
            result = self.doOneLookup()
            if result:
                return result

            if len(self.dc.dList) > (len(tldLevel) + 1):
                self.dc.dList = self.dc.dList[1:]  # strip one element from the front and try again
                if self.pc.verbose:
                    msg = f"try again with {self.dc.dList}, {len(self.dc.dList)}, {len(tldLevel) + 1}"
                    print(msg, file=sys.stderr)
                continue

            # no result or no domain but we can not reduce any further so we have None
            return None

        return None
