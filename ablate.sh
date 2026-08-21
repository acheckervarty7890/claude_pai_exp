#!/usr/bin/env bash
# Leave-one-family-out over the superset, reusing its cached activations.
#
#   ./ablate.sh <tag> <drop-prefix>...
#
# The superset activation pass costs ~37 min; every ablation after it is a row
# slice of that blob plus a probe fit, so it runs in about two minutes and never
# loads the extraction model. The staged dev validation blob is shared by symlink
# for the same reason (it is ~890MB).
set -euo pipefail

TAG="${1:?usage: ablate.sh <tag> <drop-prefix>...}"; shift
SUPER=synthetic/hu_ha_v1.jsonl
SUPER_ACTS=activations/v1_acts.pt

.venv/bin/python make_subset.py --tag "$TAG" --superset "$SUPER" --superset-acts "$SUPER_ACTS" --drop "$@"

ln -sf "$(realpath activations/val-v1_acts.pt)" "activations/val-${TAG}_acts.pt"

.venv/bin/python train.py --model google/gemma-3-27b-it --layer 32 \
  --probe_training_data "synthetic/${TAG}.jsonl" \
  --pos_class_label harmful_to_human --neg_class_label not_harmful_to_human \
  --concept_description "the conversation is harmful to the human" \
  --validation_data dev_samples/hu_ha --validation_activations_dir dev_activations_hu_ha \
  --activations_save_path "activations/${TAG}_acts.pt" \
  --output_probe_path "probes/probe_${TAG}.pkl" > "/tmp/train_${TAG}.log" 2>&1

for w in dev eval; do
  case $w in
    dev)  D=dev_samples/hu_ha;   C=dev_activations_hu_ha ;;
    eval) D=eval_datasets/hu_ha; C=eval_activations_hu_ha ;;
  esac
  .venv/bin/python evaluation.py --probe_path "probes/probe_${TAG}.pkl" \
    --eval_dataset_save_dir "$D" --activations_cache_dir "$C" \
    --pos_class_label harmful_to_human --neg_class_label not_harmful_to_human \
    --results_file_name "results/results_${TAG}_${w}.csv" > /dev/null 2>&1
done
printf '%-22s dev %.4f   eval %.4f\n' "$TAG" \
  "$(tail -1 results/results_${TAG}_dev.csv | cut -d, -f2)" \
  "$(tail -1 results/results_${TAG}_eval.csv | cut -d, -f2)"
