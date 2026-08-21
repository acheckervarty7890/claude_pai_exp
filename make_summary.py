"""Regenerate RESULTS.md from the per-split CSVs in results/.

Reads every results_<run>.csv (held-out eval) and dev_<run>.csv (tuning set) and
writes the two AUROC tables plus the training-set sizes, so the summary can never
drift from the numbers the runs actually produced.
"""
import json
import re
from pathlib import Path

import pandas as pd

FAMILY = {
    "33cf450b4eea": "anthropic_hh",
    "706fcbc9e21c": "multi_turn",
    "c5c436ad8e80": "clinical",
    "e1a1ee570ae0": "toolace",
    "mean": "MEAN",
}
ORDER = ["base", "v1", "v2", "v3", "v5", "v6", "v7"]
TRAIN = {"base": "initial_training_set/init_seed_hs_ls_50.jsonl"}


def table(prefix):
    cols = {}
    for run in ORDER:
        path = Path("results") / f"{prefix}_{run}.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        cols[run] = df.set_index(df.columns[0])["auroc"]
    if not cols:
        return None
    out = pd.DataFrame(cols)
    out.index = [FAMILY.get(i, i) for i in out.index]
    return out.round(4)


def sizes():
    rows = []
    for run in ORDER:
        path = Path(TRAIN.get(run, f"training_sets/train_{run}.jsonl"))
        if not path.exists():
            continue
        n = sum(1 for line in path.open() if line.strip())
        pos = sum(
            1
            for line in path.open()
            if line.strip() and json.loads(line)["labels"] == "high-stakes"
        )
        rows.append((run, path.as_posix(), n, pos, n - pos))
    return rows


def md_table(df):
    head = "| family | " + " | ".join(df.columns) + " |"
    sep = "|---" * (len(df.columns) + 1) + "|"
    body = [
        "| " + name + " | " + " | ".join(f"{v:.4f}" for v in row) + " |"
        for name, row in df.iterrows()
    ]
    return "\n".join([head, sep, *body])


if __name__ == "__main__":
    ev, dv = table("results"), table("dev")
    parts = ["# High-stakes probe: results\n"]
    parts.append(
        "AUROC per eval family, one column per training set. Split stems are hashed "
        "in the repo; the family names come from the fetch manifest's split names, "
        "whose row counts match the label files.\n"
    )
    parts.append("## Held-out eval (`eval_datasets/highstakes`)\n")
    parts.append(md_table(ev) + "\n")
    if dv is not None:
        parts.append("## Tuning set (`dev_samples/highstakes`)\n")
        parts.append(md_table(dv) + "\n")
    parts.append("## Training sets\n")
    parts.append("| run | file | rows | high | low |")
    parts.append("|---|---|---|---|---|")
    for run, path, n, pos, neg in sizes():
        parts.append(f"| {run} | `{path}` | {n} | {pos} | {neg} |")
    Path("RESULTS.md").write_text("\n".join(parts) + "\n")
    print("\n".join(parts))
