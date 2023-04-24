#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from: https://github.com/maarten-boot/python-whois-extended

import sys

from typing import (
    Optional,
    # Dict,
    List,
    # Any,
)


import whoisdomain as whois

DOMAINS: str = """
google.com
www.fsdfsdfsdfsd.google.com
google.org
google.net
google.pl
google.co
google.co.uk
google.jp
google.co.jp
google.de
google.cc
google.ru
google.us
google.eu,whois.markmonitor.com
google.me
google.be
google.biz
google.info
google.it
google.cz
google.fr
google.lv
google.kz
google.by
google.am
google.com.ua
google.kg
google.help
google.tv
google.link
google.com.sg
e2e4.online,whois.nic.ru
napaster.name,whois.nic.ru
XN--C1AAY4A.XN--P1AI
гугл.рф
nic.pw
nic.bid,whois.nic.bid
nic.host,whois.nic.host
nic.online,whois.nic.online
nic.party,whois.nic.party
nic.pro,whois.nic.pro
nic.review,whois.nic.review
nic.site,whois.nic.site
nic.space,whois.nic.space
nic.top,whois.nic.top
nic.website,whois.nic.website
nic.win,whois.nic.win
whois.aero
test.taxi
test.foundation
nic.ir
test.technology
test.im
nic.co.ua
nic.travel
google.ee
nic.company
nic.delivery
nic.services
nic.systems
nic.network
nic.cl
nic.company
nic.in
test.com.br
nic.ge,whois.nic.ge
nic.рус
whois.twnic.net.tw
nic.онлайн
"""


def query(
    domain: str,
    host: Optional[str] = None,
) -> None:

    print("")
    print("-" * 80)
    print("Domain: {0}, host: {1}".format(domain, host))

    timout = 30  # seconds
    try:
        w = whois.query(
            domain,
            server=host,
            ignore_returncode=True,
            verbose=False,
            internationalized=True,
            include_raw_whois_text=False,
            timeout=timout,
        )
        if w:
            wd = w.__dict__
            for k, v in wd.items():
                print('%20s\t"%s"' % (k, v))
        else:
            print("None")
            print("\n", whois.get_last_raw_whois_data())
    except Exception as e:
        print(e)


def parse(data: str) -> None:
    if "," not in data:
        query(data)
        return

    dList: List[str] = data.split(",")

    if len(dList) == 1:
        query(dList[0])
        return

    if len(dList) == 2:
        query(dList[0], dList[1])
        return


def main() -> None:
    if len(sys.argv) > 1:
        domains = sys.argv[1:]
    else:
        domains = DOMAINS.split("\n")

    for data in domains:
        if data:
            parse(data)


if __name__ == "__main__":
    main()
