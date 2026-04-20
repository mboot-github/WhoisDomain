import json
import logging
import os
import pathlib

from .simpleCacheBase import (
    SimpleCacheBase,
)

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class SimpleCacheWithFile(SimpleCacheBase):
    cache_file_path: str | None = None

    def __init__(
        self,
        *,
        verbose: bool = False,
        cache_file_path: str | None = None,
        cache_max_age: int = (60 * 60 * 48),
    ) -> None:
        super().__init__(verbose=verbose, cache_max_age=cache_max_age)
        self.cache_file_path = cache_file_path

    def _fileLoad(
        self,
    ) -> None:
        if self.cache_file_path is None:
            return

        if not pathlib.Path(self.cache_file_path).is_file():
            return

        with pathlib.Path(self.cache_file_path).open(encoding="utf-8") as f:
            try:
                self.memCache = json.load(f)
            except ValueError as e:
                msg = f"ignore json load err: {e}"
                log.exception(msg)

    def _fileSave(
        self,
    ) -> None:
        if self.cache_file_path is None:
            return

        with pathlib.Path(self.cache_file_path).open("w", encoding="utf-8") as f:
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
    ) -> str | None:
        self._fileLoad()
        return super().get(keyString=keyString)
