#! /bin/bash

VERSION=$( cat ./work/version )

main()
{
    ls -l ./dist/*${VERSION}* && {
        twine upload -r testpypi dist/*${VERSION}*
    }
}

main
