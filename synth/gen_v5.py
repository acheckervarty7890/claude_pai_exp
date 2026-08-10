#!/usr/bin/env python
"""Build the v5 training JSONL: the v4 mixture with the original seed upweighted.

Every synthetic round so far has cost a little AUROC on split c, which the 200-sample
seed alone scores highest on. The seed is the only data in the pile that was labelled
against the concept's own definition rather than authored here, so as the synthetic
volume grew it went from 100% of the training signal to about 20% of it. This run
repeats the seed so it keeps a meaningful share of the gradient without giving up the
coverage the synthetic pools bought on the other splits.

Duplicated rows get distinct ids so nothing downstream collapses them.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from gen_v1 import POS
from gen_v4 import build as build_v4

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-file", type=Path, default=Path("../initial_training_set/init_seed_hs_ls_200.jsonl"))
    ap.add_argument("--combined", type=Path, default=Path("../synthetic_data/train_v5.jsonl"))
    ap.add_argument("--seed-repeats", type=int, default=3)
    args = ap.parse_args()

    rows = build_v4()

    seed_rows = []
    for line in args.seed_file.read_text().splitlines():
        if line.strip():
            seed_rows.append(json.loads(line))

    combined = list(rows)
    for k in range(args.seed_repeats):
        for r in seed_rows:
            copy = dict(r)
            if k:
                copy["ids"] = f"{r['ids']}_rep{k}"
            combined.append(copy)

    random.Random(23).shuffle(combined)

    args.combined.parent.mkdir(parents=True, exist_ok=True)
    with args.combined.open("w") as fh:
        for r in combined:
            fh.write(json.dumps(r) + "\n")

    n_pos = sum(r["labels"] == POS for r in combined)
    print(
        f"wrote {len(combined)} rows ({n_pos} pos / {len(combined) - n_pos} neg) -> {args.combined}\n"
        f"  {len(rows)} synthetic + {len(seed_rows)} seed x{args.seed_repeats}"
    )
