#! /usr/bin/env bash

set -x

time=60 # 1 minute

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

installFromTestPyPi()
{
    sleep $time
    while true
    do
        pip install -i https://test.pypi.org/simple/ ${WHAT}==${VERSION} && break
        echo "sleeping ${time} seconds to allow the freshly uploaded image to become available on test.pypi" >&2
    done
}

main()
{
    [ ! -f "${PACKAGE_FILE}" ] && {
        echo "$(basename $0) missing whl file ${PACKAGE_FILE}" >&2
        exit 101
    }
    makeVenv

    installFromTestPyPi

    local WE_HAVE=$( whoisdomain -V )
    echo "$WE_HAVE" >&2

    [ "$WE_HAVE" == "$VERSION" ] && {
        whoisdomain \
            -f testdata/DOMAINS.txt \
            --withPublicSuffix \
            --extractServers \
            --stripHttpStatus
    }

    # clean up the venv
    rm -rf ${ENV}
}

main
