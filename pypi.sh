#! /bin/bash

version=$( cat ./work/version )

ls -l ./dist/*${version}* && {
    twine upload dist/*${version}*
}
