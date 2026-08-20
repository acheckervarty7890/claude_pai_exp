#!/usr/bin/env bash
# Evaluate a probe one eval split at a time.
#
# evaluation.py attaches every cached blob up front, and the four high-stakes eval
# blobs come to ~46 GB together - more than fits alongside anything else on this
# box. Each split is therefore run in its own process against a directory holding
# a single symlink to that split's labels file, and the per-split CSVs are
# concatenated afterwards (with the unweighted mean recomputed over the splits,
# which is what the single-process run would have reported).
set -euo pipefail

PROBE="$1"           # e.g. probes/probe_v1.pkl
OUT="$2"             # e.g. results/results_v1.csv
EVAL_DIR="${3:-eval_datasets/highstakes}"
CACHE_DIR="${4:-eval_activations_highstakes}"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

parts=()
for f in "$EVAL_DIR"/*.jsonl; do
  name="$(basename "$f" .jsonl)"
  mkdir -p "$WORK/$name"
  ln -sf "$(realpath "$f")" "$WORK/$name/$name.jsonl"
  .venv/bin/python evaluation.py \
    --probe_path "$PROBE" \
    --eval_dataset_save_dir "$WORK/$name" \
    --activations_cache_dir "$CACHE_DIR" \
    --pos_class_label high-stakes \
    --neg_class_label low-stakes \
    --results_file_name "$WORK/$name.csv" >"$WORK/$name.log" 2>&1 \
    || { echo "FAILED on $name"; tail -20 "$WORK/$name.log"; exit 1; }
  parts+=("$WORK/$name.csv")
done

.venv/bin/python - "$OUT" "${parts[@]}" <<'PY'
import sys, pandas as pd
out, parts = sys.argv[1], sys.argv[2:]
df = pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)
df = df[df.iloc[:, 0] != "mean"]
num = df.select_dtypes("number").mean()
mean_row = {df.columns[0]: "mean", **num.to_dict()}
df = pd.concat([df, pd.DataFrame([mean_row])], ignore_index=True)
df.to_csv(out, index=False)
print(df.to_string(index=False))
PY
