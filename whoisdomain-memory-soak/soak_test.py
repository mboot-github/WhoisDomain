#!/usr/bin/env python3
"""Long-running memory soak test for whoisdomain."""

from __future__ import annotations

import csv
import gc
import json
import os
from pathlib import Path
import re
import signal
import socket
import sys
import time
import tracemalloc
from typing import Any

import psutil
import whoisdomain


OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/results"))
INTERVAL = max(0.0, float(os.getenv("QUERY_INTERVAL_SECONDS", "60")))
MAX_DOMAINS = max(1, int(os.getenv("MAX_DOMAINS", "100")))
MODE = os.getenv("MODE", "default").lower()
FORCE_GC_EVERY = max(0, int(os.getenv("FORCE_GC_EVERY", "0")))
DOMAIN_FILE = os.getenv("DOMAIN_FILE", "")
STOP = False

CSV_FIELDS = [
    "timestamp_utc",
    "elapsed_seconds",
    "query_number",
    "cycle_number",
    "domain",
    "mode",
    "status",
    "duration_seconds",
    "rss_bytes",
    "uss_bytes",
    "vms_bytes",
    "tracemalloc_current_bytes",
    "tracemalloc_peak_bytes",
    "gc_gen0",
    "gc_gen1",
    "gc_gen2",
    "regex_pattern_objects",
    "whoisdomain_pattern_cache_entries",
    "open_fds",
    "threads",
    "child_processes",
    "cgroup_memory_current_bytes",
    "error",
]


def stop_handler(_signum: int, _frame: Any) -> None:
    global STOP
    STOP = True


def cgroup_memory_current() -> int:
    for candidate in (
        Path("/sys/fs/cgroup/memory.current"),
        Path("/sys/fs/cgroup/memory/memory.usage_in_bytes"),
    ):
        try:
            return int(candidate.read_text(encoding="ascii").strip())
        except (FileNotFoundError, PermissionError, ValueError):
            continue
    return -1


def pattern_cache_size() -> int:
    try:
        from whoisdomain.tldDb import finders

        return len(finders.PATTERN_CACHE)
    except (AttributeError, ImportError):
        return -1


def pattern_object_count() -> int:
    return sum(1 for obj in gc.get_objects() if isinstance(obj, re.Pattern))


def load_domains() -> list[str]:
    if DOMAIN_FILE:
        path = Path(DOMAIN_FILE)
        domains = [
            line.strip().lower()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
    else:
        domains = []
        for tld in whoisdomain.validTlds():
            hint = whoisdomain.getTestHint(tld)
            if hint and hint not in domains:
                domains.append(hint)

    if not domains:
        raise RuntimeError("No domains found. Supply DOMAIN_FILE or check package test hints.")
    return domains[:MAX_DOMAINS]


def query_domain(domain: str) -> Any:
    """Query with the same per-call ParameterContext lifecycle as Home Assistant."""
    if MODE == "default":
        return whoisdomain.query(domain)
    if MODE == "whois-only":
        return whoisdomain.query(domain, whoisOnly=True)
    if MODE == "rdap-only":
        return whoisdomain.query(domain, rdapOnly=True)
    raise ValueError("MODE must be default, whois-only, or rdap-only")


def safe_uss(process: psutil.Process) -> int:
    try:
        return int(process.memory_full_info().uss)
    except (AttributeError, psutil.Error):
        return -1


def main() -> int:
    signal.signal(signal.SIGTERM, stop_handler)
    signal.signal(signal.SIGINT, stop_handler)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    domains = load_domains()
    process = psutil.Process()
    started = time.time()
    tracemalloc.start(25)

    metadata = {
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "hostname": socket.gethostname(),
        "python": sys.version,
        "whoisdomain": whoisdomain.getVersion(),
        "mode": MODE,
        "interval_seconds": INTERVAL,
        "domain_count": len(domains),
        "domains": domains,
    }
    (OUTPUT_DIR / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    csv_path = OUTPUT_DIR / "metrics.csv"
    new_file = not csv_path.exists() or csv_path.stat().st_size == 0
    query_number = 0

    with csv_path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        if new_file:
            writer.writeheader()
            csv_file.flush()

        print(
            f"Starting mode={MODE}, domains={len(domains)}, interval={INTERVAL}s, "
            f"output={csv_path}",
            flush=True,
        )

        while not STOP:
            domain = domains[query_number % len(domains)]
            query_number += 1
            cycle_number = ((query_number - 1) // len(domains)) + 1
            query_started = time.monotonic()
            status = "ok"
            error = ""

            try:
                query_domain(domain)
            except Exception as exc:  # Metrics must survive expected WHOIS/RDAP failures.
                status = type(exc).__name__
                error = str(exc).replace("\n", " ")[:500]

            if FORCE_GC_EVERY and query_number % FORCE_GC_EVERY == 0:
                gc.collect()

            duration = time.monotonic() - query_started
            mem = process.memory_info()
            traced_current, traced_peak = tracemalloc.get_traced_memory()
            gc_counts = gc.get_count()
            try:
                open_fds = process.num_fds()
            except (AttributeError, psutil.Error):
                open_fds = -1

            row = {
                "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "elapsed_seconds": round(time.time() - started, 3),
                "query_number": query_number,
                "cycle_number": cycle_number,
                "domain": domain,
                "mode": MODE,
                "status": status,
                "duration_seconds": round(duration, 3),
                "rss_bytes": mem.rss,
                "uss_bytes": safe_uss(process),
                "vms_bytes": mem.vms,
                "tracemalloc_current_bytes": traced_current,
                "tracemalloc_peak_bytes": traced_peak,
                "gc_gen0": gc_counts[0],
                "gc_gen1": gc_counts[1],
                "gc_gen2": gc_counts[2],
                "regex_pattern_objects": pattern_object_count(),
                "whoisdomain_pattern_cache_entries": pattern_cache_size(),
                "open_fds": open_fds,
                "threads": process.num_threads(),
                "child_processes": len(process.children(recursive=True)),
                "cgroup_memory_current_bytes": cgroup_memory_current(),
                "error": error,
            }
            writer.writerow(row)
            csv_file.flush()
            print(
                f"#{query_number} cycle={cycle_number} {domain} {status} "
                f"rss={mem.rss / 1024 / 1024:.1f}MiB "
                f"traced={traced_current / 1024 / 1024:.1f}MiB "
                f"patterns={row['regex_pattern_objects']} cache={row['whoisdomain_pattern_cache_entries']}",
                flush=True,
            )

            deadline = time.monotonic() + INTERVAL
            while not STOP and time.monotonic() < deadline:
                time.sleep(min(1.0, deadline - time.monotonic()))

    print("Stopped cleanly.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
