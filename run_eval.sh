#!/usr/bin/env bash
# Score a probe against a split set. Usage: run_eval.sh <probe.pkl> <dev|eval> <tag>
# Model selection uses dev; eval is only read to confirm progress at the end of an
# iteration, so the held-out set is not being optimised against directly.
set -euo pipefail
cd /workspace/claude_pai_exp

PROBE="$1"; WHICH="$2"; TAG="$3"

case "$WHICH" in
  dev)  DATA=dev_samples/instructions;   ACTS=dev_activations_instructions ;;
  eval) DATA=eval_datasets/instructions; ACTS=eval_activations_instructions ;;
  *) echo "second arg must be dev or eval" >&2; exit 2 ;;
esac

OUT="results/${TAG}_${WHICH}.csv"

MAX_MEMORY="0=22GiB,cpu=45GiB" OFFLOAD_BUFFERS=true \
.venv/bin/python evaluation.py \
  --probe_path "$PROBE" \
  --eval_dataset_save_dir "$DATA" \
  --activations_cache_dir "$ACTS" \
  --pos_class_label assistant_follows_the_instruction \
  --neg_class_label assistant_does_not_follow_the_instruction \
  --results_file_name "$OUT" > "logs/eval_${TAG}_${WHICH}.log" 2>&1

echo "--- ${TAG} / ${WHICH} ---"
.venv/bin/python - "$OUT" <<'PY'
import sys, pandas as pd
df = pd.read_csv(sys.argv[1])
cols = [c for c in ("dataset","split","name","auroc","accuracy","tpr_at_fpr") if c in df.columns]
print(df[cols].to_string(index=False))
PY
