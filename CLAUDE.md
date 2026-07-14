# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A small experiment harness that uses **[tuberlens](https://github.com/blandfort/tuberlens)** (an activation-probing library) to **train and evaluate a "concept probe"** — a binary classifier of a labelled concept — on a HuggingFace LLM's hidden activations. It is two scripts plus local data — per-concept training seeds in `initial_training_set/` and held-out eval sets in `eval_datasets/` — with the modeling machinery living entirely in tuberlens.

The harness is **concept-agnostic**: a concept is a positive-vs-negative distinction defined entirely by its data (the `labels` field in the JSONL) plus the class labels and description you pass on the command line — no code is concept-specific. New concepts are added just by dropping in data (see "Adding a concept" below). Two concepts currently ship, each with its own training seed and a matching eval subdirectory:

- **`hs_ls`** — high-stakes vs. low-stakes conversations (labels `high-stakes` / `low-stakes`).
- **`hu_ha`** — harmful-to-human vs. not-harmful-to-human conversations (labels `harmful_to_human` / `not_harmful_to_human`).

Keep a concept's training seed and eval subdirectory paired: train on its seed, then evaluate on its subdirectory using the same class labels.

tuberlens is a **consumed dependency, installed editable from `~/Documents/tuberlens`** (branch `iterative_pipeline_2`) into `.venv`. Do not edit the tuberlens source as part of work here; treat it as a read-only library.

## Setup & commands

No `uv`/`pip` on the system Python; use the project venv directly (Python 3.12, tuberlens + torch already installed):

```bash
.venv/bin/python train.py [args]     # train a probe
.venv/bin/python evaluation.py [args]      # evaluate a trained probe
```

Requires a `HF_TOKEN` (the default model `meta-llama/Llama-3.2-1B-Instruct` is gated). It lives in the project-root **`.env`** (git-ignored / secret — do not commit or echo it). Both scripts call `load_dotenv()` at import so the `.env` is picked up automatically; note that **tuberlens does not load a `.env` on its own** when used as a library (`hf_login()` only reads `os.getenv("HF_TOKEN")`), so this `load_dotenv()` in the scripts is what makes the token reach it. A CUDA GPU is used automatically when available (else CPU + float32).

## Workflow: train → evaluate

The two scripts form a pipeline connected by a pickled `Probe` file.

1. **`train.py`** — trains and pickles a probe for whichever concept you point it at.
   - Loads training data with `LabelledDataset.load_from(...)`, splits via `create_train_test_split` (optional `--split` field), then calls `tuberlens.training.train_probe`.
   - The concept is chosen entirely via CLI args: `--probe_training_data` (path to the seed in `initial_training_set/`), `--pos_class_label` / `--neg_class_label` (must match the data's `labels` values), and `--concept_description` (a phrase used to build the stored probe description). All default to the `hs_ls` concept, so training a different concept means overriding these four.
   - Baked-in (not a CLI arg): probe type **`linear_then_softmax`** — do not change it. Model and probing layer are CLI args (defaults: `Llama-3.2-1B-Instruct`, layer `8`).
   - Output: a `pickle` of the trained probe (default `probe_llama1b.pkl`). The probe object carries its own `model_name`, `layer`, class labels, and description — evaluation relies on that metadata.

2. **`evaluation.py`** — loads a pickled probe and scores it against local eval sets.
   - Unpickles the probe, reloads its model (`LLMModel.load(probe.model_name)`), then **loads eval datasets from the local `--eval_dataset_save_dir`**. It globs every `*.jsonl` **directly in that directory** (non-recursively) and loads each via `LabelledDataset.load_from`, using the filename stem as the dataset name — so it evaluates whatever files are present. It runs `tuberlens.evaluation.get_performances` and writes a CSV.
   - `eval_datasets/` is split into a per-concept subdirectory each (`eval_datasets/hs_ls/`, `eval_datasets/hu_ha/`); there are no `*.jsonl` at the top level. Because the glob is non-recursive, point `--eval_dataset_save_dir` at the subdirectory for the concept you trained on (e.g. `eval_datasets/hs_ls`) — the baked-in default (`eval_datasets/`) now finds nothing.
   - Class labels come from `--pos_class_label` / `--neg_class_label` (defaulting to the `hs_ls` concept); they must match both the eval data's `labels` values and the labels the probe was trained with. Pass the same labels you trained with.
   - Also defines `seed_everything(seed)`, which `train.py` imports — so the two files are coupled; keep that import intact.

## Repo layout

- `train.py` — training entry point (concept-agnostic).
- `evaluation.py` — evaluation entry point + shared `seed_everything`.
- `initial_training_set/` — probe training seeds, one `*.jsonl` per concept (`init_seed_hs_ls_200.jsonl`, `init_seed_hu_ha_200.jsonl`); selected via `--probe_training_data`. Readable (not a black box).
- `eval_datasets/` — held-out eval sets consumed only by `evaluation.py`, organized into per-concept subdirectories (`hs_ls/`, `hu_ha/`). **Do not inspect these files** (see the rule below).
- `.venv/` — project virtualenv with tuberlens installed editable.
- Probe pickles (`*.pkl`) are produced by training and consumed by evaluation; paths are CLI-controlled.

## Hard rule: `eval_datasets/` is a black box

Never open, read, `cat`, `grep`, sample, or otherwise inspect the contents of any file in `eval_datasets/`. It is a held-out evaluation set that must stay uncontaminated. The **only** allowed interaction is running `evaluation.py`, which reads the files internally and outputs aggregate metrics. Do not copy dataset contents, names, or sample counts into code, docs, comments, logs, or commit messages. (Listing filenames for plumbing is fine; reading their contents is not.)

## Hard rule: the tuberlens library is off-limits to read

Never open, read, `cat`, `grep`, browse, or otherwise inspect the tuberlens source — not in `~/Documents/tuberlens`, not the installed copy under `.venv/`, and not via its repo on the web. Treat it as an opaque, read-only dependency: use it strictly through the public API already exercised by `train.py` and `evaluation.py`. Do not go digging through its internals to discover functions, arguments, or behavior. If something about tuberlens is unclear, rely on this repo's two scripts and their existing usage rather than reading the library. (This is stricter than the "don't edit tuberlens" note above — you may not even look inside it.)
