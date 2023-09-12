#! /bin/bash

# find tld with whois.nic.<tld> but without _test and add nic.<tld> as the test
# currently only the simple oneliners

XPATH="./whoisdomain/tldDb/tld_regexpr.py"

cat "${XPATH}" |
awk '
/^ZZ\["/ && /whois\.nic\./ && /}/ {
    if( $0 ~ /"_test"/ ) {
        next
    }
    print
}
'
