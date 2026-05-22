# ruff: noqa: N815
import json
import logging
from dataclasses import asdict, dataclass
from typing import Any

log = logging.getLogger(__name__)


@dataclass(slots=True)
class ParameterContext:
    # currently no params are mandatory

    # if the whois command fails with code 1 still process the data returned as normal.
    ignore_returncode: bool = False

    # Don't use cache.
    force: bool = False

    # bla bla
    verbose: bool = False

    # cleanup lines starting with % and REDACTED FOR PRIVACY
    with_cleanup_results: bool = False

    # if true convert with internationalizedDomainNameToPunyCode()
    internationalized: bool = False

    # if reqested the full response is also returned.
    include_raw_whois_text: bool = False

    # as it says
    return_raw_text_for_unsupported_tld: bool = False

    # try to parse partial response when cmd timed out
    #  (stdbuf should be in PATH for best results)
    parse_partial_response: bool = False

    # when simplistic is true,
    #  we return null for most exceptions and dont pass info why we have no data.
    simplistic: bool = False

    # show redacted output default no redacted data is shown
    withRedacted: bool = False

    # specify the path to the cli whois you want to use.
    cmd: str = "whois"

    # specify the path to the cli whois you want to use.
    cache_file: str | None = None

    # use this whois server for making this query:
    #   Linux/Mac: 'whois -h <server> <domain>'
    #   Windows: 'whois.exe <domain> <server>'"
    server: str | None = None

    # Cache expiration time for given domain in seconds 60*60*48 (48 hours).
    cache_age: int = 172800

    # Time [s] it will wait after you query WHOIS database.
    slow_down: int = 0

    # timeout in seconds for the whois command to return a result.
    timeout: float = 30.0

    # allow auto install of sysinternals whois on windows if no whois found
    tryInstallMissingWhoisOnWindows: bool = False

    # The number of lines we consider a short response.
    shortResponseLen: int = 5

    # if lib 'tld' is installed add tld info based on get_tld(); fake the tld if needed
    withPublicSuffix: bool = False

    # try to extract the whois servers from the whois output (uses --verbose)
    extractServers: bool = False

    # strip https://icann.org/epp# from status response
    stripHttpStatus: bool = False

    # if set to true we skip the strip www action
    noIgnoreWww: bool = False

    # if set to true we only consult rdap
    rdapOnly: bool = False

    # if set to true we only consult whois
    whoisOnly: bool = False

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, s: str) -> "ParameterContext":
        return cls(**json.loads(s))


if __name__ == "__main__":
    pc = ParameterContext()
    print(asdict(pc))
