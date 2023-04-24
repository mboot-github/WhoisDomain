# whoisdomain

A Python package for retrieving WHOIS information of DOMAIN'S ONLY.

This package will not support querying ip CIDR ranges or AS information

This is a copy of the original DanyCork 'whois'.

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
 * optional specify the whois command on query(...,cmd="whois") as in: https://github.com/gen1us2k/python-whois/
 * the module is now 'mypy --strict' clean
 * the module now also exports a cli command domainwhois

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
{'name': 'google.com', 'tld': 'com', 'registrar': 'MarkMonitor, Inc.', 'registrant_country': 'US', 'creation_date': datetime.datetime(1997, 9, 15, 9, 0), 'expiration_date': datetime.datetime(2028, 9, 13, 9, 0), 'last_updated': datetime.datetime(2019, 9, 9, 17, 39, 4), 'status': 'clientUpdateProhibited (https://www.icann.org/epp#clientUpdateProhibited)', 'statuses': ['clientDeleteProhibited (https://www.icann.org/epp#clientDeleteProhibited)', 'clientTransferProhibited (https://www.icann.org/epp#clientTransferProhibited)', 'clientUpdateProhibited (https://www.icann.org/epp#clientUpdateProhibited)', 'serverDeleteProhibited (https://www.icann.org/epp#serverDeleteProhibited)', 'serverTransferProhibited (https://www.icann.org/epp#serverTransferProhibited)', 'serverUpdateProhibited (https://www.icann.org/epp#serverUpdateProhibited)'], 'dnssec': False, 'name_servers': ['ns1.google.com', 'ns2.google.com', 'ns3.google.com', 'ns4.google.com'], 'registrant': 'Google LLC', 'emails': ['abusecomplaints@markmonitor.com', 'whoisrequest@markmonitor.com']}
>>> print (d.expiration_date)
2028-09-13 09:00:00

>>> print(d.name)
google.com

>>> print (d.creation_date)
1997-09-15 09:00:00
```

# example test2.py
```
./test2.py -d google.com

test domain: <<<<<<<<<< google.com >>>>>>>>>>>>>>>>>>>>
name               str               'google.com'
tld                str               'com'
registrar          str               'MarkMonitor, Inc.'
registrant_country str               'US'
creation_date      datetime.datetime 1997-09-15 09:00:00
expiration_date    datetime.datetime 2028-09-13 09:00:00
last_updated       datetime.datetime 2019-09-09 17:39:04
status             str               'clientUpdateProhibited (https://www.icann.org/epp#clientUpdateProhibited)'
statuses           list              ['clientDeleteProhibited (https://www.icann.org/epp#clientDeleteProhibited)', 'clientTransferProhibited (https://www.icann.org/epp#clientTransferProhibited)', 'clientUpdateProhibited (https://www.icann.org/epp#clientUpdateProhibited)', 'serverDeleteProhibited (https://www.icann.org/epp#serverDeleteProhibited)', 'serverTransferProhibited (https://www.icann.org/epp#serverTransferProhibited)', 'serverUpdateProhibited (https://www.icann.org/epp#serverUpdateProhibited)']
dnssec             bool              False
name_servers       list              ['ns1.google.com', 'ns2.google.com', 'ns3.google.com', 'ns4.google.com']
registrant         str               'Google LLC'
emails             list              ['abusecomplaints@markmonitor.com', 'whoisrequest@markmonitor.com']

 ```

A short intro into the cli whoisdomain command
```
whoisdomain
    [ -v | --verbose ]
        # set verbose to True, this will be forwarded to whois.query

    [ -I | --IgnoreReturncode ]
        # sets the IgnoreReturncode to True, this will be forwarded to whois.query

    [ -a | --all]
        # test all existing tld currently supported,

    [ -d <domain> | --domain = <domain> " ]
        # only analyze the given domains
        # the option can be repeated to specify more then one domain

    [ -f <filename> | --file = <filename> " ]
        # use the named file to test all domains (one domain per line)
        # lines starting with # or empty lines are skipped, anything after the domain is ignored
        # the option can be repeated to specify more then one file

    [ -D <directory> | --Directory = <directory> " ]
        # use the named directory, ald use all files ending in .txt as files containing domains
        # files are processed as in the -f option so comments and empty lines are skipped
        # the option can be repeated to specify more then one directory

    [ -p | --print ]
    also print text containing the raw output of whois

    [ -R | --Ruleset ]
    dump the ruleset for the tld and exit

    [ -S | --SupportedTld ]
    print all supported top level domains we know and exit

    [ -C <file> | --Cleanup <file> ]
    read the input file specified and run the same cleanup as in whois.query , then exit

    # options are exclusive and without any options the whoisdomain program does nothing

    # test one specific file with verbose and IgnoreReturncode
    example: whoisdomain -v -I -f tests/ok-domains.txt 2>2 >out

    # test one specific directory with verbose and IgnoreReturncode
    example: whoisdomain -v -I -D tests 2>2 >out

    # test two domains with verbose and IgnoreReturncode
    example: whoisdomain -v -I -d meta.org -d meta.com 2>2 >out

    # test all supported tld's with verbose and IgnoreReturncode
    example: whoisdomain -v -I -a 2>2 >out

    # test nothing
    example: whoisdomain -v -I 2>2 >out

```

## ccTLD & TLD support
see the file: ./whoisdomain/tld_regexpr.py
or call whoisdomain.validTlds()

## Support
 * Python 3.x is supported for x >= 6
 * Python 2.x IS NOT supported.

## Author's
  * this is a rename copy of original work done in: https://github.com/DannyCork/python-whois
  * the project is also related to the project: https://github.com/gen1us2k/python-whois
  * both seem derived from a older google.code site: https://code.google.com/archive/p/python-whois
  * aside from the original authors, many others already contributed to the repositories
  * if authors/contributors prefer to be named explicitly, they can add a line in Historical.txt
