# whoisdomain

* https://pypi.org/project/whoisdomain/

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
 * both the module and the cli now support showing the version with lib:whois.getVersion() or cli:whoisdomain -V
 * the whoisdomain can now output json data (one per domain: e.g 'whoisdomain -d google.com -j' )
 * withRedacted: bool = False has been added to query(), if set to True any redacted fields will now be shown also (also supported in the cli whoisdomain as --withRedacted)
 * a analizer directory is presend in the github repo that will be used to look for new IANA tls's currently unsupported but maching known whois servers

## Dependencies
  * please install also the command line "whois" of your distribution as this library parses the output of the "whois" cli command of your operating system

## Notes for Mac users
  * it has been observed that the default cli whois on Mac is showing each forward step in its output, this makes parsing the result very unreliable.
  * using a brew install whois will give in general better results.

## Docker
https://hub.docker.com/r/mbootgithub/whoisdomain

 * docker pull mbootgithub/whoisdomain:latest
 * docker run mbootgithub/whoisdomain -V # show version
 * docker run mbootgithub/whoisdomain -d google.com # run one domain
 * docker run mbootgithub/whoisdomain -a # run all tld
 * docker run mbootgithub/whoisdomain -d google.com -j | jq -r . # run one domains , output in json and reformat with jq
 * docker run mbootgithub/whoisdomain -d google.com -j | jq -r '.expiration_date' # output only expire date
 * docker run mbootgithub/whoisdomain -d google.com -j | jq -r '[ .expiration_date, .creation_date ]

## Usage example

Install the cli `whois` of your operating system if it is not present already,
e.g 'apt install whois' or 'yum install whois'

```
# fedora 37
sudo yum install whois
pip install whoisdomain
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

# whoisdomain
```
# fedora 37
sudo yum install whois
pip3 install whoisdomain
whoisdomain -d google.com

test domain: <<<<<<<<<< google.com >>>>>>>>>>>>>>>>>>>>
name               'google.com'
tld                'com'
registrar          'MarkMonitor, Inc.'
registrant_country 'US'
creation_date      1997-09-15 09:00:00
expiration_date    2028-09-13 09:00:00
last_updated       2019-09-09 17:39:04
status             'clientUpdateProhibited (https://www.icann.org/epp#clientUpdateProhibited)'
statuses           ['clientDeleteProhibited (https://www.icann.org/epp#clientDeleteProhibited)', 'clientTransferProhibited (https://www.icann.org/epp#clientTransferProhibited)', 'clientUpdateProhibited (https://www.icann.org/epp#clientUpdateProhibited)', 'serverDeleteProhibited (https://www.icann.org/epp#serverDeleteProhibited)', 'serverTransferProhibited (https://www.icann.org/epp#serverTransferProhibited)', 'serverUpdateProhibited (https://www.icann.org/epp#serverUpdateProhibited)']
dnssec             False
name_servers       ['ns1.google.com', 'ns2.google.com', 'ns3.google.com', 'ns4.google.com']
registrant         'Google LLC'
emails             ['abusecomplaints@markmonitor.com', 'whoisrequest@markmonitor.com']
 ```

A short intro into the cli whoisdomain command
```
whoisdomain
    [ -h | --usage ]
        print this text and exit

    [ -V | --Version ]
        print the build version string
        and exit

    [ -S | --SupportedTld ]
        print all known top level domains
        and exit

    [ -a | --all]
        test all existing tld currently supported
        and exit

    [ -f <filename> | --file = <filename> " ]
        use the named file to test all domains (one domain per line)
        lines starting with # or empty lines are skipped, anything after the domain is ignored
        the option can be repeated to specify more then one file
        exits after processing all the files

    [ -D <directory> | --Directory = <directory> " ]
        use the named directory, ald use all files ending in .txt as files containing domains
        files are processed as in the -f option so comments and empty lines are skipped
        the option can be repeated to specify more then one directory
        exits after processing all the dirs

    [ -d <domain> | --domain = <domain> " ]
        only analyze the given domains
        the option can be repeated to specify more domain's

    [ -v | --verbose ]
        set verbose to True,
        verbose output will be printed on stderr only

    [ -j | --json ]
        print each result as json

    [ -I | --IgnoreReturncode ]
        sets the IgnoreReturncode to True,

    [ -p | --print ]
        also print text containing the raw output of the cli whois

    [ -R | --Ruleset ]
        dump the ruleset for the requested tld and exit
        should be combined with -d to specify tld's

    [ -C <file> | --Cleanup <file> ]
        read the input file specified and run the same cleanup as in whois.query,
        then exit

    # test two domains with verbose and IgnoreReturncode
    example: whoisdomain -v -I -d meta.org -d meta.com

    # test all supported tld's with verbose and IgnoreReturncode
    example: whoisdomain -v -I -a

    # test one specific file with verbose and IgnoreReturncode
    example: whoisdomain -v -I -f tests/ok-domains.txt

    # test one specific directory with verbose and IgnoreReturncode
    example: whoisdomain -v -I -D tests

```

# Json output
```
{
  "name": "hello.xyz",
  "tld": "xyz",
  "registrar": "Namecheap",
  "registrant_country": "IS",
  "creation_date": "2014-03-20 15:01:22",
  "expiration_date": "2024-03-20 23:59:59",
  "last_updated": "2023-03-14 09:24:32",
  "status": "clientTransferProhibited https://icann.org/epp#clientTransferProhibited",
  "statuses": [
    "clientTransferProhibited https://icann.org/epp#clientTransferProhibited"
  ],
  "dnssec": false,
  "name_servers": [
    "dns1.registrar-servers.com",
    "dns2.registrar-servers.com"
  ],
  "registrant": "Privacy service provided by Withheld for Privacy ehf",
  "emails": [
    "abuse@namecheap.com"
  ]
}
```
## ccTLD & TLD support
see the file: ./whoisdomain/tld_regexpr.py
or call lib:whoisdomain.validTlds() or cli:whoisdomain -S

## Support
 * Python 3.x is supported for x >= 6
 * Python 2.x IS NOT supported.

## Author's
  * this is a rename copy of original work done in: https://github.com/DannyCork/python-whois
  * the project is also related to the project: https://github.com/gen1us2k/python-whois
  * both seem derived from a older google.code site: https://code.google.com/archive/p/python-whois
  * aside from the original authors, many others already contributed to these repositories
  * if authors/contributors prefer to be named explicitly, they can add a line in Historical.txt

## Updates
  * 1.20230627.2 add Kenia proper whois server and known second level domains
  * 1.20230627.3 add rw tld proper whois server and second level ; restore mistakenly deleted .toml file
  * 1.20230627.3 additional kenia second level domains
  * 1.20230712.2 tld .edu now can have up to 10 nameservers; remove action on pull request
  * 1.20230717.1 add tld: com.ru, msk.ru, spb.ru  (all have a test documented), also update the tld: ru, the newlines are not needed.
  * 1.20230717.2 add option to parse partial result after timout has occurred (parse_partial_response:bool default False); this will need `stdbuf` installed otherwise it will fail
  * 1.20230718.3 fix typo in whois server hint for tld: ru
  * 1.20230720.1 add gov.tr; switch off status:available and status:free as None response, we should not interprete the result by default (we can add a option later)
  * 1.20230720.2 fix server hints for derived second level "xxx.tr", add processing "_test" hints during 'test2.py -a'
  * add external caching framework that can be overridden for use of your own caching implementation
  * renaming various vars to mak them more verbose
  * preparing for capturing all parameters in one object and parring that object around instead of many arguments in methods/functions
  * switch to json so we dont need a additional dependency in ParamContext
  * finish rework args to ParameterContext, split of domain as file
  * 1.20230803.1 frenzy refactor-release
  * 1.20230804.1 testing
  * 1.20230804.2 testing after remove of leading dot in rw second level domains
  * 1.20230804.3 simplefy cache implementation after feedback from `baderdean`
  * "more lembas bread", refactor parse and query
  * remove option to typecheck CACHE_STUB, use try/catch/exit instead, does not work when timout happens, removed ;-(
  * refactor doQuery create processWhoisDomainRequest, split of lastWhois
  * 1.20230806.1 testing done, prep new release: "more lembas bread"
  * bug found with the default timeout: if no timeout is specified the program fails: all pypi releases before 2023-07-17 yanked
  * 1.20230807.1 fix default timeout
  * add DummyCache, DBMCache, RedisCache with simple test in testCache.py, testing custom cache options
  * 1.20230811.1 ; replace type hint | with Union for py3.9 compat; switch off experimental redis tools
