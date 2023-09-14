#! /usr/bin/env python3

# import sys
import os
import json
import logging

from typing import (
    Optional,
    # Tuple,
)

from .simpleCacheBase import (
    SimpleCacheBase,
)

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class SimpleCacheWithFile(SimpleCacheBase):
    cacheFilePath: Optional[str] = None

    def __init__(
        self,
        verbose: bool = False,
        cacheFilePath: Optional[str] = None,
        cacheMaxAge: int = (60 * 60 * 48),
    ) -> None:
        super().__init__(verbose=verbose, cacheMaxAge=cacheMaxAge)
        self.cacheFilePath = cacheFilePath

    def _fileLoad(
        self,
    ) -> None:
        if self.cacheFilePath is None:
            return

        if not os.path.isfile(self.cacheFilePath):
            return

        with open(self.cacheFilePath, "r") as f:
            try:
                self.memCache = json.load(f)
            except Exception as e:
                msg = f"ignore json load err: {e}"
                log.error(msg)

    def _fileSave(
        self,
    ) -> None:
        if self.cacheFilePath is None:
            return

        with open(self.cacheFilePath, "w") as f:
            json.dump(self.memCache, f)

    def put(
        self,
        keyString: str,
        data: str,
    ) -> str:
        super().put(keyString=keyString, data=data)
        self._fileSave()
        return data

    def get(
        self,
        keyString: str,
    ) -> Optional[str]:
        self._fileLoad()
        return super().get(keyString=keyString)


if __name__ == "__main__":
    pass
