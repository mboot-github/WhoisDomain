#! /usr/bin/env bash
ENV="tmp/t1"
time=120
VERSION=$( cat ./work/version )

mkdir -p tmp
python3 -m venv ${ENV}
source ./${ENV}/bin/activate

sleep $time
while true
do
    pip install -i https://test.pypi.org/simple/ whoisdomain==${VERSION} && break
    echo "sleeping ${time} seconds to allow the freshly uploaded image to become available on test.pypi" >&2
done

WE_HAVE=$( whoisdomain -V )
echo "$WE_HAVE" >&2

[ "$WE_HAVE" == "$VERSION" ] && {
    whoisdomain -a
    rm -rf ${ENV}
    exit 0
}

exit 101
