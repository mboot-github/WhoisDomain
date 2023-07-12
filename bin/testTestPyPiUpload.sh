#! /usr/bin/env bash

set -x

time=300

VERSION=$( cat ./work/version )
WHAT="whoisdomain"
PACKAGE_FILE="dist/${WHAT}-${VERSION}-py3-none-any.whl"
TMPDIR="tmp"
ENV="${TMPDIR}/t1"

makeVenv()
{
    mkdir -p ${TMPDIR}
    rm -rf ${TMPDIR}/t1

    python3 -m venv ${ENV}
    source ./${ENV}/bin/activate
}

installFromDistWhl()
{
    pip3 install dist/${WHAT}-${VERSION}-py3-none-any.whl
}

installFromTestPyPi()
{
    sleep $time
    while true
    do
        pip install -i https://test.pypi.org/simple/ ${WHAT}==${VERSION} && break
        echo "sleeping ${time} seconds to allow the freshly uploaded image to become available on test.pypi" >&2
    done
}

getInstalledVersion()
{
    # after install
    WE_HAVE=$( whoisdomain -V )
    echo "$WE_HAVE" >&2
}

testAllIfCorrectVersion()
{
    [ "$WE_HAVE" == "$VERSION" ] && {
        whoisdomain -f testdata/DOMAINS.txt
        # clean up the venv
        rm -rf ${ENV}
        exit 0
    }
}

main()
{
    [ -f "${PACKAGE_FILE}" ] && {
        makeVenv
        # installFromDistWhl
        installFromTestPyPi
        getInstalledVersion
        testAllIfCorrectVersion
    }

    echo "$(basename $0) Failed" >&2
    exit 101
}

main
