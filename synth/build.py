"""Assemble the synthetic pools into a training JSONL for train.py.

Usage:
    .venv/bin/python -m synth.build --out synthetic/hu_ha_v1.jsonl --pools a b c d --seed-file initial_training_set/init_seed_hu_ha_50.jsonl

Output rows are exactly the seed's schema: {"inputs": <json string of a message
list>, "labels": <class label>}. Classes are balanced by trimming the larger side
(deterministically, under --seed) so the probe never sees a prior it can lean on.
"""

import argparse
import importlib
import json
import random
from pathlib import Path

from .common import NEG, POS

POOLS = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"]


def collect(pool_names):
    rows, provenance = [], {}
    for name in pool_names:
        mod = importlib.import_module(f"synth.pool_{name}")
        for attr, value in vars(mod).items():
            if attr.startswith("_") or not isinstance(value, list):
                continue
            if not value or not isinstance(value[0], tuple):
                continue
            for label, msgs in value:
                rows.append((label, msgs, attr))
            provenance[attr] = len(value)
    return rows, provenance


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--pools", nargs="+", default=["a", "b", "c", "d"])
    ap.add_argument("--seed-file", type=Path, default=None,
                    help="Original training seed to prepend (kept as-is)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--no-balance", action="store_true")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    rows, provenance = collect(args.pools)

    out_rows = []
    if args.seed_file is not None:
        for line in args.seed_file.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                out_rows.append((r["labels"], json.loads(r["inputs"]), "seed"))
    out_rows.extend(rows)

    # De-duplicate on the exact rendered conversation; a repeated row would just
    # reweight that point in the loss.
    seen, deduped = set(), []
    for label, msgs, src in out_rows:
        key = json.dumps(msgs, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        deduped.append((label, msgs, src))
    dropped = len(out_rows) - len(deduped)

    pos = [r for r in deduped if r[0] == POS]
    neg = [r for r in deduped if r[0] == NEG]
    if not args.no_balance:
        n = min(len(pos), len(neg))
        rng.shuffle(pos)
        rng.shuffle(neg)
        pos, neg = pos[:n], neg[:n]

    final = pos + neg
    rng.shuffle(final)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as f:
        for label, msgs, _ in final:
            f.write(json.dumps({"inputs": json.dumps(msgs), "labels": label}) + "\n")

    # Row-aligned sidecar naming each row's source pool. Activations for this file
    # are expensive to compute (a 27B forward pass per row), so ablations are done
    # by slicing the blob to a subset of these rows rather than recomputing - which
    # needs to know which pool each row came from. See make_subset.py.
    meta = args.out.with_suffix(".meta.jsonl")
    with meta.open("w") as f:
        for label, msgs, src in final:
            f.write(json.dumps({"source": src, "labels": label}) + "\n")

    by_src = {}
    for label, _, src in final:
        by_src.setdefault(src, [0, 0])
        by_src[src][0 if label == POS else 1] += 1
    print(f"wrote {len(final)} rows to {args.out}  ({len(pos)} {POS} / {len(neg)} {NEG})")
    if dropped:
        print(f"  dropped {dropped} duplicate conversation(s)")
    for src in sorted(by_src):
        p, n = by_src[src]
        print(f"  {src:32s} pos={p:3d} neg={n:3d}")


if __name__ == "__main__":
    main()
