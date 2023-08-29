#! /usr/bin/env bash

time=120

ENV="tmp/t1"
VERSION=$( cat ./work/version )
WHAT="whoisdomain"
PACKAGE_FILE="dist/${WHAT}-${VERSION}-py3-none-any.whl"

makeVenv()
{
    mkdir -p tmp
    rm -rf tmp/t1
    python3 -m venv ${ENV}
    source ./${ENV}/bin/activate
}

installFromDistWhl()
{
    pip3 install dist/${WHAT}-${VERSION}-py3-none-any.whl
}

getInstalledVersion()
{
    # after install
    WE_HAVE=$( $WHAT -V )
    echo "$WE_HAVE" >&2
}

testSimpleIfCorrectVersion()
{
    [ "$WE_HAVE" == "$VERSION" ] && {
        $WHAT -f testdata/DOMAINS.txt
        rm -rf ${ENV}
        exit 0
    }
}

testAllIfCorrectVersion()
{
    [ "$WE_HAVE" == "$VERSION" ] && {
        $WHAT -a # run a complete test cycle on all domains
        rm -rf ${ENV}
        exit 0
    }
}

main()
{
    [ -f "${PACKAGE_FILE}" ] && {
        makeVenv
        installFromDistWhl
        getInstalledVersion
        testSimpleIfCorrectVersion

        [ "$1" == "full" ] && {
            testAllIfCorrectVersion
        }
    }

    echo "$(basename $0) Failed" >&2
    exit 101
}

main $@
