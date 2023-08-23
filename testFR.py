#! /usr/bin/env python3.9

import whoisdomain

w_fr = whoisdomain.query("sfr.fr")
w_com = whoisdomain.query("sfr.com")

print("TEST registrant organization")
assert w_fr.registrant == "SOCIETE FRANCAISE DU RADIOTELEPHONE - SFR"

# print("TEST that .com and .fr give same results")
assert w_fr.registrant == w_com.registrant
