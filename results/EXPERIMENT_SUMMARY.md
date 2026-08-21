# harmful_to_human probe — experiment summary

Model/layer: google/gemma-3-27b-it, layer 32 (fixed by the fetched activations).
All AUROC on the held-out **eval** set. Multi-seed rows are mean ± sd across seeds.

## Headline (multi-seed eval mean)

| corpus | rows | eval AUROC | sd | vs baseline |
|---|---|---|---|---|
| baseline (seed only) | 50 | 0.8284 | 0.0263 | — |
| drop A2 (buggy pool) | 596 | 0.8804 | 0.0076 | +0.0520 |
| **v2 = drop A2+N+D+C** | 492 | 0.8920 | 0.0041 | +0.0636 |
| v3 = v2 + red-team pool O | 512 | 0.8716 | 0.0185 | +0.0432 |

## Per-split, baseline vs v2 (eval, multi-seed mean ± sd)

| split | baseline | v2 | Δ |
|---|---|---|---|
| ai_dilemmas | 0.7816 ± 0.0860 | 0.9188 ± 0.0232 | +0.1372 |
| ant_hh | 0.7402 ± 0.0119 | 0.7306 ± 0.0079 | -0.0096 |
| daily_dilemmas | 0.9435 ± 0.0357 | 0.9827 ± 0.0057 | +0.0392 |
| balanced_refusal | 0.8482 ± 0.0157 | 0.9358 ± 0.0073 | +0.0877 |
| mean | 0.8284 ± 0.0263 | 0.8920 ± 0.0041 | +0.0636 |
