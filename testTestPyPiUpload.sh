#! /usr/bin/env bash

mkdir -p tmp
python3 -m venv tmp/t1
source ./tmp/t1/bin/activate
pip install -i https://test.pypi.org/simple/ whoisdomain

whoisdomain -a
