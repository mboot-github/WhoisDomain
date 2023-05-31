#! /usr/bin/env bash

TMPDIR="./tmp/A"
TMPDIR="./tmp/B"

CMD="./test2.py"
HOST=""

mkdir -p "${TMPDIR}"
NH="${TMPDIR}/nohost.txt"

getHost()
{
    local domain="$1"

    HOST=""
    for j in meta google nic
    do
        local d="${j}.${domain}"
        host -t soa "${d}" && {
            HOST="$d"
            return 0
        }
    done
    HOST=""
}

main()
{
    >"${NH}"

    "${CMD}" -S |
    while read domain
    do
        local f="${TMPDIR}/test-${domain}.txt"
        [ -f "${f}" ] && {
            echo "exists: $f" >&2
            continue
        }

        getHost "${domain}"
        [ -z "${HOST}" ] && {
            echo "## no host for domain: '${domain}'" |
            tee -a "${NH}"
            continue
        }

        "${CMD}" -d "${HOST}" |
        tee "${f}"
    done
}

main 2>2 |
tee 1
