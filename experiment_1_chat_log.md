# Experiment 1 — Conversation Log

> Transcript of the chat that produced `basic_experiment_1` (synthetic training-data
> augmentation of the high/low-stakes probe). Saved up to the point before the
> git setup/commit instructions. Assistant tool actions are summarized inline with
> their key outputs.

---

## User

- There is a pretrained probe: `probe_llama1b.pkl`.
- You are not allowed to look into initial training data in `initial_training_set`.
- There evaluation results of this probe in `_evaluation_results.csv`.

Your aim is to improve these results, i.e. increase the mean AUROC eval score results by retraining the probe.

Describe a plan how would you do it?

## Assistant

*(Read `high_stakes.py`, `evaluation.py`, `_evaluation_results.csv`, and listed the repo. Then inspected tuberlens read-only for tunable knobs: probe types, hyperparams, probe metadata.)*

**Current state** — mean **AUROC 0.825**, per dataset:

| dataset | auroc |
|---|---|
| anthropic | 0.877 |
| mts | 0.852 |
| mt | 0.833 |
| toolace | **0.737** ← weakest |

The probe is `linear_then_softmax` on `Llama-3.2-1B-Instruct`, **layer 8**, trained with empty `hyperparams={}` (tuberlens defaults: 200 epochs, lr 5e-3, weight_decay 1e-3). The only things that determine the probe are **which activations** (model, layer, token-pooling) and **how the linear head is fit** (hyperparams, training data). Those are the levers — none require touching the probe *architecture*, reading `eval_datasets/`, or reading `initial_training_set/`.

**Methodological rule:** the failure mode is *tuning on the eval set*. With only 4 eval datasets it's easy to keep retraining until their mean AUROC goes up — that's leakage. So: select layer/hyperparameters on a **validation split carved from the training data**, and touch the eval sets as few times as possible (ideally once, at the end).

**Plan (roughly by payoff/cost):**

1. **Layer sweep** — cheapest, usually biggest lever. Llama-3.2-1B has 16 layers; layer 8 is just a default. Retrain per layer, select on the validation split.
2. **Regularization / fit hyperparameters** — tune `weight_decay`, `epochs`, `lr`, `final_lr` for `linear_then_softmax` via `ProbeSpec` (currently `{}`).
3. **Add training-data diversity (no peeking)** — generate *new* synthetic high/low-stakes conversations from scratch to broaden coverage; `toolace` being weakest suggests thin tool-use/agentic coverage.
4. **Bigger backbone** — point `--model` at `Llama-3.2-3B-Instruct` and sweep its layers (probe pickles its own `model_name`, so eval flows through).
5. **Eval-preprocessing consistency** — `--combine_consecutive_messages` / `--convert_tool_to_assistant` are off by default; verify train/eval formatting agree (fairness fix, not a knob to twist for score).

**Deliverable:** a small sweep runner, a results table (validation-selected config → final eval), and the retrained probe + new CSV for the winning config.

*(Asked two clarifying questions.)*

## User (answers to clarifying questions)

- **Scope:** Add synthetic training data
- **Compute:** GPU available

## Assistant

*(Confirmed GPU: NVIDIA RTX 5060; seed set = 290 lines. Inspected tuberlens `LabelledDataset` loaders read-only to learn the JSONL schema — **not** by reading the training file.)*

**Schema learned:** each JSONL line is `{"inputs": [{"role","content"}...], "labels": "high-stakes"|"low-stakes"}` (optional `ids`); labels map pos→1 / neg→0.

**Approach:** generate ~500 class-balanced synthetic examples where the **same topics appear in both classes** so the probe learns *stakes, not topic* (e.g. medical emergency vs. vitamin question; an $840k fraudulent wire vs. splitting a dinner bill; an agent about to `DROP` a live prod table vs. formatting a markdown table), plus tool-use/agentic transcripts for the weak `toolace` axis. Authored from scratch — never derived from `eval_datasets/` or the seed contents.

Steps taken:

1. **Generated** `scripts/gen_synthetic_stakes.py` → `initial_training_set/synthetic_stakes.jsonl` (500 rows, 250 high / 250 low, 28 high + 30 low base scenarios with light structural augmentation). Verified it parses via `LabelledDataset.load_from` (500 rows, balanced, dialogues → `Message` lists).
2. **Merged** seed + synthetic via shell into `initial_training_set/combined_train.jsonl` (790 rows) — without reading the seed's contents. Verified load: 790 rows, 395/395, all labels mapped.
3. **Retrained** at layer 8, seed 42, to a new path `probe_llama1b_combined.pkl` (clean data-only A/B). Early-stopped at 65 epochs; in-distribution validation AUROC ≈ 1.0 (synthetic split is easily separable).
4. **Evaluated** to `_evaluation_results_combined.csv`.

**Result: mean AUROC 0.825 → 0.846 (+0.021)**

| dataset | baseline | new | Δ |
|---|---|---|---|
| anthropic | 0.877 | **0.916** | +0.039 |
| mt | 0.833 | **0.903** | +0.070 |
| mts | 0.852 | **0.871** | +0.019 |
| toolace | 0.737 | **0.692** | −0.045 |
| **mean** | **0.825** | **0.846** | **+0.021** |

`tpr@fpr=0.01` mean also improved 0.122 → 0.233.

**Promoted** the winner to `probe_llama1b.pkl` / `_evaluation_results.csv`, backing up the originals as `probe_llama1b.baseline.pkl` / `_evaluation_results.baseline.csv`.

**Honest caveat:** `toolace` *regressed* by 0.045 despite adding agentic transcripts — the synthetic tool calls are embedded as pseudo-text in message content, which likely doesn't match toolace's real tool-message formatting, so that data taught a slightly off pattern. The other three sets more than compensated.

Highest-leverage next steps (both within the rules): **(a)** a layer sweep on the combined set; **(b)** fixing the tool-use representation to recover `toolace`.

---

*End of transcript excerpt.*
