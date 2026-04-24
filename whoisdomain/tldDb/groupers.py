# import re
# import sys
import logging

log = logging.getLogger(__name__)


COM_LIST: list[str] = [
    r"\nRegistrar",
    r"\nRegistrant",
    r"\nTech",
    r"\nAdmin",
    r"\nDomain",
    r"\nName Server:",
]


# def groupFromList(
#    aList: list[str],
# ) -> Callable[[str], dict[str, str]]:
#    def xgroupFromList(
#        whoisStr: str,
#    ) -> dict[str, str]:
#        result: dict[str, str] = {}
#        return result
#
#    return xgroupFromList
