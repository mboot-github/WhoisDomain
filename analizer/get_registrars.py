#! /usr/bin/env python3

# import sys
import csv
import requests

from tld import get_tld
from urllib.parse import urlparse

from Typing import (
    List,
)

FILE_NAME: str = "registrar-ids-1.csv"
FILE_URL: str = f"https://www.iana.org/assignments/registrar-ids/{FILE_NAME}"


def getFileFromUrl(fileName: str, url: str) -> None:
    r = requests.get(
        url,
        allow_redirects=True,
    )
    open(
        fileName,
        "wb",
    ).write(
        r.content,
    )
    return fileName


def readCsvFile(fileName: str):
    result: List[List[str]] = []
    with open(fileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")

        line_count = 0
        for row in csv_reader:
            line_count += 1

            if line_count == 1:
                print(f"Column names: {row}")
                continue
            if row[2] in ["Reserved", "Terminated"]:
                continue
            result.append(row)
    return result


def xMain() -> None:
    fileName: str = getFileFromUrl(FILE_NAME, FILE_URL)
    result: List[List[str]] = readCsvFile(fileName)

    rdapList: List[str] = []
    hostList: List[str] = []
    tldList: List[str] = []
    fldList: List[str] = []

    for row in result:
        if row[3].strip() == "":
            continue

        rdap = row[3]

        if rdap not in rdapList:
            rdapList.append(rdap)

        parsed_uri = urlparse(rdap)
        host = parsed_uri.netloc
        if host not in hostList:
            hostList.append(host)

        res = get_tld(rdap, fail_silently=True, as_object=True)
        if res is None:
            continue

        tld = res.tld
        fld = res.fld

        if tld not in tldList:
            tldList.append(tld)
        if fld not in fldList:
            fldList.append(fld)

    for rdap in rdapList:
        print(rdap)

    print("# rdapList", len(rdapList))
    print("# hostList", len(hostList))
    print("# fldList", len(fldList))
    print("# tldList", len(tldList), tldList)


xMain()
