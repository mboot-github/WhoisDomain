#!  /usr/bin/env python3

import subprocess
import time
import sys
import os
import platform
import shutil

from .exceptions import (
    WhoisCommandFailed,
    WhoisCommandTimeout,
)

from typing import (
    List,
)

from .parameterContext import ParameterContext


class WhoisCliInterface:
    pc: ParameterContext
    dList: List[str]

    def __init__(
        self,
        dList: List[str],
        pc: ParameterContext,
    ):
        self.dList = dList
        self.pc = pc
        self.IS_WINDOWS: bool = platform.system() == "Windows"

        self.STDBUF_OFF_CMD: List[str] = []
        if not self.IS_WINDOWS and shutil.which("stdbuf"):
            self.STDBUF_OFF_CMD = ["stdbuf", "-o0"]

    def _testWhoisPythonFromStaticTestData(self) -> str:
        domain = ".".join(self.dList)
        testDir = os.getenv("TEST_WHOIS_PYTHON")
        pathToTestFile = f"{testDir}/{domain}/input"
        if os.path.exists(pathToTestFile):
            with open(pathToTestFile, mode="rb") as f:  # switch to binary mode as that is what Popen uses
                # make sure the data is treated exactly the same as the output of Popen
                return f.read().decode(errors="ignore")

        raise WhoisCommandFailed("")

    def _tryInstallMissingWhoisOnWindows(self) -> None:
        """
        Windows 'whois' command wrapper
        https://docs.microsoft.com/en-us/sysinternals/downloads/whois
        """
        folder = os.getcwd()
        copy_command = r"copy \\live.sysinternals.com\tools\whois.exe " + folder
        if self.pc.verbose:
            print("downloading dependencies", file=sys.stderr)
            print(copy_command, file=sys.stderr)

        subprocess.call(
            copy_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
        )

    def _makeWhoisCommandToRun(self) -> List[str]:
        domain = ".".join(self.dList)

        whList: List[str] = [self.pc.cmd]
        if " " in self.pc.cmd:
            whList = self.pc.cmd.split(" ")

        if self.IS_WINDOWS:
            if self.pc.cmd == "whois":  # only if the use did not specify what whois to use
                k: str = "whois.exe"
                if os.path.exists(k):
                    self.pc.cmd = os.path.join(".", k)
                else:
                    find = False
                    paths = os.environ["path"].split(";")
                    for path in paths:
                        wpath = os.path.join(path, k)
                        if os.path.exists(wpath):
                            self.pc.cmd = wpath
                            find = True
                            break

                    if not find:
                        self._tryInstallMissingWhoisOnWindows()
            whList = [self.pc.cmd]

            if self.pc.server:
                return whList + ["-v", "-nobanner", domain, self.pc.server]
            return whList + ["-v", "-nobanner", domain]

        # not windows
        if self.pc.server:
            return whList + [domain, "-h", self.pc.server]
        return whList + [domain]

    def execute_whois_query(self) -> str:
        # if getenv[TEST_WHOIS_PYTON] fake whois by reading static data from a file
        # this wasy we can actually implemnt a test run with known data in and expected data out
        if os.getenv("TEST_WHOIS_PYTHON"):
            return self._testWhoisPythonFromStaticTestData()

        cmd = self._makeWhoisCommandToRun()
        if self.pc.verbose:
            print(cmd, self.pc.cmd, file=sys.stderr)

        if self.pc.slow_down:
            # slow down before so we can force individual domains at a slower tempo
            time.sleep(self.pc.slow_down)

        # LANG=en is added to make the ".jp" output consist across all environments
        p = subprocess.Popen(
            # STDBUF_OFF_CMD needed to not lose data on kill
            self.STDBUF_OFF_CMD + cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env={"LANG": "en"} if self.dList[-1] in ".jp" else None,
        )

        try:
            r = p.communicate(timeout=self.pc.timeout,)[
                0
            ].decode(errors="ignore")
        except subprocess.TimeoutExpired:
            # Kill the child process & flush any output buffers
            p.kill()
            r = p.communicate()[0].decode(errors="ignore")
            # In most cases whois servers returns partial domain data really fast
            # after that delay occurs (probably intentional) before returning contact data.
            # Add this option to cover those cases
            if not self.pc.parse_partial_response or not r:
                raise WhoisCommandTimeout(f"timeout: query took more then {self.pc.timeout} seconds")

        if self.pc.verbose:
            print(r, file=sys.stderr)

        if self.pc.ignore_returncode is False and p.returncode not in [0, 1]:
            if "fgets: Connection reset by peer" in r:
                return r.replace("fgets: Connection reset by peer", "")

            if "connect: Connection refused" in r:
                return r.replace("connect: Connection refused", "")

            if self.pc.simplistic:
                return r

            raise WhoisCommandFailed(r)

        return r
