# whoisdomain

  * A Python package for retrieving WHOIS information of DOMAIN'S ONLY.
  * Python 2.x IS NOT supported.
  * Currently no additional python packages need to be installed.

## Notes

  * This package will not support querying ip CIDR ranges or AS information
  * This was a copy of the original DanyCork 'whois'.
      * Significantly refactored in 2023.
      * The output is still compatible with DanyCork 'whois'

## Releases
I will start versioning at 1.x.x where the second item will be YYYYMMDD,
the third item will start from 1 and be only used if more than one update will have to be done in one day.

Versions `1.x.x` will keep the output compatible with Danny Cork until 2024-02-03 (February 2023)

  * Releases are avalable at: [Pypi](https://pypi.org/project/whoisdomain/)

Pypi releases can be installed with:

  * `pip install whoisdomain`


## Features
  * See: [Features](Features.md)

## Dependencies
  * please install also the command line "whois" of your distribution as this library parses the output of the "whois" cli command of your operating system

### Notes for Mac users
  * it has been observed that the default cli whois on Mac is showing each forward step in its output, this makes parsing the result very unreliable.
  * using a brew install whois will give in general better results.

## Docker release
  * See [Docker](Docker.md)

## Usage example
  * See [Usage](Usage.mf)

## whoisdomain
  * the cli `whoisdomain` is  documented in [whoisdomain-cli](whoisdomain-cli.md)

## ccTLD & TLD support

Most `tld's` are now autodetected via IANA root db, see the Analizer directory
and `make suggest`.

  * see the file: [tld_regexpr](./whoisdomain/tldDb/tld_regexpr.py)
  * for python use:  `whoisdomain.validTlds()`
  * for cli use `whoisdomain -S`

## Support
 * Python 3.x is supported for x >= 9
 * Python 2.x IS NOT supported.

## Author's
  * See: [Authors](Authors.md)

## Updates
  * see [Updates](Updates.md) for a full history of changes.
  * Only the latest update is mentioned here

### 1.20230906.1
  * introduce parsing based on functions, allow contextual search in splitted data and plain data, allow contextual search based on earlier result; fix a few tld to return the proper registrant string (not nic handle)
