#! /bin/bash

# look for differences after updates of the regexes

ls tmp/A/test-*.txt |
while read item
do
    b=$( basename $item )

    [ -f "tmp/B/$b" ] && {
        diff -q tmp/A/$b tmp/B/$b || {
            echo "## diff for $b"
            diff tmp/A/$b tmp/B/$b >tmp/diff-$b
        }
        continue
    }
    echo "## no file for $b"
done
