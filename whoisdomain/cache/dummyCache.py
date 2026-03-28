import logging
import os

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class DummyCache:
    def __init__(
        self,
        verbose: bool = False,
    ) -> None:
        self.verbose = verbose

    def get(
        self,
        keyString: str,
    ) -> str | None:
        return None

    def put(
        self,
        keyString: str,
        data: str,
    ) -> str:
        return data
