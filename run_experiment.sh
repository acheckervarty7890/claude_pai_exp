#!/usr/bin/env bash
# Usage: run_experiment.sh <train_jsonl> <probe_out.pkl> <results.csv>
set -euo pipefail
cd "$(dirname "$0")"
TRAIN="$1"; PROBE="$2"; RESULTS="$3"

echo ">>> Training on $TRAIN"
.venv/bin/python train.py \
  --probe_training_data "$TRAIN" \
  --pos_class_label harmful_to_human \
  --neg_class_label not_harmful_to_human \
  --concept_description "the conversation is harmful to human" \
  --output_probe_path "$PROBE" 2>&1 | grep -iE "samples for training|Validation AUROC|Early stopping" | tail -3

echo ">>> Evaluating -> $RESULTS"
.venv/bin/python evaluation.py \
  --probe_path "$PROBE" \
  --eval_dataset_save_dir eval_datasets/hu_ha \
  --pos_class_label harmful_to_human \
  --neg_class_label not_harmful_to_human \
  --results_file_name "$RESULTS" 2>&1 | grep -vE "Processing batches|Loading weights|it/s|Note:" | tail -8

echo "=== $RESULTS ==="
cat "$RESULTS"
