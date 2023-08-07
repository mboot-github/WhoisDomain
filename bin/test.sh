#! /usr/bin/env bash

# signal whois module that we are testing, this reads data from testdata/<domain>/in
prepPath()
{
    local xpath="$1"
    TestDataDir=$( realpath "$xpath" )
    export TEST_WHOIS_PYTHON="$TestDataDir"
}

get_testdomains()
{
    ls "$TestDataDir" |
    grep -v ".sh"
}

testOneDomain()
{
    domain="$1"
    [ ! -d "$TestDataDir/$domain" ] && return

    echo "testing: $domain"
    ./test2.py -d "$domain" >"$TestDataDir/$domain/test.out"

    diff "$TestDataDir/$domain/output" "$TestDataDir/$domain/test.out" |
    tee "$TestDataDir/$domain/diff.out"
}

testOneDomain2()
{
    domain="$1"
    [ ! -d "$TestDataDir/$domain" ] && return

    echo "testing: $domain"
    ./test2.py -T -d "$domain" >"$TestDataDir/$domain/test.out2"

    diff "$TestDataDir/$domain/output" "$TestDataDir/$domain/test.out2" |
    tee "$TestDataDir/$domain/diff.out2"
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
        testOneDomain $(basename $line)
        testOneDomain2 $(basename $line)
    done
}

main $*
