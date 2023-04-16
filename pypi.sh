#! /bin/bash

rm -rf dist
python -m build
twine upload dist/*
