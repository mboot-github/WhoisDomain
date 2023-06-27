#! /bin/bash

VERSION=$( cat ./work/version )

ls -l ./dist/*${VERSION}* && {
    twine upload --verbose dist/*${VERSION}*
}
