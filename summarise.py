"""One line per run: per-split eval AUROC plus the mean, ordered by mean."""
import csv, sys
from pathlib import Path

SPLITS = {  # eval stem -> readable name (from the fetch manifest's split names)
    "228c4932c563": "ai_dilem", "28755bfa0e99": "ant_hh",
    "6f894eb4d195": "daily_dil", "7e06f33c554b": "bal_refus",
    "734b25929d93": "ai_dilem", "c6241094aa14": "daily_dil",
    "d8e7c86f242a": "bal_refus", "fe3d70860961": "ant_hh",
}
ORDER = ["ai_dilem", "ant_hh", "daily_dil", "bal_refus"]


def load(p):
    rows = list(csv.DictReader(p.open()))
    key = next(iter(rows[0]))
    return {SPLITS.get(r[key], r[key]): r for r in rows}


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "eval"
    runs = {}
    for p in sorted(Path("results").glob(f"results_*_{which}.csv")):
        runs[p.stem[len("results_"):-len(f"_{which}")]] = load(p)
    if not runs:
        print(f"no {which} results")
        return
    print(f"=== {which} AUROC ===")
    print(f"{'run':<24}" + "".join(f"{s:>11}" for s in ORDER) + f"{'MEAN':>11}")
    for tag in sorted(runs, key=lambda t: -float(runs[t]["mean"]["auroc"])):
        r = runs[tag]
        cells = "".join(f"{float(r[s]['auroc']):>11.4f}" if s in r else f"{'-':>11}" for s in ORDER)
        print(f"{tag:<24}{cells}{float(r['mean']['auroc']):>11.4f}")


if __name__ == "__main__":
    main()
