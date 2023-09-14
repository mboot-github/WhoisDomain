#! /usr/bin/env bash

# here we never actually query with whois but read existing data
# this way we can verify that the parser still works identical and produces the same output as we had before
#
prepPath()
{
    local xpath="$1"
    TestDataDir=$( realpath "$xpath" )

    # signal whois module that we are testing,
    # forces the library not tho use the cli whois but to read data from:
    # $TestDataDir/<domain>/input
    export TEST_WHOIS_PYTHON="$TestDataDir"
    echo "## SET:  TEST_WHOIS_PYTHON='$TestDataDir'"
}

get_testdomains()
{
    ls "$TestDataDir" |
    grep -v ".sh" |
    grep -v "*.txt"
}

testOneDomain()
{
    domain="$1"
    [ ! -d "$TestDataDir/$domain" ] && return

    # echo "$TestDataDir/$domain/output"
    grep Try "$TestDataDir/$domain/output" >/dev/null && return
    grep Exception "$TestDataDir/$domain/output" >/dev/null && return

    echo "testing: $domain"
    ./test2.py -d "$domain" >"$TestDataDir/$domain/test.out"

    local out="$TestDataDir/$domain/diff.out"
    diff "$TestDataDir/$domain/output" "$TestDataDir/$domain/test.out" >"${out}"
    [ -s "${out}" ] && {
        echo "### parse testing: '$domain' shows diff"
        cat "${out}"
    }
}

main()
{
    prepPath "testdata" # set a default
    [ -d "$1" ] && { # if a argument and is a dir use that for testing
        prepPath "$1"
    }

    get_testdomains |
    while read line
    do
        local z=$(basename $line)
        testOneDomain $z
    done
    exit 0
}

main $*
