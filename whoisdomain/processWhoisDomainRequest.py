import sys

from typing import (
    Optional,
    List,
    Dict,
    Tuple,
)

from .exceptions import WhoisPrivateRegistry
from ._0_init_tld import filterTldToSupportedPattern
from .doWhoisCommand import doWhoisAndReturnString
from .doParse import do_parse
from .domain import Domain
from .parameterContext import ParameterContext
from .lastWhois import updateLastWhois


class ProcessWhoisDomainRequest:
    def __init__(
        self,
        domain: str,
        pc: ParameterContext,
    ) -> None:
        self.domain = domain
        self.pc = pc

    def setThisTldEntry(self, thisTld: Dict[str, str]) -> None:
        self.thisTld = thisTld

    def setThisTldSring(self, tldString: str) -> None:
        self.tldString = tldString

    def _fromDomainStringToTld(
        self,
    ) -> Tuple[str, Optional[str], Optional[List[str]]]:
        def _internationalizedDomainNameToPunyCode(d: List[str]) -> List[str]:
            return [k.encode("idna").decode() or k for k in d]

        self.domain = self.domain.lower().strip().rstrip(".")  # Remove the trailing dot to support FQDN.

        dList: List[str] = self.domain.split(".")
        if self.pc.verbose:
            print(dList, file=sys.stderr)

        if dList[0] == "www":
            dList = dList[1:]

        if len(dList) == 1:
            return self.domain, None, None

        tldString: str = filterTldToSupportedPattern(
            self.domain,
            dList,
            self.pc.verbose,
        )  # may raise UnknownTld
        if self.pc.verbose:
            print(f"filterTldToSupportedPattern returns tld: {tldString}", file=sys.stderr)

        if self.pc.internationalized:
            dList = _internationalizedDomainNameToPunyCode(dList)

        if self.pc.verbose:
            print(tldString, dList, file=sys.stderr)

        return self.domain, tldString, dList

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
        dList: List[str],
    ) -> Optional[Domain]:
        # we will not hunt for possible valid first level domains as we have no actual feedback
        self.pc.include_raw_whois_text = True
        whoisStr = doWhoisAndReturnString(
            dList=dList,
            pc=self.pc,
        )

        # we will only return minimal data
        data = {
            "tld": self.tldString,
            "domain_name": [],
        }
        data["domain_name"] = [".".join(dList)]  # note the fields are default all array, except tld
        self.pc.return_raw_text_for_unsupported_tld = True

        return Domain(
            data=data,
            pc=self.pc,
            whoisStr=whoisStr,
        )

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
        tldString: str,
        dList: List[str],
    ) -> Optional[Domain]:

        try:
            whoisStr = doWhoisAndReturnString(
                dList=dList,
                pc=self.pc,
            )
        except Exception as e:
            if self.pc.simplistic:
                return Domain(
                    data={},
                    pc=self.pc,
                    whoisStr=None,
                    exeptionStr=f"{e}",
                )

            raise e

        updateLastWhois(
            dList=dList,
            whoisStr=whoisStr,
            pc=self.pc,
        )

        data = do_parse(
            whoisStr=whoisStr,
            tldString=tldString,
            dList=dList,
            pc=self.pc,
        )

        if isinstance(data, Domain):
            return data

        # do we have a result and does it have a domain name
        if data and data["domain_name"][0]:
            return Domain(
                data=data,
                pc=self.pc,
                whoisStr=whoisStr,
            )
        return None
