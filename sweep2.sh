#!/bin/bash
# Sweep configs for the compositional generator (gen_synth2.py).
# Usage: sweep2.sh <tag> <per_domain> <w2> <wm> <wtool> [gen_seed] [extra_gen_flags...]
cd /home/ankush/Documents/claude_pai_exp
SEED=initial_training_set/init_seed_hs_ls_200.jsonl
tag=$1; pd=$2; wt=$3; wm=$4; wtool=$5; gseed=${6:-7}; shift 6 2>/dev/null || shift 5
extra="$@"
.venv/bin/python gen_synth2.py --per_domain "$pd" --w_two "$wt" --w_multi "$wm" --w_tool "$wtool" \
    --seed "$gseed" $extra \
    --include_seed "$SEED" --out initial_training_set/synth_${tag}.jsonl >/dev/null 2>&1
.venv/bin/python train.py --probe_training_data initial_training_set/synth_${tag}.jsonl \
    --output_probe_path probe_${tag}.pkl >/dev/null 2>&1
.venv/bin/python evaluation.py --probe_path probe_${tag}.pkl \
    --eval_dataset_save_dir eval_datasets/hs_ls \
    --results_file_name results_${tag}.csv >/dev/null 2>&1
mean=$(awk -F, '$1=="mean"{printf "%.4f", $2}' results_${tag}.csv)
per=$(awk -F, 'NR>1&&$1!="mean"{printf "%s=%.3f ", $1, $2}' results_${tag}.csv)
echo "$tag pd=$pd w=($wt,$wm,$wtool) gseed=$gseed $extra -> MEAN $mean | $per"
