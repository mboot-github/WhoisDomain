#!  /usr/bin/env python3

# import sys

# from .simpleCacheBase import SimpleCacheBase
from .simpleCacheWithFile import SimpleCacheWithFile

from typing import (
    # Dict,
    List,
    Optional,
    # Tuple,
    Any,
)

from .parameterContext import ParameterContext
from .whoisCliInterface import WhoisCliInterface

# actually also whois uses cache, so if you really dont want to use cache
# you should also pass the --force-lookup flag (on linux)

CACHE_STUB: Any = None


def _initDefaultCache(
    pc: ParameterContext,
) -> Any:
    global CACHE_STUB

    # here you can override caching, if someone else already defined CACHE_STUB by this time, we use their caching
    if CACHE_STUB is None:
        # if no cache defined init the default cache (optional with file storage based on pc)
        CACHE_STUB = SimpleCacheWithFile(
            verbose=pc.verbose,
            cacheFilePath=pc.cache_file,
            cacheMaxAge=pc.cache_age,
        )

    # allways test CACHE_STUB is a subclass of SimpleCacheBase
    # if pc.withVerifyCacheStubType:
    #   assert isinstance(CACHE_STUB, SimpleCacheBase), Exception("CACHE_STUB - must inherit from SimpleCacheBase")

    return CACHE_STUB


def _getNewDataForKey(
    dList: List[str],
    pc: ParameterContext,
) -> str:
    wci = WhoisCliInterface(
        dList=dList,
        pc=pc,
    )
    return wci.executeWhoisQueryOrReturnFileData()


# TODO: future: can we use decorator for caching?
def doWhoisAndReturnString(
    dList: List[str],
    pc: ParameterContext,
) -> str:
    cache = _initDefaultCache(pc)
    keyString = ".".join(dList)

    if pc.force is False:
        oldData: Optional[str] = cache.get(keyString)
        if oldData is not None:
            return str(oldData)

    newData = _getNewDataForKey(dList=dList, pc=pc)
    cache.put(keyString, newData)

    return newData
