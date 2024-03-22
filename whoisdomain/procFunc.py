# python3

import sys
import errno
from typing import (
    Tuple,
    Any,
    Dict,
)

from socket import error as SocketError

import multiprocessing as mp

from .context.parameterContext import ParameterContext

# from .domain import Domain

MAX_CLIENT_RUNS_BEFORE_EXIT = 1000


class ProcFunc:
    def __init__(self, ctx: Any = None) -> None:
        if ctx is None:
            ctx = mp.get_context("spawn")
        self.ctx = ctx

    def startProc(self, f: Any, max_requests: int) -> Tuple[Any, Any]:
        # start the whole parent part
        self.parent_conn, self.child_conn = mp.Pipe()

        self.proc = self.ctx.Process(
            target=f,
            args=(self.child_conn, max_requests),
        )

        self.proc.start()
        self.child_conn.close()

        return self.proc, self.parent_conn

    def oneItem(
        self,
        domain: str,
        pc: ParameterContext,
    ) -> Any:
        jStr = pc.toJson()

        request: Dict[str, Any] = {
            "domain": domain,
            "pc": jStr,
        }

        # request -> reply: remote
        if pc.verbose:
            print("OneItem:SEND:", request, file=sys.stderr)
        self.parent_conn.send(request)

        reply = self.parent_conn.recv()
        if pc.verbose:
            print("OneItem:RECEIVE:", reply, file=sys.stderr)

        if reply["status"] is True:
            result = reply["result"]
            # possibly re convert this into a Domain object.
            return result

        raise Exception(reply["exception"])

    def makeHandler(
        self,
        f: Any,
        max_requests: int = MAX_CLIENT_RUNS_BEFORE_EXIT,
    ) -> Any:
        self.startProc(f, max_requests)

        def inner_func(
            domain: str,
            pc: ParameterContext,
        ) -> Any:
            nonlocal self
            try:
                return self.oneItem(domain, pc)
            except SocketError as e:
                if e.errno != errno.ECONNRESET:
                    print(f"restart process {e}", file=sys.stderr)
                    raise

                self.startProc(f, max_requests)
                return self.oneItem(domain, pc)

        return inner_func
