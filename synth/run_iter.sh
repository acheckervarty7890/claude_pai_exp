#!/usr/bin/env bash
# Usage: run_iter.sh <tag> <train_jsonl>
# Trains a probe on <train_jsonl> and evaluates it, writing runs/probe_<tag>.pkl
# and runs/results_<tag>.csv, logging to runs/<tag>.log. Never touches the
# baseline probe_llama1b.pkl / _evaluation_results.csv.
set -euo pipefail
cd /home/ankush/Documents/claude_pai_exp
tag="$1"; train="$2"
probe="runs/probe_${tag}.pkl"
res="runs/results_${tag}.csv"
log="runs/${tag}.log"
mkdir -p runs
{
  echo "=== TRAIN ${tag} ($train) start $(date +%T) ==="
  .venv/bin/python high_stakes.py --probe_training_data "$train" --output_probe_path "$probe" 2>&1 | grep -v "it/s\]" | tail -8
  echo "=== EVAL ${tag} start $(date +%T) ==="
  .venv/bin/python evaluation.py --probe_path "$probe" --results_file_name "$res" 2>&1 | grep -v "it/s\]" | tail -15
  echo "=== DONE ${tag} $(date +%T) ==="
  echo "--- RESULTS ${tag} ---"; cat "$res"
} > "$log" 2>&1
echo "finished ${tag}: $res"
