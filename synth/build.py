"""Expand contrastive PAIRS modules into a training JSONL for the probe.

Usage:
    .venv/bin/python synth/build.py --out initial_training_set/train_fi_v1.jsonl \
        --modules pairs_v1 [pairs_v2 ...] [--no-seed]
"""

import argparse
import importlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED_PATH = ROOT / "initial_training_set" / "init_seed_follows_instruction.jsonl"
POS = "assistant_follows_the_instruction"
NEG = "assistant_does_not_follow_the_instruction"


def to_rows(item: dict) -> list[dict]:
    """Turn one contrastive item into a compliant row and a non-compliant row."""
    base = []
    if item.get("sys"):
        base.append({"role": "system", "content": item["sys"]})
    for role, content in item.get("pre", []):
        base.append({"role": role, "content": content})
    base.append({"role": "user", "content": item["u"]})

    rows = []
    for key, label in (("pos", POS), ("neg", NEG)):
        msgs = base + [{"role": "assistant", "content": item[key]}]
        rows.append({"inputs": json.dumps(msgs, ensure_ascii=False), "labels": label})
    return rows


def lengthen(items: list[dict], n: int, rng: random.Random) -> list[dict]:
    """Build long-context variants by prepending compliant history to a pair.

    Training conversations are ~110 tokens while the eval conversations are
    several times that, and a probe fitted only on short exchanges has never
    seen the pooled-activation statistics of a long one. Prepending unrelated
    but *compliant* turns lengthens the context while leaving the label
    determined solely by the final assistant turn.

    The char budget keeps the decisive turn inside the 1024-token window that
    `get_activations` truncates to -- overshooting it would cut the final turn
    off entirely and turn these into mislabelled samples.
    """
    # History turns are drawn from single-turn items only, so the prepended
    # context is always a clean, compliant user/assistant exchange.
    pool = [it for it in items if not it.get("pre") and not it.get("sys")]
    if not pool:
        return []

    budget = 3600  # chars, ~900 tokens
    out = []
    for _ in range(n):
        target = rng.choice(items)
        target_len = len(target["u"]) + max(len(target["pos"]), len(target["neg"]))
        room = budget - target_len
        if room < 400:
            continue

        history, used = [], 0
        for src in rng.sample(pool, k=min(len(pool), 12)):
            if src is target:
                continue
            cost = len(src["u"]) + len(src["pos"])
            if used + cost > room:
                continue
            history.append(("user", src["u"]))
            history.append(("assistant", src["pos"]))
            used += cost
            if used > room * 0.7:
                break

        if len(history) < 4:  # at least two prior exchanges
            continue

        out.append({**target, "pre": list(target.get("pre", [])) + history})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--modules", nargs="+", required=True)
    ap.add_argument("--no-seed", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument(
        "--long-aug",
        type=int,
        default=0,
        help="Number of long-context variants to synthesize from the pairs.",
    )
    args = ap.parse_args()

    rows = []
    if not args.no_seed:
        with open(SEED_PATH) as f:
            rows.extend(json.loads(line) for line in f)
        print(f"seed rows: {len(rows)}")

    all_items: list[dict] = []
    for mod_name in args.modules:
        mod = importlib.import_module(f"synth.{mod_name}")
        n_before = len(rows)
        for item in mod.PAIRS:
            rows.extend(to_rows(item))
        all_items.extend(mod.PAIRS)
        print(f"{mod_name}: {len(mod.PAIRS)} pairs -> {len(rows) - n_before} rows")

    if args.long_aug:
        rng = random.Random(args.seed + 1)
        long_items = lengthen(all_items, args.long_aug, rng)
        n_before = len(rows)
        for item in long_items:
            rows.extend(to_rows(item))
        print(f"long-aug: {len(long_items)} pairs -> {len(rows) - n_before} rows")

    random.Random(args.seed).shuffle(rows)

    counts = {POS: 0, NEG: 0}
    for r in rows:
        counts[r["labels"]] += 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"wrote {len(rows)} rows to {out}")
    print(f"  {POS}: {counts[POS]}")
    print(f"  {NEG}: {counts[NEG]}")


if __name__ == "__main__":
    main()
