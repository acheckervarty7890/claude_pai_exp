#!/usr/bin/env bash
# Refit one subset under several --seed values to size the run-to-run noise.
# Ablation gaps smaller than this spread are not worth acting on.
set -euo pipefail
TAG="${1:?usage: seed_check.sh <tag> <training_jsonl> <seed>...}"; shift
DATA="${1:?usage: seed_check.sh <tag> <training_jsonl> <seed>...}"; shift
for S in "$@"; do
  OUT="${TAG}_s${S}"
  ln -sf "$(realpath activations/val-v1_acts.pt)" "activations/val-${OUT}_acts.pt"
  cp -f "activations/${TAG}_acts.pt" "activations/${OUT}_acts.pt" 2>/dev/null || \
    ln -sf "$(realpath activations/${TAG}_acts.pt)" "activations/${OUT}_acts.pt"
  .venv/bin/python train.py --model google/gemma-3-27b-it --layer 32 \
    --probe_training_data "$DATA" --seed "$S" \
    --pos_class_label harmful_to_human --neg_class_label not_harmful_to_human \
    --concept_description "the conversation is harmful to the human" \
    --validation_data dev_samples/hu_ha --validation_activations_dir dev_activations_hu_ha \
    --activations_save_path "activations/${OUT}_acts.pt" \
    --output_probe_path "probes/probe_${OUT}.pkl" > "/tmp/train_${OUT}.log" 2>&1
  for w in dev eval; do
    case $w in dev) D=dev_samples/hu_ha; C=dev_activations_hu_ha;; eval) D=eval_datasets/hu_ha; C=eval_activations_hu_ha;; esac
    .venv/bin/python evaluation.py --probe_path "probes/probe_${OUT}.pkl" \
      --eval_dataset_save_dir "$D" --activations_cache_dir "$C" \
      --pos_class_label harmful_to_human --neg_class_label not_harmful_to_human \
      --results_file_name "results/results_${OUT}_${w}.csv" > /dev/null 2>&1
  done
  printf '%-22s dev %.4f   eval %.4f\n' "$OUT" \
    "$(tail -1 results/results_${OUT}_dev.csv | cut -d, -f2)" \
    "$(tail -1 results/results_${OUT}_eval.csv | cut -d, -f2)"
done
