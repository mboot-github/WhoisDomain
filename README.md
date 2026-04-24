# whoisdomain [![Spectra Assure Community Badge](https://secure.software/pypi/badge/whoisdomain)](https://secure.software/pypi/packages/whoisdomain)

- A Python package for retrieving WHOIS information of DOMAIN'S ONLY.
- Python >=3.10
- requirements
    - whodap>=0.1.16 [![Spectra Assure Community Badge](https://secure.software/pypi/badge/whodap)](https://secure.software/pypi/packages/whodap)
    - tld>=0.13.2 [![Spectra Assure Community Badge](https://secure.software/pypi/badge/tld)](https://secure.software/pypi/packages/tld/0.13.2/tld-0.13.2-py2.py3-none-any.whl)
- v1 uses only whois and will be moved to maintenance only
- v2 will use whodap to first retrieve info with rdap and if no data is available try the classic whois approach

  * This package will not support querying ip CIDR ranges or AS information.
  * This was a copy of the original DanyCork 'whois'.
      * Significantly refactored in 2023 (v1).
      * RDAP adding in 2026 (v2).
      * The v1 output is still compatible with DanyCork 'whois'.
      * the v2 will move away from strict compatibility.

---

## Notes

### A) https://en.wikipedia.org/wiki/WHOIS

On January 19, 2023, ICANN opened voting on a global amendment to all its registry and registrar agreements. In it they defined an RDAP Ramp-Up Period of 180 days starting with the effectiveness of this amendment. 360 days after this period is defined as the WHOIS Services Sunset Date, after which it is not a requirement for registries and registrars to offer a WHOIS service and instead only an RDAP service is required. All voting thresholds were met within the 60 day voting period and the amendment was approved by the ICANN Board. The date for WHOIS Sunset for gTLDs was set as 28 January 2025.[47]

### B) **memory leak**

**2024-02-05: The current whoisdomain has a memory leak.**

The memory leak is not relevant for short running use
but when using whoisdomain in long running programs
you should be aware that each query will increase its memory use.


### Versioning

  * I will start versioning at 1.x.x
     * the second item will be YYYYMMDD,
     * the third item will start from 1 and be only used if more than one update will have to be done in one day.

Versions `1.x.x` will keep the output compatible with Danny Cork.

Versions `2.x.x` will add a dependency on whodap and use rdab based whois data before consulting historical whois.

### Releases

  * Releases are avalable at: [Pypi](https://pypi.org/project/whoisdomain/)

Pypi releases can be installed with:

  * `pip install whoisdomain`

---

## Features
  * See: [Features](docs/Features.md)

## Dependencies
  * please install also the command line "whois" of your distribution as this library parses the output of the "whois" cli command of your operating system

### Notes for Mac users
  * it has been observed that the default cli whois on Mac is showing each forward step in its output, this makes parsing the result very unreliable.
  * using a brew install whois will give in general better results.

## Docker release
  * See [Docker](docs/Docker.md)

## Usage example
  * See [Usage](docs/Usage.md)

## whoisdomain
  * the cli `whoisdomain` is  documented in [whoisdomain-cli](docs/whoisdomain-cli.md)

## ccTLD & TLD support

Most `tld's` are now autodetected via IANA root db, see the Analizer directory
and `make suggest`.

  * see the file: [tld_regexpr](./whoisdomain/tldDb/tld_regexpr.py)
  * for python use:  `whoisdomain.validTlds()`
  * for cli use `whoisdomain -S`

---

## Support
 * Python 3.x is supported for x >= 10

## Author's
  * See: [Authors](docs/Authors.md)

---

## Updates
  * see [Updates](docs/Updates.md) for a full history of changes.

## in progress

- switch to minimal version 3.10
- update gitgub-action lint (mypy) to use `setup-python@v6` and `checkout@v6`
- start working on v2 with rdap first
