# High-stakes probe: results

AUROC per eval family, one column per training set. Split stems are hashed in the repo; the family names come from the fetch manifest's split names, whose row counts match the label files.

## Held-out eval (`eval_datasets/highstakes`)

| family | base | v1 | v2 | v3 | v5 |
|---|---|---|---|---|---|
| anthropic_hh | 0.9468 | 0.9801 | 0.9764 | 0.9732 | 0.9778 |
| multi_turn | 0.8541 | 0.9020 | 0.9522 | 0.9670 | 0.9740 |
| clinical | 0.9424 | 0.9456 | 0.9308 | 0.9465 | 0.9708 |
| toolace | 0.8557 | 0.8764 | 0.8917 | 0.8805 | 0.8863 |
| MEAN | 0.8997 | 0.9260 | 0.9378 | 0.9418 | 0.9522 |

## Tuning set (`dev_samples/highstakes`)

| family | base | v1 | v2 | v3 | v5 |
|---|---|---|---|---|---|
| anthropic_hh | 0.9401 | 0.9703 | 0.9655 | 0.9652 | 0.9668 |
| multi_turn | 0.8860 | 0.9383 | 0.9510 | 0.9659 | 0.9745 |
| clinical | 0.8818 | 0.9185 | 0.9214 | 0.9302 | 0.9398 |
| toolace | 0.8649 | 0.8960 | 0.9011 | 0.8912 | 0.9055 |
| MEAN | 0.8932 | 0.9308 | 0.9348 | 0.9381 | 0.9466 |

## Training sets

| run | file | rows | high | low |
|---|---|---|---|---|
| base | `initial_training_set/init_seed_hs_ls_50.jsonl` | 50 | 25 | 25 |
| v1 | `training_sets/train_v1.jsonl` | 283 | 141 | 142 |
| v2 | `training_sets/train_v2.jsonl` | 427 | 213 | 214 |
| v3 | `training_sets/train_v3.jsonl` | 569 | 284 | 285 |
| v5 | `training_sets/train_v5.jsonl` | 949 | 474 | 475 |
| v6 | `training_sets/train_v6.jsonl` | 1007 | 503 | 504 |
