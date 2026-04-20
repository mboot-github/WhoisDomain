import logging
import os
import time

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class SimpleCacheBase:
    def __init__(
        self,
        *,
        verbose: bool = False,
        cache_max_age: int = (60 * 60 * 48),
    ) -> None:
        self.verbose = verbose
        self.memCache: dict[str, tuple[float, str]] = {}
        self.cache_max_age: int = cache_max_age

    def put(
        self,
        keyString: str,
        data: str,
    ) -> str:
        # store the currentTime and data tuple (time, data)
        self.memCache[keyString] = (
            int(time.time()),
            data,
        )
        return data

    def get(
        self,
        keyString: str,
    ) -> str | None:
        cData = self.memCache.get(keyString)
        if cData is None:
            return None

        t = time.time()
        hasExpired = cData[0] < (t - self.cache_max_age)
        if hasExpired is True:
            return None

        return cData[1]
