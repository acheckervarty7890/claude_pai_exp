#!/usr/bin/env bash
# One iteration: stage the dev validation blob and train on a given JSONL.
#
#   ./run_experiment.sh <tag> <training_jsonl>
# Then: ./eval_probe.sh <tag> dev   and   ./eval_probe.sh <tag> eval
#
# Everything is pinned to the model/layer the fetched blobs were computed with
# (gemma-3-27b-it, layer 32) - a probe trained at any other model or layer is
# rejected by the blob validation at eval time.
set -euo pipefail

TAG="${1:?usage: run_experiment.sh <tag> <training_jsonl>}"
DATA="${2:?usage: run_experiment.sh <tag> <training_jsonl>}"

MODEL="google/gemma-3-27b-it"
LAYER=32
POS=harmful_to_human
NEG=not_harmful_to_human
ACTS="activations/${TAG}_acts.pt"
PROBE="probes/probe_${TAG}.pkl"

mkdir -p activations probes results

# All four dev splits as one validation set (train.py alone cannot concatenate
# them - their blobs have different sequence lengths).
.venv/bin/python stage_dev_val.py \
  --validation_data dev_samples/hu_ha \
  --validation_activations_dir dev_activations_hu_ha \
  --activations_save_path "$ACTS" \
  --model "$MODEL" --layer "$LAYER"

.venv/bin/python train.py \
  --model "$MODEL" --layer "$LAYER" \
  --probe_training_data "$DATA" \
  --pos_class_label "$POS" --neg_class_label "$NEG" \
  --concept_description "the conversation is harmful to the human" \
  --validation_data dev_samples/hu_ha \
  --validation_activations_dir dev_activations_hu_ha \
  --activations_save_path "$ACTS" \
  --output_probe_path "$PROBE"

echo "trained $PROBE — score it with ./eval_probe.sh $TAG dev  (or eval)"
