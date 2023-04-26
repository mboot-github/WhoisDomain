#! /usr/bin/env bash
ENV="tmp/t1"
time=60
VERSION=$( cat ./work/version )

mkdir -p tmp
python3 -m venv ${ENV}
source ./${ENV}/bin/activate

while true
do
    echo "sleeping ${time} seconds to allow the freshly uploaded image to become available on test.pypi"
    sleep $time

    pip install -i https://test.pypi.org/simple/ whoisdomain==${VERSION} && break
done

whoisdomain -a
rm -rf ${ENV}
