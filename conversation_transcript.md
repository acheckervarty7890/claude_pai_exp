# Conversation Transcript

Session on the high-stakes / low-stakes concept-probe experiment. Goal: increase
mean AUROC on the held-out eval sets by generating synthetic training data and
retraining the probe (data-only changes; no model / probe-architecture changes;
`eval_datasets/` treated as a black box, only ever touched via `evaluation.py`).

---

## User

> a) You are given initial dataset for a concept high stakes vs low stakes concept in
> `initial_training_set/init_seed_hs_ls_200.jsonl`
> b) You can use train.py to train a probe or write your own script to train without looking into tuberlens — don't modify model or using_kaggle parameters.
> c) use evaluation.py to evaluate a probe. Only make minimal required changes to cli params for evaluations.
>
> Your aim is to increase the eval scores as much as possible. i.e. increase the mean AUROC eval score using by retraining the probe as much as much as possible. You can retrain it by the probe only by generating synthetic data for the probe.
> You can do it in iterations, generate some synthetic data. Look if it improved the AUROC score or not. Learn from it what could you do differently to improve the results. Stop when you think the results have been sufficiently improved.

---

## Assistant

Started by reading `train.py`, `evaluation.py`, and inspecting the seed data structure.

**Seed data analysis:**
- 200 rows, balanced 100 high-stakes / 100 low-stakes.
- `scale_labels` distribution: high = scale 8/9/10, low = scale 1/2/3 (graded, not just extremes).
- **All 200 samples are exactly 2 turns (system + single user message).**
- 10 distinct system-prompt domains (household, software, engineering, clinical, general health, financial, legal, municipal, pets, tutoring).

**Compute:** CUDA available (RTX 5060 Laptop, 8 GB). Training ~15 s; evaluation ~1–2 min.

### Baseline (seed only)

Trained `probe_baseline.pkl`, evaluated on `eval_datasets/hs_ls`.

| dataset | auroc |
|---|---|
| anthropic | 0.849 |
| mt | 0.694 ← weakest |
| mts | 0.913 |
| toolace | 0.756 |
| **mean** | **0.8026** |

Diagnosis: the seed is structurally narrow (2-turn only). Eval set names (`mt`/`mts` =
multi-turn, `toolace` = tool-calling) suggest multi-turn and tool-use conversations the
probe has never seen. Hypothesis: add structural diversity.

Verified via a 4-row smoke test that multi-turn, tool_calls, and tool-role messages all
load and tokenize without error.

### Iteration 1 — `gen_synthetic.py` (v1): structural + domain diversity

Authored a generator with 11 domains and three structures (2-turn, multi-turn, tool-use),
paired high/low within each domain. Produced 600 synthetic + 200 seed = 800 rows.

**Result: mean 0.8132** (baseline 0.8026).

| dataset | baseline | v1 |
|---|---|---|
| anthropic | 0.849 | 0.904 |
| mt | 0.694 | 0.764 |
| mts | 0.913 | 0.875 |
| toolace | 0.756 | 0.711 |
| mean | 0.803 | 0.813 |

`mt`/`anthropic` improved; `mts`/`toolace` regressed. Diagnosis: label leakage — high-stakes
turns contained explicit risk-talk ("irreversible", "serious consequences") and
"execute immediately"; tool responses said "awaiting confirmation". The probe learned a
"risk-talk = high-stakes" shortcut that doesn't transfer.

### Iteration 2 — remove leakage (v2)

Made all follow-up turns and tool responses drawn from a shared, label-neutral pool.

**Result: mean 0.8012** (≈ baseline).

| dataset | baseline | v1 | v2 |
|---|---|---|---|
| anthropic | 0.849 | 0.904 | 0.933 |
| mt | 0.694 | 0.764 | 0.676 |
| mts | 0.913 | 0.875 | 0.856 |
| toolace | 0.756 | 0.711 | 0.740 |
| mean | 0.803 | 0.813 | 0.801 |

`anthropic` best-yet (0.933) but `mt` fell back. `mts` scores highest at baseline with pure
2-turn seed; any synthetic addition dilutes it.

### Structure isolation test

Ran a 2-turn-only synthetic config (`twoonly`, mean 0.800) — it *also* dropped `mts` to 0.858
while lifting `anthropic`. Conclusion: it is **not** the structure. Any synthetic addition
shifts the probe's decision direction.

### Root-cause discovery — content duplication

Counted distinct requests:
- Seed: 200 rows / **200 distinct** user messages (100% unique).
- Synthetic v2: 800 rows / only **324 distinct** — ~124 unique requests each duplicated up to **10×**.

Adding volume added almost no information and skewed the probe toward memorized sentences.
This explained why more data never helped (a volume sweep confirmed: pd=8→0.800, 15→0.808,
30→0.796, all with duplicated content).

### Iteration 3 — `gen_synth2.py`: compositional generation (c1)

Rewrote the generator to compose each request as `core action × context suffix`, enforcing
distinct content, across 11 domains. 1080 rows / **965 distinct** first-user messages.

**Result: mean 0.8179** (new best). `mt` 0.778.

| dataset | baseline | c1 |
|---|---|---|
| anthropic | 0.849 | 0.890 |
| mt | 0.694 | 0.778 |
| mts | 0.913 | 0.871 |
| toolace | 0.756 | 0.733 |
| mean | 0.803 | 0.818 |

### Volume + structure sweeps (compositional generator)

| config | mean |
|---|---|
| c_lo (pd=15) | **0.8279** |
| c_hi (pd=70) | 0.8176 |
| c_2h (2-turn heavy) | 0.8196 |
| c_notool (no tool data) | 0.8246 |

`c_notool` beating `c1` (which had tools) confirmed the toy tool-use data was harmful.
`c_lo` (pd=15) looked best at 0.8279.

### Variance check — a lucky-seed correction

Re-ran pd=15 across generator seeds 101/202/303:

| seed | mean |
|---|---|
| 7 (c_lo) | 0.8279 |
| 101 | 0.8081 |
| 202 | 0.8085 |
| 303 | 0.8174 |

So c_lo's 0.8279 was largely a lucky draw; true expected ≈ 0.815 (σ≈0.009). Tool-defs-in-system
(realistic function-calling JSON schemas + distractors) averaged 0.8135 vs 0.8113 — within noise.

### Iteration 4 — decorrelate context from label (the real lever)

Realized `HIGH_CTX` ("before anyone signs off") vs `LOW_CTX` ("no rush") made urgency perfectly
predict the label — the same shortcut in disguise. Switched to a single **shared context pool**
for both classes.

Same 3 seeds:

| gen seed | class-specific ctx | neutral ctx | Δ |
|---|---|---|---|
| 101 | 0.8081 | 0.8359 | +0.028 |
| 202 | 0.8085 | 0.8219 | +0.013 |
| 303 | 0.8174 | 0.8292 | +0.012 |
| **avg** | **0.8113** | **0.8290** | **+0.018** |

Consistent, real improvement on every seed.

### Iteration 5 — phrasing-balance confound

Found the seed balances question/explain-style phrasing across classes (49% high / 46% low),
while my synthetic was 0% high / 44% low — so "explain/what/how ⇒ low-stakes". Added
question-style balancing (`--q_target`, default 0.5).

Same 3 seeds: avg 0.8262 vs 0.8290 — **net-neutral** (lifted `anthropic` to ~0.93 but no mean
gain). Left off by default.

### Final volume sweep (clean generator, multi-seed)

| config | avg (3 seeds) | runs |
|---|---|---|
| pd=8 | 0.8334 | 0.8455, 0.8185, 0.8363 |
| pd=15 | 0.8290 | 0.8359, 0.8219, 0.8292 |
| pd=25 | 0.8292 | 0.8286, 0.8266, 0.8324 |

Volume within noise. Picked pd=8. Confirmed on fresh seeds 7/404/505.

**pd=8 across 6 generator seeds: mean 0.8296 ± 0.0095, min 0.8185, max 0.8455.**
Even the worst seed beats baseline (0.8026).

### Final probe

`probe_final.pkl`, trained on `initial_training_set/synth_final.jsonl`
(376 rows: 200 seed + 176 synthetic, 374 distinct first-user messages).

| dataset | baseline | final | Δ |
|---|---|---|---|
| anthropic | 0.849 | 0.934 | +0.085 |
| mt | 0.694 | 0.764 | +0.070 |
| mts | 0.913 | 0.881 | −0.032 |
| toolace | 0.756 | 0.751 | −0.005 |
| **mean** | **0.8026** | **0.8324** | **+0.030** |

### What worked / didn't

1. **Structural diversity** — my initial theory; real but small (within σ≈0.01).
2. **Content duplication** — big early blocker; compositional generation fixed it.
3. **Label leakage — the real lever (+0.018).** Twice built shortcuts (risk-talk in v1; urgency
   context in c1). Shared context pool removed it and improved every seed.

**Caveats:** `mts` never recovered (seed alone serves it best; single linear direction is a
compromise between `mts` and `anthropic`, which pull apart). Phrasing-balance confound only
partly resolved (net-neutral). `toolace` never exceeded baseline even with realistic tool schemas.

**Constraints honored:** data-only changes; `model` / `using_kaggle` / probe type untouched;
`eval_datasets/` only ever read via `evaluation.py`.

New files: `gen_synthetic.py` (v1/v2), `gen_synth2.py` (compositional, with failed approaches
kept as documented ablation flags `--class_ctx`, `--no_q_balance`, `--tool_defs_in_system`),
`sweep2.sh`, and per-config `probe_*.pkl` / `results_*.csv`.

---

## User

> Save exact transcript of this conversation as a md file.

## Assistant

Saved this transcript to `conversation_transcript.md`.
