#!/bin/bash
set -e
source /workspace/claude_pai_exp/run_env.sh
cd /workspace/claude_pai_exp
tag=$1; data=$2; seed=$3
.venv/bin/python train.py --model google/gemma-3-27b-it --layer 32 --seed "$seed" \
  --probe_training_data "$data" --pos_class_label harmful_to_human \
  --neg_class_label not_harmful_to_human \
  --concept_description "the conversation is harmful to human" \
  --output_probe_path "probes/probe_${tag}.pkl" \
  --activations_save_path "acts_train/${tag}.pt" > "logs/train_${tag}.log" 2>&1
.venv/bin/python evaluation.py --probe_path "probes/probe_${tag}.pkl" \
  --eval_dataset_save_dir eval_datasets/hu_ha --pos_class_label harmful_to_human \
  --neg_class_label not_harmful_to_human --results_file_name "results/${tag}.csv" \
  --activations_save_path eval_acts_hu_ha/acts_full.pt > "logs/eval_${tag}.log" 2>&1
echo "== $tag =="; cat "results/${tag}.csv"
