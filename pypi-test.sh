#! /bin/bash

DATE=$( date +%Y%m%d )

setupVersionNumberToday()
{
    VERSION="1" # we start with version 1, only breaking changes will increment the first digit

    # while preparing the test.pypi we increment the day sequence if needed,
    # only a last version actually later will get published to the actual pypi (non test)

    TODAY_SEQ=$(
        ls dist/*${DATE}*.whl 2>/dev/null |
        awk -F\- '{ print $2 }' |
        awk -F\. '{ print $3 }' |
        awk '{ if ($1 > a) { a = $1 }} END { print a }'
    )

    if [ -z "${TODAY_SEQ}" ]
    then
        TODAY_SEQ="1"
    else
        TODAY_SEQ=$(( TODAY_SEQ + 1))
    fi

    mkdir -p ./work/
    # keep track of the latest version string
    echo "${VERSION}.${DATE}.${TODAY_SEQ}" >./work/version
}

makeTomlFile()
{
    cat pyproject.toml-template |
    awk -vversion="${VERSION}" -vdate="${DATE}" -vseq="${TODAY_SEQ}" '
    /@VERSION@/  { sub(/@VERSION@/,version) }
    /@YYYYMMDD@/ { sub(/@YYYYMMDD@/,date) }
    /@SEQ@/      { sub(/@SEQ@/,seq) }
    { print }
    ' >pyproject.toml
}

buildDist()
{
    python -m build
    ls -l dist
}

uploadTwineTest()
{
    twine upload -r testpypi dist/*"${VERSION}.${DATE}.${TODAY_SEQ}"*
}

main()
{
    ./reformat-code.sh
    mypy --implicit-optional *.py
    mypy --implicit-optional whoisdomain

    setupVersionNumberToday
    makeTomlFile
    buildDist
    uploadTwineTest
}

main
