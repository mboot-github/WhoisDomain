#!/usr/bin/env python3
"""Summarize a metrics.csv file without third-party dependencies."""

from __future__ import annotations

import csv
import math
from pathlib import Path
import sys


def slope(xs: list[float], ys: list[float]) -> float:
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    denominator = sum((x - x_mean) ** 2 for x in xs)
    if denominator == 0:
        return math.nan
    return sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denominator


def mib(value: float) -> float:
    return value / 1024 / 1024


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "results/metrics.csv")
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) < 20:
        print(f"Too few samples: {len(rows)} (need at least 20)")
        return 2

    # Ignore the first 20% as warm-up.
    measured = rows[max(1, len(rows) // 5) :]
    xs = [float(row["query_number"]) for row in measured]

    print(f"Samples: {len(rows)}; measured after warm-up: {len(measured)}")
    for field in ("rss_bytes", "uss_bytes", "tracemalloc_current_bytes", "cgroup_memory_current_bytes"):
        values = [float(row[field]) for row in measured if float(row[field]) >= 0]
        field_xs = [
            float(row["query_number"])
            for row in measured
            if float(row[field]) >= 0
        ]
        if len(values) < 2:
            continue
        per_query = slope(field_xs, values)
        per_1000 = mib(per_query * 1000)
        print(
            f"{field}: first={mib(values[0]):.2f} MiB, last={mib(values[-1]):.2f} MiB, "
            f"min={mib(min(values)):.2f}, max={mib(max(values)):.2f}, "
            f"trend={per_1000:+.3f} MiB/1000 queries"
        )

    for field in ("regex_pattern_objects", "whoisdomain_pattern_cache_entries", "open_fds", "child_processes"):
        values = [int(row[field]) for row in measured]
        print(f"{field}: first={values[0]}, last={values[-1]}, min={min(values)}, max={max(values)}")

    errors = sum(1 for row in rows if row["status"] != "ok")
    print(f"Non-ok queries: {errors}/{len(rows)}")
    print("Interpret trend only after checking errors/rate limits and whether values reached a plateau.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
