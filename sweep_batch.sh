#!/bin/bash
# Run several (tag, per_domain, w2, wm, wtool) configs sequentially, print summary.
cd /home/ankush/Documents/claude_pai_exp
SEED=initial_training_set/init_seed_hs_ls_200.jsonl
run() {
  tag=$1; pd=$2; wt=$3; wm=$4; wtool=$5
  .venv/bin/python gen_synthetic.py --per_domain "$pd" --w_two "$wt" --w_multi "$wm" --w_tool "$wtool" \
      --include_seed "$SEED" --out initial_training_set/synth_${tag}.jsonl >/dev/null 2>&1
  .venv/bin/python train.py --probe_training_data initial_training_set/synth_${tag}.jsonl \
      --output_probe_path probe_${tag}.pkl >/dev/null 2>&1
  .venv/bin/python evaluation.py --probe_path probe_${tag}.pkl \
      --eval_dataset_save_dir eval_datasets/hs_ls \
      --results_file_name results_${tag}.csv >/dev/null 2>&1
  mean=$(awk -F, '$1=="mean"{print $2}' results_${tag}.csv)
  echo "$tag pd=$pd w=($wt,$wm,$wtool) -> $(python3 -c "print(f'{float('$mean'):.4f}')")"
}
"$@"
