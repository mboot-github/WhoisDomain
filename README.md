# whoisdomain

A Python package for retrieving WHOIS information of domains.

This package will not support querying ip CIDR ranges or AS information

A copy of the original DanyCork 'whois',
I will start versioning at 1.x.x where the second item will be YYYYMMDD,
the third will start from 1 and be only used if more than one update will have to be done in one day.

## Features
 * Python wrapper for the "whois" cli command of your operating system.
 * Simple interface to access parsed WHOIS data for a given domain.
 * Able to extract data for all the popular TLDs (com, org, net, biz, info, pl, jp, uk, nz,  ...).
 * Query a WHOIS server directly instead of going through an intermediate web service like many others do.
 * Works with Python >= 3.6
 * All dates as datetime objects.
 * Possibility to cache results.
 * Verbose output on stderr during debugging to see how the internal functions are doing their work
 * raise a exception on Quota ecceeded type responses
 * raise a exception on PrivateRegistry tld's where we know the tld and know we don't know anything
 * allow for optional cleaning the response before extracting information
 * optionally allow IDN's to be translated to Punycode

## Dependencies
  * please install also the command line "whois" of your distribution
  * this library parses the output of the "whois" cli command of your operating system

## Usage example

Install the cli `whois` of your operating system if it is not present already,
e.g 'apt install whois' or 'yum install whois'

```
sudo yum install whois
$pip install whoisdomain
python
>>> import whoisdomain as whois
>>> d = whois.query('google.com')
>>> print(d.__dict__)
{'name': 'google.com', 'tld': 'com', 'registrar': 'MarkMonitor, Inc.', 'registrant_country': 'US', 'creation_date': datetime.datetime(1997, 9, 15, 9, 0), 'expiration_date': None, 'last_updated': datetime.datetime(2019, 9, 9, 17, 39, 4), 'status': 'clientUpdateProhibited (https://www.icann.org/epp#clientUpdateProhibited)', 'statuses': ['clientDeleteProhibited (https://www.icann.org/epp#clientDeleteProhibited)', 'clientTransferProhibited (https://www.icann.org/epp#clientTransferProhibited)', 'clientUpdateProhibited (https://www.icann.org/epp#clientUpdateProhibited)', 'serverDeleteProhibited (https://www.icann.org/epp#serverDeleteProhibited)', 'serverTransferProhibited (https://www.icann.org/epp#serverTransferProhibited)', 'serverUpdateProhibited (https://www.icann.org/epp#serverUpdateProhibited)'], 'dnssec': False, 'name_servers': ['ns1.google.com', 'ns2.google.com', 'ns3.google.com', 'ns4.google.com'], 'registrant': 'Google LLC', 'emails': ['abusecomplaints@markmonitor.com', 'whoisrequest@markmonitor.com']}

>>> print(d.name)
google.com

>>> print (d.expiration_date)
None

>>> print (d.creation_date)
1997-09-15 09:00:00
```

## ccTLD & TLD support
see the file: ./whoisdomain/tld_regexpr.py
or call whoisdomain.validTlds()

## Support
 * Python 3.x is supported for x >= 6
 * Python 2.x IS NOT supported.

## Author's
  * this is a rename copy of original work done in: https://github.com/DannyCork/python-whois
