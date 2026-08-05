# whoisdomain memory soak test on Docker Desktop for Windows

This project runs `whoisdomain==2.20260709.1` in a standalone Linux container. It uses Home Assistant's multi-architecture Python 3.14/Alpine 3.24 base image and its `psutil-home-assistant` build, but it does not run Home Assistant itself.

The image installs `whodap>=0.1.16` and `tld>=0.13.2` explicitly. This `whoisdomain` release imports those packages but does not declare them as install dependencies in its package metadata.

## Requirements

- Windows with Docker Desktop running Linux containers
- PowerShell 7 or Windows PowerShell 5.1
- internet access from the container

## Recommended first run

Open PowerShell in this directory:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
./run-test.ps1 -Action Start -Mode default -IntervalSeconds 60 -MaxDomains 100
./run-test.ps1 -Action Logs -Mode default
```

One domain is queried per interval. With 100 domains and 60 seconds, every domain is revisited roughly every 100 minutes. Do not interpret expected WHOIS/RDAP errors as memory leaks.

Every query creates a fresh `ParameterContext`, matching Home Assistant's call lifecycle. In `default` mode the exact library call is `whoisdomain.query(domain)`; diagnostic modes pass `whoisOnly=True` or `rdapOnly=True` per call.

Set `-IntervalSeconds 0` for a short maximum-throughput run. The next query then starts immediately after the previous query completes. Keep zero-interval runs short because they use public WHOIS/RDAP services and may trigger rate limits. Starting a new run automatically moves existing results to a timestamped archive directory.

Check status from another terminal:

```powershell
./run-test.ps1 -Action Status -Mode default
```

Stop cleanly and retain CSV results:

```powershell
./run-test.ps1 -Action Stop -Mode default
./run-test.ps1 -Action Analyze -Mode default
```

Results are stored in `results-default/metrics.csv` and `metadata.json`.

## Separate code paths

Run only one mode at a time initially:

```powershell
# Classic whois executable and parser/regex path
./run-test.ps1 -Action Start -Mode whois-only -IntervalSeconds 60 -MaxDomains 100

# RDAP/whodap path
./run-test.ps1 -Action Start -Mode rdap-only -IntervalSeconds 60 -MaxDomains 100
```

Use matching `-Mode` with `Status`, `Logs`, `Stop`, and `Analyze`.

The suggested sequence is:

1. `default` for 24 hours.
2. `whois-only` for 24 hours.
3. `rdap-only` for 24 hours.
4. Extend suspicious modes to seven days.

## Metrics

Every query records:

- process RSS, USS, and VMS;
- Python allocations from `tracemalloc`;
- Linux cgroup memory;
- live `re.Pattern` objects;
- entries in `whoisdomain`'s global `PATTERN_CACHE`;
- file descriptors, threads, and child processes;
- query status, duration, and truncated error.

The analyzer ignores the first 20% of samples as warm-up and calculates a linear memory trend per 1,000 queries. A positive trend is not by itself proof of a leak. Check whether the graph reaches a plateau and whether errors/rate limits dominate the measured period.

Strong leak indicators are:

- `tracemalloc_current_bytes` continuing to grow after several complete cycles;
- regex or pattern-cache counts increasing when the same domain set repeats;
- file descriptors or child processes increasing over time;
- RSS/USS rising approximately linearly without reaching a plateau.

If `tracemalloc` is stable but RSS rises, investigate native dependencies, subprocesses, DNS/HTTP clients, and allocator behavior.

## Important limitations

- This is a network soak test, not a deterministic CI regression test.
- Server rate limiting and changing responses affect results.
- The automatically selected domains come from `_test` hints bundled with `whoisdomain`; some may become unavailable.
- Do not reduce the interval aggressively against public WHOIS/RDAP services.
- A separate fixture-based test is still required before an upstream fix can be considered proven.

## Optional forced GC

Normal runs should keep forced GC disabled to reflect a long-running application:

```powershell
-ForceGcEvery 0
```

For diagnosis, repeat a suspicious mode with collection every 100 queries:

```powershell
./run-test.ps1 -Action Start -Mode whois-only -IntervalSeconds 60 -MaxDomains 100 -ForceGcEvery 100
```

If the trend disappears only with forced GC, objects may be collectible cycles rather than permanently referenced objects.
