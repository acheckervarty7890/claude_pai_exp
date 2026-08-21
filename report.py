"""Tabulate every results/results_*.csv side by side, sorted by mean AUROC.

Split names are the eval files' stems (opaque hashes), so they are printed as
given - the point is the trend across iterations, not which split is which.
"""

import csv
import sys
from pathlib import Path

METRICS = ("auroc", "accuracy", "tpr_at_fpr")


def load(path):
    """{split_name: {metric: value}} for one results CSV."""
    with path.open() as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return {}
    name_col = next(iter(rows[0]))  # first column names the split; 'mean' is the last row
    return {r[name_col]: r for r in rows}


def main():
    paths = sorted(Path("results").glob("results_*.csv"))
    if len(sys.argv) > 1:
        wanted = set(sys.argv[1:])
        paths = [p for p in paths if p.stem.replace("results_", "") in wanted]
    if not paths:
        print("no results yet")
        return

    runs = {p.stem.replace("results_", ""): load(p) for p in paths}

    splits = []
    for r in runs.values():
        for s in r:
            if s not in splits and s != "mean":
                splits.append(s)
    splits.append("mean")

    def mean_auroc(tag):
        try:
            return float(runs[tag]["mean"]["auroc"])
        except (KeyError, TypeError, ValueError):
            return -1.0

    order = sorted(runs, key=lambda t: -mean_auroc(t))

    for metric in METRICS:
        if not any(metric in next(iter(r.values()), {}) for r in runs.values() if r):
            continue
        print(f"\n=== {metric} ===")
        print(f"{'run':<26}" + "".join(f"{s[:13]:>15}" for s in splits))
        for tag in order:
            cells = ""
            for s in splits:
                v = runs[tag].get(s, {}).get(metric)
                try:
                    cells += f"{float(v):>15.4f}"
                except (TypeError, ValueError):
                    cells += f"{'-':>15}"
            print(f"{tag:<26}{cells}")


if __name__ == "__main__":
    main()
