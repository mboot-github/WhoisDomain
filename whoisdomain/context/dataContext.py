#! /usr/bin/env python3

from typing import (
    List,
    Dict,
    Any,
    Optional,
)

# from .parameterContext import ParameterContext


class DataContext:
    def __init__(
        self,
        domain: str,
    ) -> None:
        self.originalDomain: str = domain
        self.domain: str = domain

        self.dList: List[str] = []
        self.tldString: Optional[str] = None

        self.lastWhoisStr: str = ""
        self.whoisStr: str = ""

        self.data: Dict[str, Any] = {}
        self.exeptionStr: Optional[str] = None
        self.thisTld: Dict[str, Any] = {}
