"""Per-family scores for a trained probe on its own training corpus.

Diagnostic, not a metric: it says which cells of the synthetic corpus the probe
actually learned and which it still gets wrong, which is what decides where the
next iteration's rows should go. Runs off the cached superset activations, so it
costs nothing once the training pass has been done.

    .venv/bin/python eval_pools.py --tag v1

Pools are grouped into families because most individual pools are single-class by
construction (A1 is all harmful, A3 all safe) and AUROC needs both. A family
pairs the harmful and safe halves that were written against each other.
"""

import argparse
import json
import pickle
import tempfile
from collections import defaultdict
from pathlib import Path

import torch
from dotenv import load_dotenv

load_dotenv(override=True)

from evaluation import ACTIVATION_FIELDS, read_activation_blob  # noqa: E402
from tuberlens.interfaces.dataset import LabelledDataset  # noqa: E402

POS, NEG = "harmful_to_human", "not_harmful_to_human"

# pool-name prefix -> family
FAMILIES = [
    ("A", "A_style_confound"),
    ("B", "B_third_party"),
    ("C", "C_dilemma_long"),
    ("D", "D_multiturn"),
    ("E", "E_refusal"),
    ("F", "F_info_and_ai"),
    ("G", "G_physical_wide"),
    ("H", "H_minimal_pairs"),
    ("I", "I_dilemma_short"),
    ("J", "J_contempt"),
    ("K", "K_dilemma_more"),
    ("L", "L_ai_dilemma"),
    ("seed", "seed"),
]


def family_of(source):
    for prefix, name in FAMILIES:
        if source.startswith(prefix):
            return name
    return "other"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tag", default="v1")
    ap.add_argument("--data", type=Path, default=Path("synthetic/hu_ha_v1.jsonl"))
    ap.add_argument("--acts", type=Path, default=None)
    ap.add_argument("--probe", type=Path, default=None)
    args = ap.parse_args()

    acts_path = args.acts or Path(f"activations/{args.tag}_acts.pt")
    probe_path = args.probe or Path(f"probes/probe_{args.tag}.pkl")

    probe = pickle.load(probe_path.open("rb"))
    blob = read_activation_blob(acts_path)
    rows = [json.loads(l) for l in args.data.read_text().splitlines() if l.strip()]
    meta = [json.loads(l) for l in args.data.with_suffix(".meta.jsonl").read_text().splitlines() if l.strip()]

    n = int(blob["activations"].shape[0])
    if not (n == len(rows) == len(meta)):
        raise ValueError(f"row counts disagree: blob={n} data={len(rows)} meta={len(meta)}")

    by_family = defaultdict(list)
    for i, m in enumerate(meta):
        by_family[family_of(m["source"])].append(i)

    from tuberlens.evaluation import get_performances

    datasets = {}
    with tempfile.TemporaryDirectory() as tmp:
        for family, idx in sorted(by_family.items()):
            labels = {meta[i]["labels"] for i in idx}
            if len(idx) < 8 or len(labels) < 2:
                print(f"[skip] {family}: {len(idx)} rows, {len(labels)} class(es)")
                continue
            path = Path(tmp) / f"{family}.jsonl"
            path.write_text("".join(json.dumps(rows[i]) + "\n" for i in idx))
            ds = LabelledDataset.load_from(path, pos_class_label=POS, neg_class_label=NEG)
            sel = torch.tensor(idx)
            datasets[family] = ds.assign(
                **{f: blob[f].index_select(0, sel) for f in ACTIVATION_FIELDS}
            )
        if not datasets:
            print("nothing scoreable")
            return
        print(get_performances(probe, datasets))


if __name__ == "__main__":
    main()
