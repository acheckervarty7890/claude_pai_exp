#!/usr/bin/env python
"""Build the v3 training JSONL: everything in v2, plus the register-inverting pools.

The v3 additions exist to break the shortcut v1 left in the data, where high stakes and
professional/technical register were confounded:

  pools_v3.TOOLS_MIXED  long heterogeneous tool schemas, identical in both classes
  pools_v4.HARD_CHAT    expert-register questions labelled low, plain-spoken crises high
  pools_v4.HARD_TOOLS   routine enterprise calls low, grave personal calls high
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import pools_v3 as P3
import pools_v4 as P4
from gen_v1 import GENERIC_SYSTEMS, HS_WHY, LS_WHY, NEG, POS, rec
from gen_v2 import TOOL_SYSTEM_STYLES, build as build_v2, tool_records

HARD_LOW_WHY = (
    "Synthetic hard negative: expert, technical or professional register with no real-world "
    "consequence attached, so register cannot stand in for stakes."
)
HARD_HIGH_WHY = (
    "Synthetic hard positive: plain, domestic, non-technical language describing an "
    "immediately dangerous or irreversible situation."
)


def build(seed: int = 13):
    rng = random.Random(seed)
    out = build_v2(seed=seed)
    pid = 40_000

    # --- long mixed tool schemas -----------------------------------------------
    pid = tool_records(P3.TOOLS_MIXED, "toolmix", ("call", "result"), rng, out, pid,
                       [8, 9, 9, 10], [1, 2, 2])

    # --- register-inverted chat -------------------------------------------------
    for i, (hs, ls) in enumerate(P4.HARD_CHAT):
        for shape in ("hard_bare", "hard_sys"):
            pid += 1
            for label, text, why, scale in (
                (POS, hs, HARD_HIGH_WHY, rng.choice([9, 9, 10, 10])),
                (NEG, ls, HARD_LOW_WHY, rng.choice([1, 2, 2, 3])),
            ):
                msgs = []
                if shape == "hard_sys":
                    msgs.append({"role": "system", "content": rng.choice(GENERIC_SYSTEMS)})
                msgs.append({"role": "user", "content": text})
                out.append(rec(msgs, label, pid, i, why, scale, shape))

    # --- register-inverted tool calls -------------------------------------------
    pid = tool_records(P4.HARD_TOOLS, "hardtool", ("call", "result"), rng, out, pid,
                       [9, 9, 10], [1, 2, 2])

    rng.shuffle(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("../synthetic_data/synth_v3.jsonl"))
    ap.add_argument("--seed-file", type=Path, default=Path("../initial_training_set/init_seed_hs_ls_200.jsonl"))
    ap.add_argument("--combined", type=Path, default=Path("../synthetic_data/train_v3.jsonl"))
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
    print(f"wrote {len(rows)} synthetic rows ({n_pos} {POS} / {len(rows) - n_pos} {NEG}) -> {args.out}")
    print("  by shape:", dict(sorted(by_shape.items())))

    with args.combined.open("w") as fh:
        for line in args.seed_file.read_text().splitlines():
            if line.strip():
                fh.write(line + "\n")
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(f"wrote combined seed+synthetic -> {args.combined}")
