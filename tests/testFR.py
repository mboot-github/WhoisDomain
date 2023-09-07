#! /usr/bin/env python3.9

sys.path.append("..")
import whoisdomain

w_fr = whoisdomain.query("sfr.fr")
w_com = whoisdomain.query("sfr.com")

if w_fr is None or w_com is None:
    exit(101)

print("TEST registrant organization")
assert w_fr.registrant == "SOCIETE FRANCAISE DU RADIOTELEPHONE - SFR"

# print("TEST that .com and .fr give same results")
assert w_fr.registrant == w_com.registrant
