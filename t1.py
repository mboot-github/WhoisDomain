#! /usr/bin/env python3

import os

from typing import Any

from whoisdomain import ProcFunc


def remoteFunc(
    conn: Any,
    max_requests: int,
) -> None:
    n = 0
    while True:
        n += 1
        try:
            request = conn.recv()
            reply = f"The name of the given continent is: {request}. Says process {os.getpid()} with count {n}"
            conn.send(reply)
        except EOFError as e:
            _ = e
            exit(0)

        if n >= max_requests:
            break


def main() -> None:
    names = [
        "Africa",
        "America",
        "Antarctica",
        "Atlantis",
        "Australie",
        "Azia",
        "Europe",
        "Heaven",
        "Hell",
        "Mu",
        "Nirvana",
        "Purgatory",
    ]

    restart_after_count: int = 50
    pf: ProcFunc = ProcFunc()
    f = pf.makeHandler(remoteFunc, restart_after_count)

    n = 0
    while True:
        n += 1
        for item in names:
            v = f(item)
            print(v)
        if n >= 26:
            break

    f = pf.makeHandler(remoteFunc, restart_after_count)
    n = 0
    while True:
        n += 1
        for item in names:
            v = f(item)
            print(v)
        if n >= 26:
            break


if __name__ == "__main__":
    main()
