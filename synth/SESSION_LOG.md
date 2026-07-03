# Session log — improving the high/low-stakes probe via synthetic data

Date: 2026-07-03

## Task (as given)

- A pretrained probe existed: `probe_llama1b.pkl`.
- Baseline evaluation results were in `_evaluation_results.csv`.
- Allowed to look at only 2–3 examples from `initial_training_set/` to learn the data format.
- **Goal:** increase the **mean AUROC** eval score by **retraining the probe using synthetic training data only**.
- **Method emphasis:** red-team the probe — generate examples where the probe fails to identify
  the correct label — iterate, learn what works, and stop when results are sufficiently improved.

## Constraints respected

- Never inspected `eval_datasets/` (held-out black box) — only ran `evaluation.py` and read aggregate AUROC.
- Trained with the repo's `high_stakes.py`; evaluated with `evaluation.py`. Did not inspect tuberlens internals.
- Probe architecture left fixed (`linear_then_softmax`), layer fixed at default `8`, labels
  `high-stakes` / `low-stakes` unchanged. Improvements came entirely from added synthetic data.

## Data format (learned from 2 seed examples)

JSONL records shaped like:

```json
{"inputs": "<json-string of [{\"role\":..., \"content\":...}, ...]>",
 "ids": "hs_3", "pair_id": 3, "labels": "high-stakes"}
```

`inputs` is a JSON-encoded chat transcript; `labels` maps to 1 (high) / 0 (low). The seed set
was 290 balanced samples (145/145) of fairly narrow `system + user` software-development prompts,
built as matched pairs (same topic, different stakes) keyed by `pair_id`.

## Approach

Generate diverse synthetic data as **matched high/low-stakes pairs on the same topic**, so the
probe keys on *consequence of error* rather than topic vocabulary. Vary conversation **structure**
(single-user, `system+user`, multi-turn, and tool/function-call transcripts) to cover the eval
distribution. Add each new batch on top of the champion, retrain, re-evaluate, keep what helps.

Red-teaming was done at the design level (build the kinds of inputs the probe most likely mislabels:
domain shift, multi-turn, tool-use, boundary cases) and empirically by watching per-dataset AUROC to
see which distribution the probe was failing on (consistently `toolace`).

## Iterations & results (mean AUROC)

| ver | training mix | mean | note |
|-----|--------------|------|------|
| base | init_seed only (pretrained) | **0.8250** | starting point |
| v1 | + diverse NL matched pairs (`synth_v1`) | 0.8594 | biggest single jump (+0.034) |
| **v2** | + clear-cut tool calls (`synth_tools_v2`) | **0.8635** | **champion** |
| v3 | + realistic read/write tool pairs (`synth_tools_v3`) | 0.8399 | regressed — hurt `mt` |
| v4 | v2 base + expanded NL (`synth_general_v4`) | 0.8628 | tie with v2 |
| v5 | kitchen sink (all of the above) | 0.8444 | dragged down by v3 data |

Per-dataset AUROC:

| set | base | v1 | v2 (★) | v3 | v4 | v5 |
|-----|------|----|--------|----|----|----|
| anthropic | 0.8774 | 0.9326 | 0.9386 | 0.9214 | 0.9356 | 0.9268 |
| mt | 0.8331 | 0.8932 | 0.8867 | 0.8140 | 0.8767 | 0.8264 |
| mts | 0.8520 | 0.8771 | 0.8746 | 0.8834 | 0.8789 | 0.8790 |
| toolace | 0.7374 | 0.7346 | 0.7542 | 0.7408 | 0.7599 | 0.7455 |
| **mean** | **0.8250** | 0.8594 | **0.8635** | 0.8399 | 0.8628 | 0.8444 |

## What each iteration taught me

1. **v1 — breadth of natural-language domains + multi-turn** gave the largest gain. The seed set was
   narrow (software-dev `system+user`); adding medical/finance/security/legal/safety matched pairs and
   multi-turn structure generalized well across `anthropic`, `mt`, `mts`.
2. **v2 — clear-cut tool/function-call transcripts** (transfer $85k, DROP TABLE vs. get weather / find
   recipe, across 3 call notations) targeted the weak `toolace` set and nudged the mean to the peak.
3. **v3 — realistic "read = low / write = high" tool pairs regressed the mean.** That rigid heuristic
   conflicts with how the eval sets judge stakes and injected label noise; `mt` fell 0.887 → 0.814.
   Lesson: *more tool data is not monotonically better; label fidelity matters more than volume.*
4. **v4 — more diverse NL** was a statistical tie with v2 (traded a little `mt` for `toolace`/`mts`).
5. **v5 — union of everything** underperformed because it re-included the harmful v3 data.

**Stopping criterion:** a real plateau — two independent expansions (v3, v4) and their union (v5) all
failed to beat v2, and `toolace` (~0.75) anchors the mean given the layer-8 1B probe.

## Final outcome

- **Mean AUROC 0.8250 → 0.8635 (+0.0385).** Every eval set improved:
  anthropic 0.877→0.939, mt 0.833→0.887, mts 0.852→0.875, toolace 0.737→0.754.
- Winning recipe: `initial_training_set/init_seed.jsonl` + `synth/synth_v1.jsonl` + `synth/synth_tools_v2.jsonl`
  (= `synth/train_v2.jsonl`).

## Deliverables in the repo

- `probe_llama1b.pkl` — replaced with the improved **v2** probe.
- `_evaluation_results.csv` — refreshed to the v2 numbers (mean 0.8635).
- `synth/` — full reproducible trail:
  - generators: `gen_synth.py` (v1), `gen_tools.py` (v2), `gen_tools_v3.py` (v3), `gen_general_v4.py` (v4)
  - synthetic data: `synth_v1.jsonl`, `synth_tools_v2.jsonl`, `synth_tools_v3.jsonl`, `synth_general_v4.jsonl`
  - combined training sets: `train_v1..v5.jsonl`
  - per-version probes/results/logs: `probe_v*.pkl`, `results_v*.csv`, `*.log`
  - backups of the originals: `probe_baseline_backup.pkl`, `results_baseline_backup.csv`

## Reproduce the champion

```bash
cat initial_training_set/init_seed.jsonl synth/synth_v1.jsonl synth/synth_tools_v2.jsonl > synth/train_v2.jsonl
.venv/bin/python high_stakes.py --probe_training_data synth/train_v2.jsonl --output_probe_path probe_llama1b.pkl
.venv/bin/python evaluation.py --probe_path probe_llama1b.pkl --results_file_name _evaluation_results.csv
```

## Possible next steps (not done)

- Longer multi-tool-call transcripts to push `toolace` (kept short here; more tool data risked `mt`).
- Layer sweep (`--layer`) — a legitimate CLI knob, but outside the "synthetic-data-only" framing of this task.
