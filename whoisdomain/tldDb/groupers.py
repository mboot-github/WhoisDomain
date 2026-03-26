# import re
# import sys
import logging
import os
from collections.abc import Callable

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


COM_LIST: list[str] = [
    r"\nRegistrar",
    r"\nRegistrant",
    r"\nTech",
    r"\nAdmin",
    r"\nDomain",
    r"\nName Server:",
]


def groupFromList(aList: list[str]) -> Callable[[str], dict[str, str]]:
    def xgroupFromList(
        whoisStr: str,
        *,
        verbose: bool = False,
    ) -> dict[str, str]:
        result: dict[str, str] = {}
        # iterate over the lines of whoisStr
        #   for key each item in the list
        #       create a empty list
        #       store the list under key
        #       see if there is a match ans append matched lines to the list
        # what = r"\n\n"
        return result

    return xgroupFromList
