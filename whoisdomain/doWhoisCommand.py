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

from .simpleCacheBase import SimpleCacheBase
from .simpleCacheWithFile import SimpleCacheWithFile

from typing import (
    # Dict,
    List,
    Optional,
    # Tuple,
    Any,
)

from .parameterContext import ParameterContext


IS_WINDOWS: bool = platform.system() == "Windows"

STDBUF_OFF_CMD: List[str] = []
if not IS_WINDOWS and shutil.which("stdbuf"):
    STDBUF_OFF_CMD = ["stdbuf", "-o0"]

# actually also whois uses cache, so if you really dont want to use cache
# you should also pass the --force-lookup flag (on linux)

CACHE_STUB: Any = None


def _testWhoisPythonFromStaticTestData(
    dList: List[str],
    pc: ParameterContext,
) -> str:
    domain = ".".join(dList)
    testDir = os.getenv("TEST_WHOIS_PYTHON")
    pathToTestFile = f"{testDir}/{domain}/input"
    if os.path.exists(pathToTestFile):
        with open(pathToTestFile, mode="rb") as f:  # switch to binary mode as that is what Popen uses
            # make sure the data is treated exactly the same as the output of Popen
            return f.read().decode(errors="ignore")

    raise WhoisCommandFailed("")


def _tryInstallMissingWhoisOnWindows(
    pc: ParameterContext,
) -> None:
    """
    Windows 'whois' command wrapper
    https://docs.microsoft.com/en-us/sysinternals/downloads/whois
    """
    folder = os.getcwd()
    copy_command = r"copy \\live.sysinternals.com\tools\whois.exe " + folder
    if pc.verbose:
        print("downloading dependencies", file=sys.stderr)
        print(copy_command, file=sys.stderr)

    subprocess.call(
        copy_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    )


def _makeWhoisCommandToRun(
    dList: List[str],
    pc: ParameterContext,
) -> List[str]:
    domain = ".".join(dList)

    whList: List[str] = [pc.cmd]
    if " " in pc.cmd:
        whList = pc.cmd.split(" ")

    if IS_WINDOWS:
        if pc.cmd == "whois":  # only if the use did not specify what whois to use
            k: str = "whois.exe"
            if os.path.exists(k):
                pc.cmd = os.path.join(".", k)
            else:
                find = False
                paths = os.environ["path"].split(";")
                for path in paths:
                    wpath = os.path.join(path, k)
                    if os.path.exists(wpath):
                        pc.cmd = wpath
                        find = True
                        break

                if not find:
                    _tryInstallMissingWhoisOnWindows(
                        pc=pc,
                    )
        whList = [pc.cmd]

        if pc.server:
            return whList + ["-v", "-nobanner", domain, pc.server]
        return whList + ["-v", "-nobanner", domain]

    # not windows
    if pc.server:
        return whList + [domain, "-h", pc.server]
    return whList + [domain]


def _execute_whois_query(
    dList: List[str],
    pc: ParameterContext,
) -> str:
    # if getenv[TEST_WHOIS_PYTON] fake whois by reading static data from a file
    # this wasy we can actually implemnt a test run with known data in and expected data out
    if os.getenv("TEST_WHOIS_PYTHON"):
        return _testWhoisPythonFromStaticTestData(
            dList,
            pc=pc,
        )

    cmd = _makeWhoisCommandToRun(
        dList=dList,
        pc=pc,
    )
    if pc.verbose:
        print(cmd, pc.cmd, file=sys.stderr)

    if pc.slow_down:
        # slow down before so we can force individual domains at a slower tempo
        time.sleep(pc.slow_down)

    # LANG=en is added to make the ".jp" output consist across all environments
    p = subprocess.Popen(
        # STDBUF_OFF_CMD needed to not lose data on kill
        STDBUF_OFF_CMD + cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={"LANG": "en"} if dList[-1] in ".jp" else None,
    )

    try:
        r = p.communicate(timeout=pc.timeout,)[
            0
        ].decode(errors="ignore")
    except subprocess.TimeoutExpired:
        # Kill the child process & flush any output buffers
        p.kill()
        r = p.communicate()[0].decode(errors="ignore")
        # In most cases whois servers returns partial domain data really fast
        # after that delay occurs (probably intentional) before returning contact data.
        # Add this option to cover those cases
        if not pc.parse_partial_response or not r:
            raise WhoisCommandTimeout(f"timeout: query took more then {pc.timeout} seconds")

    if pc.verbose:
        print(r, file=sys.stderr)

    if pc.ignore_returncode is False and p.returncode not in [0, 1]:
        if "fgets: Connection reset by peer" in r:
            return r.replace("fgets: Connection reset by peer", "")

        if "connect: Connection refused" in r:
            return r.replace("connect: Connection refused", "")

        if pc.simplistic:
            return r

        raise WhoisCommandFailed(r)

    return r


# PUBLIC

# future: use decorator for caching
def doWhoisAndReturnString(
    dList: List[str],
    pc: ParameterContext,
) -> str:
    global CACHE_STUB

    # here you can override caching, if someone else already defined CACHE_STUB by this time, we use their caching
    if CACHE_STUB is None:
        CACHE_STUB = SimpleCacheWithFile(
            verbose=pc.verbose,
            cacheFilePath=pc.cache_file,
            cacheMaxAge=pc.cache_age,
        )

    # allways test CACHE_STUB is a subclass of SimpleCacheBase
    assert isinstance(CACHE_STUB, SimpleCacheBase), Exception("CACHE_STUB - must inherit from SimpleCacheBase")

    keyString = ".".join(dList)

    oldData: Optional[str] = CACHE_STUB.cacheGetData(keyString)

    needFreshData: bool = False

    if pc.force is True:
        needFreshData = True

    if oldData is None:
        needFreshData = True

    hasExpired: Optional[bool] = CACHE_STUB.cacheExpired(keyString)
    if hasExpired is None:
        needFreshData = True

    if hasExpired is True:
        needFreshData = True

    if needFreshData is False:
        return str(oldData)

    newData: str = _execute_whois_query(
        dList=dList,
        pc=pc,
    )

    # populate a fresh cache entry and save if needed
    CACHE_STUB.cachePut(keyString, newData)

    return newData
