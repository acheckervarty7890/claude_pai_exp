# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A small experiment harness that uses **[tuberlens](https://github.com/blandfort/tuberlens)** (an activation-probing library) to **train and evaluate a "high-stakes vs. low-stakes" probe** on a HuggingFace LLM's hidden activations. It is two scripts plus downloaded eval data — the modeling machinery lives entirely in tuberlens.

tuberlens is a **consumed dependency, installed editable from `~/Documents/tuberlens`** (branch `iterative_pipeline_2`) into `.venv`. Do not edit the tuberlens source as part of work here; treat it as a read-only library.

## Setup & commands

No `uv`/`pip` on the system Python; use the project venv directly (Python 3.12, tuberlens + torch already installed):

```bash
.venv/bin/python high_stakes.py [args]     # train a probe
.venv/bin/python evaluation.py [args]      # evaluate a trained probe
```

Requires a `HF_TOKEN` (the default model `meta-llama/Llama-3.2-1B-Instruct` is gated). It lives in the project-root **`.env`** (git-ignored / secret — do not commit or echo it). Both scripts call `load_dotenv()` at import so the `.env` is picked up automatically; note that **tuberlens does not load a `.env` on its own** when used as a library (`hf_login()` only reads `os.getenv("HF_TOKEN")`), so this `load_dotenv()` in the scripts is what makes the token reach it. A CUDA GPU is used automatically when available (else CPU + float32).

## Workflow: train → evaluate

The two scripts form a pipeline connected by a pickled `Probe` file.

1. **`high_stakes.py`** — trains and pickles a probe.
   - Loads training data with `LabelledDataset.load_from(...)`, splits via `create_train_test_split` (optional `--split` field), then calls `tuberlens.training.train_probe`.
   - Fixed choices baked into the script: probe type **`linear_then_softmax`**, classes `pos="high-stakes"` / `neg="low-stakes"`. Model and probing layer are CLI args (defaults: `Llama-3.2-1B-Instruct`, layer `8`).
   - Output: a `pickle` of the trained probe (default `probe_llama1b.pkl`). The probe object carries its own `model_name`, `layer`, and class labels — evaluation relies on that metadata.

2. **`evaluation.py`** — loads a pickled probe and scores it against local eval sets.
   - Unpickles the probe, reloads its model (`LLMModel.load(probe.model_name)`), then **loads eval datasets from the local `--eval_dataset_save_dir`** (default: the project-local `eval_datasets/`). It globs every `*.jsonl` in that directory and loads each via `LabelledDataset.load_from`, using the filename stem as the dataset name — so it evaluates whatever files are present. It runs `tuberlens.evaluation.get_performances` and writes a CSV.
   - Also defines `seed_everything(seed)`, which `high_stakes.py` imports — so the two files are coupled; keep that import intact.

## Repo layout

- `high_stakes.py` — training entry point.
- `evaluation.py` — evaluation entry point + shared `seed_everything`.
- `eval_datasets/` — held-out eval sets consumed only by `evaluation.py`. **Do not inspect these files** (see the rule below).
- `.venv/` — project virtualenv with tuberlens installed editable.
- Probe pickles (`*.pkl`) are produced by training and consumed by evaluation; paths are CLI-controlled.

## Hard rule: `eval_datasets/` is a black box

Never open, read, `cat`, `grep`, sample, or otherwise inspect the contents of any file in `eval_datasets/`. It is a held-out evaluation set that must stay uncontaminated. The **only** allowed interaction is running `evaluation.py`, which reads the files internally and outputs aggregate metrics. Do not copy dataset contents, names, or sample counts into code, docs, comments, logs, or commit messages. (Listing filenames for plumbing is fine; reading their contents is not.)

## Notes for changes

- Keep the `pos="high-stakes"` / `neg="low-stakes"` labels consistent between the two scripts and the probe metadata — evaluation loads eval datasets with these same labels.
- Evaluation reads local files only; to add/remove eval datasets, drop `*.jsonl` files into `eval_datasets/` (or point `--eval_dataset_save_dir` elsewhere) — there is no download step or split selector anymore.
