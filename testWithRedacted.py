#! /usr/bin/env python3

import whoisdomain as whois

domain = "meta.alsace"
d = whois.query(domain, withRedacted=True)
if d:
    print(d.__dict__)
else:
    print(None)
