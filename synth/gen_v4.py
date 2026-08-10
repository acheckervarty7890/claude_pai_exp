#!/usr/bin/env python
"""Build the v4 training JSONL: everything in v3, plus pools_v5.TOOLS_WIDE.

Split d responded most strongly to added function-calling data across v1 -> v2, so v4
widens the API surface again while keeping the register mixing that v3 introduced.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import pools_v5 as P5
from gen_v1 import POS
from gen_v2 import tool_records
from gen_v3 import build as build_v3


def build(seed: int = 17):
    rng = random.Random(seed)
    out = build_v3(seed=seed)
    tool_records(P5.TOOLS_WIDE, "toolwide", ("call", "result"), rng, out, 60_000,
                 [8, 9, 9, 10], [1, 2, 2])
    rng.shuffle(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("../synthetic_data/synth_v4.jsonl"))
    ap.add_argument("--seed-file", type=Path, default=Path("../initial_training_set/init_seed_hs_ls_200.jsonl"))
    ap.add_argument("--combined", type=Path, default=Path("../synthetic_data/train_v4.jsonl"))
    args = ap.parse_args()

    rows = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")

    n_pos = sum(r["labels"] == POS for r in rows)
    by_shape: dict[str, int] = {}
    for r in rows:
        key = r["ids"].rsplit("_", 2)[0][4:]
        by_shape[key] = by_shape.get(key, 0) + 1
    print(f"wrote {len(rows)} synthetic rows ({n_pos} pos / {len(rows) - n_pos} neg) -> {args.out}")
    print("  by shape:", dict(sorted(by_shape.items())))

    with args.combined.open("w") as fh:
        for line in args.seed_file.read_text().splitlines():
            if line.strip():
                fh.write(line + "\n")
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(f"wrote combined seed+synthetic -> {args.combined}")
