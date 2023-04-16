#! /bin/bash

rm -rf dist
python -m build
twine upload -r testpypi dist/*
