#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from https://github.com/maarten-boot/python-whois-extended

from whoisdomain._3_adjust import str_to_date

from typing import (
    List,
)

TEST_DATETIMES: List[str] = [
    "02-jan-2000",
    "02.02.2000",
    "01/06/2011",
    "2000-01-02",
    "2000.01.02",
    "2005/05/30",
    "31-01-2000",
    "01-31-2000",  # is ambivalent for all days <=12 could be interpreded as dd-mm-yyyy
    "20240405",
    "2000. 01. 31.",
    "aug-1996",
    "2002.09.19 13:00:00",
    "20110908 14:44:51",
    "2011-09-08 14:44:51",
    "19.09.2002 13:00:00",
    "24-Jul-2009 13:20:03 UTC",
    "24-Jul-2009 13:20:03",
    # '%d %b %Y %H:%M %Z',
    "2011/06/01 01:05:01 (+0900)",
    "2011/06/01 01:05:01",
    "Tue Jun 21 23:59:59 GMT 2011",
    "Tue Jun 21 23:59:59 2015",
    "Tue Dec 12 2000",
    "2007-01-26T19:10:31",
    "2007-01-26T19:10:31Z",
    "2019-11-12T19:15:55.283Z",
    "2011-03-30T19:36:27+0200",
    "2011-09-08T14:44:51.622265+03:00",
    "2011-09-08t14:44:51.622265",
    "2010-04-07 03:32:36 (GMT+0:00)",
    "2010-04-07 03:32:36 (GMT+00:00)",
    "21/09/2018 23:59:48",
    "2015-08-21 16:07:21+02",
    "2015-08-21 16:07:21+03",
    "2024-04-21 00:00:00 (UTC+8)",
]

for f in TEST_DATETIMES:
    try:
        str_to_date(f)
    except ValueError as err:
        print(f"{err} :: Unable to convert: '%s'" % f)
        raise
