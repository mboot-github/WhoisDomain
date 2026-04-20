import logging
import os

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class DummyCache:
    def __init__(
        self,
        *,
        verbose: bool = False,
    ) -> None:
        self.verbose = verbose

    def get(  # noqa: PLR6301
        self,
        keyString: str,  # noqa: ARG002
    ) -> str | None:
        return None

    def put(  # noqa: PLR6301
        self,
        keyString: str,  # noqa: ARG002
        data: str,
    ) -> str:
        return data
