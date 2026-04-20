import logging
import os

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class WhoisExceptionError(Exception):
    # make all other exeptions based on a generic exception
    pass


class UnknownTldError(WhoisExceptionError):
    pass


class FailedParsingWhoisOutputError(WhoisExceptionError):
    pass


class WhoisQuotaExceededError(WhoisExceptionError):
    pass


class UnknownDateFormatError(WhoisExceptionError):
    pass


class WhoisCommandFailedError(WhoisExceptionError):
    pass


class WhoisPrivateRegistryError(WhoisExceptionError):
    # also known as restricted : see comments at the bottom in tld_regexpr.py
    # almost no info is returned or there is no cli whois server at all:
    # see: https://www.iana.org/domains/root/db/<tld>.html
    pass


class WhoisCommandTimeoutError(WhoisExceptionError):
    pass
