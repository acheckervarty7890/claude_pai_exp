#!/usr/bin/env python
"""Build the v6 training JSONL: the v4 mixture plus pools_v6.TOOLS_MORE.

Seed repetition is a flag here rather than a fixed choice, so the v5 result decides
whether this run carries it.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import pools_v6 as P6
from gen_v1 import POS
from gen_v2 import tool_records
from gen_v4 import build as build_v4


def build(seed: int = 19):
    rng = random.Random(seed)
    out = build_v4()
    tool_records(P6.TOOLS_MORE, "toolmore", ("call", "result"), rng, out, 80_000,
                 [8, 9, 9, 10], [1, 2, 2])
    rng.shuffle(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("../synthetic_data/synth_v6.jsonl"))
    ap.add_argument("--seed-file", type=Path, default=Path("../initial_training_set/init_seed_hs_ls_200.jsonl"))
    ap.add_argument("--combined", type=Path, default=Path("../synthetic_data/train_v6.jsonl"))
    ap.add_argument("--seed-repeats", type=int, default=1)
    args = ap.parse_args()

    rows = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")

    seed_rows = [json.loads(l) for l in args.seed_file.read_text().splitlines() if l.strip()]
    combined = list(rows)
    for k in range(args.seed_repeats):
        for r in seed_rows:
            copy = dict(r)
            if k:
                copy["ids"] = f"{r['ids']}_rep{k}"
            combined.append(copy)
    random.Random(29).shuffle(combined)

    with args.combined.open("w") as fh:
        for r in combined:
            fh.write(json.dumps(r) + "\n")

    n_pos = sum(r["labels"] == POS for r in combined)
    print(f"wrote {len(rows)} synthetic rows -> {args.out}")
    print(
        f"wrote {len(combined)} combined rows ({n_pos} pos / {len(combined) - n_pos} neg) "
        f"-> {args.combined}  [seed x{args.seed_repeats}]"
    )
