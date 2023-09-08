#! /usr/bin/env python3.9

import sys
sys.path.append("..")
import whoisdomain

w_fr = whoisdomain.query("sfr.fr")
w_com = whoisdomain.query("sfr.com")

if w_fr is None or w_com is None:
    print("NO DATA FOUND")
    exit(101)

print("TEST registrant organization: will fail if test fails")
assert w_fr.registrant == "SOCIETE FRANCAISE DU RADIOTELEPHONE - SFR"

print("TEST that .com and .fr give same results")
assert w_fr.registrant == w_com.registrant
