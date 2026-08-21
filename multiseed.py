"""Mean and spread of a run's dev/eval AUROC across its seed variants.

Seed-to-seed spread on this probe is around 0.02-0.03 AUROC, which is larger than
most of the leave-one-family-out gaps, so single-run comparisons are not decidable.
Everything gets compared on a multi-seed mean instead.

Groups results/results_<tag>[_s<seed>]_<which>.csv by <tag>.
"""

import csv
import re
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path


def mean_auroc(path):
    rows = list(csv.DictReader(path.open()))
    key = next(iter(rows[0]))
    for r in rows:
        if r[key] == "mean":
            return float(r["auroc"])
    return None


def main():
    only = set(sys.argv[1:])
    runs = defaultdict(lambda: defaultdict(list))
    for which in ("dev", "eval"):
        for p in sorted(Path("results").glob(f"results_*_{which}.csv")):
            tag = p.stem[len("results_"):-len(f"_{which}")]
            base = re.sub(r"_s\d+$", "", tag)
            if only and base not in only:
                continue
            v = mean_auroc(p)
            if v is not None:
                runs[base][which].append(v)

    print(f"{'run':<24}{'n':>3}{'dev mean':>11}{'±':>8}{'eval mean':>11}{'±':>8}")
    def key(t):
        e = runs[t]["eval"]
        return -(sum(e) / len(e)) if e else 0
    for tag in sorted(runs, key=key):
        d, e = runs[tag]["dev"], runs[tag]["eval"]
        dm = sum(d) / len(d) if d else float("nan")
        em = sum(e) / len(e) if e else float("nan")
        ds = st.stdev(d) if len(d) > 1 else 0.0
        es = st.stdev(e) if len(e) > 1 else 0.0
        print(f"{tag:<24}{max(len(d), len(e)):>3}{dm:>11.4f}{ds:>8.4f}{em:>11.4f}{es:>8.4f}")


if __name__ == "__main__":
    main()
