#!/usr/bin/env bash
# Train a probe on one version of the training data, then evaluate it.
#
#   bash iterate.sh <version-tag> <training-jsonl>
#
# Eval activations are cached under $ACT_DIR and reused across versions, so
# only the first evaluation pays the cost of running the 27B model.
set -euo pipefail

cd "$(dirname "$0")"
source run_env.sh

TAG="$1"
TRAIN_DATA="$2"

PROBE="probes/probe_${TAG}.pkl"
RESULTS="results/eval_${TAG}.csv"

mkdir -p probes results "$ACT_DIR"

echo "=== [$TAG] training on $TRAIN_DATA ==="
.venv/bin/python train.py \
  --model "$MODEL" \
  --layer "$LAYER" \
  --probe_training_data "$TRAIN_DATA" \
  --pos_class_label "$POS_LABEL" \
  --neg_class_label "$NEG_LABEL" \
  --concept_description "$CONCEPT_DESC" \
  --output_probe_path "$PROBE" \
  --activations_save_path "${ACT_DIR}/train_${TAG}.pt"

echo "=== [$TAG] evaluating ==="
.venv/bin/python evaluation.py \
  --probe_path "$PROBE" \
  --eval_dataset_save_dir "$EVAL_DIR" \
  --pos_class_label "$POS_LABEL" \
  --neg_class_label "$NEG_LABEL" \
  --results_file_name "$RESULTS" \
  --activations_save_path "${ACT_DIR}/eval.pt"

echo "=== [$TAG] results ==="
.venv/bin/python - "$RESULTS" <<'PY'
import sys
import pandas as pd
df = pd.read_csv(sys.argv[1])
print(df.to_string(index=False))
auroc = [c for c in df.columns if "auroc" in c.lower()]
if auroc:
    print(f"\nMEAN {auroc[0]}: {df[auroc[0]].mean():.4f}")
PY
