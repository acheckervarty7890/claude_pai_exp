#!/usr/bin/env bash
# Score a trained probe against either the dev or the eval split set.
#
#   ./eval_probe.sh <tag> [dev|eval]
#
# Both are the same code path - evaluation.py globs *.jsonl out of a directory and
# attaches the matching precomputed blobs - so dev gives an identical metric shape
# without waiting on the eval download or loading the extraction model. Iterate on
# dev; keep eval for confirmation.
set -euo pipefail

TAG="${1:?usage: eval_probe.sh <tag> [dev|eval]}"
WHICH="${2:-eval}"

case "$WHICH" in
  dev)  DATA=dev_samples/hu_ha;   CACHE=dev_activations_hu_ha  ;;
  eval) DATA=eval_datasets/hu_ha; CACHE=eval_activations_hu_ha ;;
  *) echo "second argument must be dev or eval" >&2; exit 2 ;;
esac

mkdir -p results
OUT="results/results_${TAG}${WHICH:+_$WHICH}.csv"
[ "$WHICH" = eval ] && OUT="results/results_${TAG}.csv"

.venv/bin/python evaluation.py \
  --probe_path "probes/probe_${TAG}.pkl" \
  --eval_dataset_save_dir "$DATA" \
  --activations_cache_dir "$CACHE" \
  --pos_class_label harmful_to_human \
  --neg_class_label not_harmful_to_human \
  --results_file_name "$OUT"

echo "=== $TAG / $WHICH ==="
cat "$OUT"
