import logging
from typing import Any

logger = logging.getLogger(__name__)


class DataResponse:  # noqa: B903
    status: bool  # if status is True we have data else a message
    data: Any
    message: str

    def __init__(
        self,
        *,
        status: bool = False,
        data: Any = None,
        message: str = "",
    ) -> None:
        self.status = status
        self.data = data
        self.message = message
