"""Carve an ablation out of the superset training file, activations included.

Computing activations for a training file is a 27B forward pass per row, so every
ablation reuses the superset's blob instead of recomputing: this writes a subset
JSONL (row order preserved) and the matching row-slice of the superset activation
blob, saved where train.py will look for it.

    .venv/bin/python make_subset.py --tag noseed --drop seed
    .venv/bin/python make_subset.py --tag minimal_pairs --keep H_ I_ H_SAFE

--keep/--drop match a row's source pool name by prefix, as recorded in the
<superset>.meta.jsonl sidecar written by synth.build.
"""

import argparse
import json
from pathlib import Path

import torch

from evaluation import ACTIVATION_FIELDS, read_activation_blob


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--superset", type=Path, default=Path("synthetic/hu_ha_v1.jsonl"))
    ap.add_argument("--superset-acts", type=Path, default=Path("activations/v1_acts.pt"))
    ap.add_argument("--tag", required=True, help="Output tag: synthetic/<tag>.jsonl + activations/<tag>_acts.pt")
    ap.add_argument("--keep", nargs="*", default=None, help="Source-pool prefixes to keep")
    ap.add_argument("--drop", nargs="*", default=None, help="Source-pool prefixes to drop")
    args = ap.parse_args()

    rows = [json.loads(l) for l in args.superset.read_text().splitlines() if l.strip()]
    meta_path = args.superset.with_suffix(".meta.jsonl")
    meta = [json.loads(l) for l in meta_path.read_text().splitlines() if l.strip()]
    if len(rows) != len(meta):
        raise ValueError(f"{args.superset} has {len(rows)} rows but {meta_path} has {len(meta)}")

    def wanted(src):
        if args.keep is not None and not any(src.startswith(k) for k in args.keep):
            return False
        if args.drop is not None and any(src.startswith(d) for d in args.drop):
            return False
        return True

    idx = [i for i, m in enumerate(meta) if wanted(m["source"])]
    if not idx:
        raise ValueError("subset is empty")

    out_jsonl = Path("synthetic") / f"{args.tag}.jsonl"
    out_jsonl.write_text("".join(json.dumps(rows[i]) + "\n" for i in idx))
    (out_jsonl.with_suffix(".meta.jsonl")).write_text(
        "".join(json.dumps(meta[i]) + "\n" for i in idx)
    )

    pos = sum(1 for i in idx if meta[i]["labels"] == "harmful_to_human")
    print(f"[subset] {len(idx)} rows -> {out_jsonl}  ({pos} pos / {len(idx) - pos} neg)")

    if args.superset_acts.exists():
        blob = read_activation_blob(args.superset_acts)
        sel = torch.tensor(idx)
        sliced = {f: blob[f].index_select(0, sel) for f in ACTIVATION_FIELDS if f in blob}
        for key in ("model_name", "layer"):
            if key in blob:
                sliced[key] = blob[key]
        out_acts = Path("activations") / f"{args.tag}_acts.pt"
        out_acts.parent.mkdir(parents=True, exist_ok=True)
        torch.save(sliced, out_acts)
        print(f"[subset] sliced activations -> {out_acts} {tuple(sliced['activations'].shape)}")
    else:
        print(f"[subset] no superset activations at {args.superset_acts}; "
              "train.py will compute them for this subset")


if __name__ == "__main__":
    main()
