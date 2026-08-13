#!/usr/bin/env bash
# Re-fit one dataset's probe under several seeds to measure the noise floor.
#
#   bash seed_variance.sh <tag> <training-jsonl> <seed> [seed ...]
#
# The recipes are separated by ~0.01 mean AUROC, which is only meaningful if
# refitting the *same* data varies by less than that.
#
# Each seed gets its OWN train activation file. `train.py` seeds the RNG before
# create_train_test_split, so the split membership and order are seed-dependent,
# while tuberlens' get_activations returns a cached tensor whenever save_path
# exists without checking that the inputs still match. Sharing one cache across
# seeds therefore pairs one split's activations with another split's labels and
# silently trains on mislabelled data -- it scores ~0.5, which looks like a
# catastrophic result rather than the bug it is. The eval cache is safe to share
# (evaluation.py neither shuffles nor subsamples), so only training re-extracts.
set -euo pipefail

cd "$(dirname "$0")"
source run_env.sh

TAG="$1"
TRAIN_DATA="$2"
shift 2

for SEED in "$@"; do
  echo "=== [$TAG] seed $SEED ==="
  .venv/bin/python train.py \
    --model "$MODEL" \
    --layer "$LAYER" \
    --probe_training_data "$TRAIN_DATA" \
    --pos_class_label "$POS_LABEL" \
    --neg_class_label "$NEG_LABEL" \
    --concept_description "$CONCEPT_DESC" \
    --output_probe_path "probes/probe_${TAG}_s${SEED}.pkl" \
    --activations_save_path "${ACT_DIR}/train_${TAG}_s${SEED}.pt" \
    --seed "$SEED" 2>&1 | tail -2

  .venv/bin/python evaluation.py \
    --probe_path "probes/probe_${TAG}_s${SEED}.pkl" \
    --eval_dataset_save_dir "$EVAL_DIR" \
    --pos_class_label "$POS_LABEL" \
    --neg_class_label "$NEG_LABEL" \
    --results_file_name "results/seedvar_${TAG}_s${SEED}.csv" \
    --activations_save_path "${ACT_DIR}/eval.pt" \
    --seed "$SEED" 2>&1 | tail -2
done

.venv/bin/python - "$TAG" <<'PY'
import sys
from pathlib import Path

import pandas as pd

tag = sys.argv[1]
cols = {}
for path in sorted(Path("results").glob(f"seedvar_{tag}_s*.csv")):
    df = pd.read_csv(path)
    name = "dataset" if "dataset" in df.columns else df.columns[0]
    cols[path.stem.split("_")[-1]] = (
        df.set_index(name)["auroc"].drop(index="mean", errors="ignore")
    )
table = pd.DataFrame(cols)
table.loc["** MEAN **"] = table.mean()
table["spread"] = table.max(axis=1) - table.min(axis=1)
print(f"\n=== {tag}: same data, different seeds ===")
print(table.round(4).to_string())
PY
