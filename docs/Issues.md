# Known issues

# Memory

It has been observed by a user that in very long sessions memory issues can manifest.

The memory issue is not relevant for short running use
but when using whoisdomain in long running programs
you should be aware that each query may increase its memory use.

With the assistance of Misiu we now formulate the potential issue as:

- The original high-memory report was observed on Windows with Sysinternals whois.exe.
- Linux/Alpine testing with a repeated fixed domain/TLD set showed bounded cache warm-up and a memory plateau, not continuous per-query growth.
- Querying previously unused TLDs may populate additional regex/cache entries.
- Windows, very high concurrency and extremely large workloads have not yet been conclusively characterized.

for further deftails see https://github.com/mboot-github/WhoisDomain/issues/30
