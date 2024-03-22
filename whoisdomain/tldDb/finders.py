import os
import re
import logging

# re._MAXCACHE = 1

# pylint: disable=unused-argument
# import typing
from typing import (
    Dict,
    Any,
    List,
    Callable,
    Tuple,
)

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

PATTERN_CACHE: Dict[Tuple[str, int], Any] = {}


def make_pat(reStr: str, flags: int) -> Any:
    return re.compile(reStr, flags=flags)

    if (reStr, flags) in PATTERN_CACHE:
        pattern = PATTERN_CACHE[(reStr, flags)]
    else:
        pattern = re.compile(reStr, flags=flags)
        PATTERN_CACHE[(reStr, flags)] = pattern
    return pattern


def newLineSplit(
    ignoreCase: bool = True,
) -> Callable[[str], List[str]]:
    def xNewlineSplit(
        whoisStr: str,
        verbose: bool = False,
    ) -> Any:
        # split the incoming text on newlines \n\n
        reStr = r"\n\n"
        flags = re.IGNORECASE if ignoreCase else 0
        pattern = make_pat(reStr, flags)
        z = pattern.split(whoisStr)
        del pattern
        return z

    return xNewlineSplit


def R(
    reStr: str,
    ignoreCase: bool = True,
) -> Callable[[str, List[str], bool], List[str]]:
    # regular simple regex strings are converter with currying to functins to be called later
    def reFindAll(
        textStr: str,
        sData: List[str],
        verbose: bool = False,
    ) -> Any:
        flags = re.IGNORECASE if ignoreCase else 0  # NOFLAG is 3.11
        pattern = make_pat(reStr, flags)
        z = pattern.findall(textStr)
        del pattern
        return z

    return reFindAll


# def R2(reString: str) -> str:
#     # you could still only use strings, untested
#     return reString


def findFromToAndLookFor(
    fromStr: str,
    toStr: str,
    lookForStr: str,
    ignoreCase: bool = True,
    verbose: bool = False,
) -> Callable[[str, List[str], bool], List[str]]:
    # look for a particular string like R()
    # but limit the context we look in
    # to a specific sub section of the whois cli response
    # use currying to create a func that will be called later
    def xFindFromToAndLookFor(
        textStr: str,
        sData: List[str],
        verbose: bool = False,
    ) -> Any:
        flags = re.IGNORECASE if ignoreCase else 0  # NOFLAG is 3.11
        p1 = make_pat(fromStr, flags)
        s1 = p1.search(textStr)
        del p1

        msg = f"s1 {s1}, {fromStr}"
        log.debug(msg)

        if s1 is None:
            return []

        start = s1.start()
        t2 = textStr[start:]
        msg = f"fromStr {t2}"
        log.debug(msg)

        p2 = make_pat(toStr, flags)
        p3 = make_pat(lookForStr, flags)

        s2 = p2.search(t2)
        del p2
        if s2 is None:
            z = p3.findall(t2)
            del p3
            return z

        end = s2.end()
        t3 = t2[:end]
        msg = f"toStr {t3}"
        log.debug(msg)

        z = p3.findall(t3)
        del p3
        return z

    return xFindFromToAndLookFor


# pylint disable=pointless-string-statement
r"""
example look for in context: google.sk
look for Organization:\s*([^\n]*)\n
but limit that search (as Organization occurs multiple times) to the section between:
r"Domain registrant:" and "\n\n"

Domain registrant:            mmr-170347
Name:                         Domain Administrator
Organization:                 Google Ireland Holdings Unlimited Company
Organization ID:              369511
Phone:                        +353.14361000
Email:                        dns-admin@google.com
Street:                       70 Sir John Rogerson's Quay
City:                         Dublin
Postal Code:                  2
Country Code:                 IE
Authorised Registrar:         MARK-0292
Created:                      2019-06-07
Updated:                      2019-06-07


    findFromToAndLookFor(
        fromStr=r"Domain registrant:",
        toStr=r"\n\n",
        lookForStr=r"Organization:\s*([^\n]*)\n"
    )
test with: ./test2.py -v -d google.sk 2>2
"""  # pylint disable=pointless-string-statement


def findFromToAndLookForWithFindFirst(
    findFirst: str,
    fromStr: str,  # we will replace {} in fromStr with the result from findFirst
    toStr: str,
    lookForStr: str,
    ignoreCase: bool = True,
    verbose: bool = False,
) -> Callable[[str, List[str], bool], List[str]]:
    # look for a particular string like R() with find first
    #   then build a from ,to context using the result from findFirst (google.fr is a example)
    #     but limit the context we look in
    #       to a specific sub section of the whois cli response
    # use currying to create a func that will be called later
    def xFindFromToAndLookForWithFindFirst(
        textStr: str,
        sData: List[str],
        verbose: bool = False,
    ) -> List[str]:
        flags = re.IGNORECASE if ignoreCase else 0  # NOFLAG is 3.11

        ff = re.findall(findFirst, textStr, flags=flags)
        if ff is None or ff == []:
            return []

        ff2: str = str(ff[0].strip())  # only use the first element and clean it
        if ff2 == "":
            return []

        msg = f"we found: {ff2}, now combine with {fromStr}"
        log.debug(msg)

        fromStr2 = fromStr.replace(r"{}", ff2)
        s1 = re.search(fromStr2, textStr, flags=flags)

        msg = f"s1 {s1}, {fromStr}"
        log.debug(msg)

        if s1 is None:
            return []

        start = s1.start()
        t2 = textStr[start:]
        msg = f"fromStr {t2}"
        log.debug(msg)

        s2 = re.search(toStr, t2, flags=flags)
        if s2 is None:
            return re.findall(lookForStr, t2, flags=flags)

        end = s2.end()
        t3 = t2[:end]
        msg = f"toStr {t3}"
        log.debug(msg)

        return re.findall(lookForStr, t3, flags=flags)

    return xFindFromToAndLookForWithFindFirst


# example google.at
# find me registrant aand with that data
# find me a section that has nic-hdl:\s*<registrant>
# from that section extract organization:


def findInSplitedLookForHavingFindFirst(
    findFirst: str,
    lookForStr: str,
    extract: str,
    ignoreCase: bool = True,
    verbose: bool = False,
) -> Callable[[str, List[str], bool], List[str]]:
    # requires splitted data
    def xfindInSplitedLookForHavingFindFirst(
        textStr: str,
        sData: List[str],
        verbose: bool = False,
    ) -> List[str]:
        flags = re.IGNORECASE if ignoreCase else 0  # NOFLAG is 3.11

        ff = re.findall(findFirst, textStr, flags=flags)
        if ff is None or ff == []:
            return []

        ff2: str = str(ff[0].strip())  # only use the first element and clean it
        if ff2 == "":
            return []

        lookForStr2 = lookForStr.replace(r"{}", ff2)
        for section in sData:
            s1 = re.findall(lookForStr2, section, flags=flags)
            if s1:
                return re.findall(extract, section, flags=flags)
        return []

    return xfindInSplitedLookForHavingFindFirst
