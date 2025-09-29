#! /bin/bash

doIt()
{
    black --line-length 160 .
    pylama --ignore "C0114,C0115"--max-line-length 160 *.py bin/*.py whoisdomain/ |
    awk '
    /__init__/ && / W0611/ { next }
#    / W0401 / { next }
    / E203 / { next } # E203 whitespace before ':' [pycodestyle]
    / C901 / { next } # C901 <something> is too complex (<nr>) [mccabe]
    { print }
    '
}

main()
{
    doIt

    mypy --strict --no-incremental *.py
    mypy --strict --no-incremental bin/*.py
    mypy --strict --no-incremental whoisdomain
}

main
