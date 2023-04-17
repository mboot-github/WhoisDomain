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

 {'Try': [{'Domain': 'google.com', 'rawData': '[Querying whois.verisign-grs.com]\n[Redirected to whois.markmonitor.com]\n[Querying whois.markmonitor.com]\n[whois.markmonitor.com]\nDomain Name: google.com\nRegistry Domain ID: 2138514_DOMAIN_COM-VRSN\nRegistrar WHOIS Server: whois.markmonitor.com\nRegistrar URL: http://www.markmonitor.com\nUpdated Date: 2019-09-09T15:39:04+0000\nCreation Date: 1997-09-15T07:00:00+0000\nRegistrar Registration Expiration Date: 2028-09-13T07:00:00+0000\nRegistrar: MarkMonitor, Inc.\nRegistrar IANA ID: 292\nRegistrar Abuse Contact Email: abusecomplaints@markmonitor.com\nRegistrar Abuse Contact Phone: +1.2086851750\nDomain Status: clientUpdateProhibited (https://www.icann.org/epp#clientUpdateProhibited)\nDomain Status: clientTransferProhibited (https://www.icann.org/epp#clientTransferProhibited)\nDomain Status: clientDeleteProhibited (https://www.icann.org/epp#clientDeleteProhibited)\nDomain Status: serverUpdateProhibited (https://www.icann.org/epp#serverUpdateProhibited)\nDomain Status: serverTransferProhibited (https://www.icann.org/epp#serverTransferProhibited)\nDomain Status: serverDeleteProhibited (https://www.icann.org/epp#serverDeleteProhibited)\nRegistrant Organization: Google LLC\nRegistrant State/Province: CA\nRegistrant Country: US\nRegistrant Email: Select Request Email Form at https://domains.markmonitor.com/whois/google.com\nAdmin Organization: Google LLC\nAdmin State/Province: CA\nAdmin Country: US\nAdmin Email: Select Request Email Form at https://domains.markmonitor.com/whois/google.com\nTech Organization: Google LLC\nTech State/Province: CA\nTech Country: US\nTech Email: Select Request Email Form at https://domains.markmonitor.com/whois/google.com\nName Server: ns1.google.com\nName Server: ns3.google.com\nName Server: ns2.google.com\nName Server: ns4.google.com\nDNSSEC: unsigned\nURL of the ICANN WHOIS Data Problem Reporting System: http://wdprs.internic.net/\n>>> Last update of WHOIS database: 2023-04-17T08:13:22+0000 <<<\n\nFor more information on WHOIS status codes, please visit:\n  https://www.icann.org/resources/pages/epp-status-codes\n\nIf you wish to contact this domain’s Registrant, Administrative, or Technical\ncontact, and such email address is not visible above, you may do so via our web\nform, pursuant to ICANN’s Temporary Specification. To verify that you are not a\nrobot, please enter your email address to receive a link to a page that\nfacilitates email communication with the relevant contact(s).\n\nWeb-based WHOIS:\n  https://domains.markmonitor.com/whois\n\nIf you have a legitimate interest in viewing the non-public WHOIS details, send\nyour request and the reasons for your request to whoisrequest@markmonitor.com\nand specify the domain name in the subject line. We will review that request and\nmay ask for supporting documentation and explanation.\n\nThe data in MarkMonitor’s WHOIS database is provided for information purposes,\nand to assist persons in obtaining information about or related to a domain\nname’s registration record. While MarkMonitor believes the data to be accurate,\nthe data is provided "as is" with no guarantee or warranties regarding its\naccuracy.\n\nBy submitting a WHOIS query, you agree that you will use this data only for\nlawful purposes and that, under no circumstances will you use this data to:\n  (1) allow, enable, or otherwise support the transmission by email, telephone,\nor facsimile of mass, unsolicited, commercial advertising, or spam; or\n  (2) enable high volume, automated, or electronic processes that send queries,\ndata, or email to MarkMonitor (or its systems) or the domain name contacts (or\nits systems).\n\nMarkMonitor reserves the right to modify these terms at any time.\n\nBy submitting this query, you agree to abide by this policy.\n\nMarkMonitor Domain Management(TM)\nProtecting companies and consumers in a digital world.\n\nVisit MarkMonitor at https://www.markmonitor.com\nContact us at +1.8007459229\nIn Europe, at +44.02032062220\n--\n', 'server': None}]}
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
