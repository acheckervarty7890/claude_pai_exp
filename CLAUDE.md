# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A small experiment harness that uses **[tuberlens](https://github.com/blandfort/tuberlens)** (an activation-probing library) to **train and evaluate a "concept probe"** — a binary classifier of a labelled concept — on a HuggingFace LLM's hidden activations. It is two entry-point scripts plus local data, with the modeling machinery living entirely in tuberlens.

The harness is **concept-agnostic**: a concept is a positive-vs-negative distinction defined entirely by its data (the `labels` field in the JSONL) plus the class labels and description you pass on the command line — no code is concept-specific. Three concepts ship, each with a training seed, a dev set and an eval set:

| concept | positive / negative label | training seed | dev | eval |
|---|---|---|---|---|
| **high-stakes** | `high-stakes` / `low-stakes` | `initial_training_set/init_seed_hs_ls_50.jsonl` | `dev_samples/highstakes/` | `eval_datasets/highstakes/` |
| **harmful-to-human** | `harmful_to_human` / `not_harmful_to_human` | `initial_training_set/init_seed_hu_ha_50.jsonl` | `dev_samples/hu_ha/` | `eval_datasets/hu_ha/` |
| **follows-instructions** | `assistant_follows_the_instruction` / `assistant_does_not_follow_the_instruction` | `initial_training_set/init_seed_instructions_50.jsonl` | `dev_samples/instructions/` | `eval_datasets/instructions/` |

Each seed is 50 balanced rows of `{"inputs": ..., "labels": ...}`. The seed file names do not match the dev/eval directory names (`init_seed_hs_ls_50` ↔ `highstakes`, `init_seed_instructions_50` ↔ `instructions`), so copy the paths rather than guessing them. Keep a concept's three pieces together, and pass the same class labels to both scripts.

The training seeds carry full conversation text. **The dev and eval sets carry labels only** — their activations are precomputed and downloaded (see below), so both scripts need an activation cache to use them.

tuberlens is a **consumed dependency, installed editable from `~/Documents/tuberlens`** (branch `iterative_pipeline_2`) into `.venv`. Do not edit the tuberlens source as part of work here; treat it as a read-only library.

## Setup

No `uv`/`pip` on the system Python; use the project venv directly (Python 3.12, tuberlens + torch already installed):

```bash
.venv/bin/python train.py [args]
.venv/bin/python evaluation.py [args]
```

Requires a `HF_TOKEN` (the default model `meta-llama/Llama-3.2-1B-Instruct` is gated). It lives in the project-root **`.env`** (git-ignored / secret — do not commit or echo it). Both scripts call `load_dotenv()` at import so the `.env` is picked up automatically; note that **tuberlens does not load a `.env` on its own** when used as a library (`hf_login()` only reads `os.getenv("HF_TOKEN")`), so this `load_dotenv()` in the scripts is what makes the token reach it. A CUDA GPU is used automatically when available (else CPU + float32).

Fetching activations additionally needs the `kaggle` package and `KAGGLE_CONFIG_DIR` pointing at the **directory** holding `kaggle.json` (not the file itself), or `KAGGLE_API_TOKEN`.

## The run: fetch → train → evaluate

Three steps for a concept. The example is `instructions`; swap the paths and labels from the table above for the others.

### 1. Fetch the dev and eval activations

`fetch_kaggle_eval_activations.py` downloads the precomputed activations for a concept. Its whole interface is the concept name — `--list` shows what is available.

```bash
.venv/bin/python fetch_kaggle_eval_activations.py --concept instructions_dev  --cache-dir dev_activations_instructions
.venv/bin/python fetch_kaggle_eval_activations.py --concept instructions_eval --cache-dir eval_activations_instructions
```

Use **separate** `--cache-dir`s for `_dev` and `_eval`. A cache is keyed by split name alone, and a concept may use the same split names for both — sharing one directory would let them overwrite each other.

A cache holds one blob per split, `<split>-acts_full.pt`, which is exactly the path tuberlens derives from an `activations_save_path` via `Path(save_path).with_stem(f"{name}-{stem}")`. Blobs are matched to dev/eval files by name; a blob carries no labels and no ids, so **within a file the join is positional** — row *i* of the labels belongs to row *i* of the blob. Never sort or reorder rows in `dev_samples/` or `eval_datasets/`.

### 2. Train, validating against the dev activations

```bash
.venv/bin/python train.py \
  --probe_training_data initial_training_set/init_seed_instructions_50.jsonl \
  --pos_class_label assistant_follows_the_instruction \
  --neg_class_label assistant_does_not_follow_the_instruction \
  --concept_description "the assistant follows the instruction" \
  --validation_data dev_samples/instructions \
  --validation_activations_dir dev_activations_instructions \
  --activations_save_path activations/instructions_acts.pt \
  --output_probe_path probe_instructions.pkl
```

`--validation_data` (one or more `*.jsonl`, or a directory of them) makes the **whole** seed the training set and the dev samples the validation set; several files are concatenated. Without it, `train.py` falls back to carving a validation slice out of the seed via `create_train_test_split`.

`--validation_activations_dir` supplies the dev activations, and is required whenever the dev samples are labels-only — otherwise `train.py` refuses rather than running the model over empty inputs. It also needs `--activations_save_path`, because `train_probe` recomputes validation activations unconditionally and the only lever is the path it reads: `with_stem(f"val-{stem}")` of `--activations_save_path`. The dev blob is staged there (symlinked for one split, concatenated for several) so tuberlens finds it instead of running the model.

Training itself always loads the extraction model — the training seed is raw text.

Other knobs: `--model` and `--layer` (defaults `Llama-3.2-1B-Instruct`, layer `8`), `--seed`. The probe type is baked in as **`linear_then_softmax`** — not a CLI arg, and do not change it. `--split` names a field to group the seed split by; the current seeds have no such field, so leave it unset.

### 3. Evaluate against the eval activations

```bash
.venv/bin/python evaluation.py \
  --probe_path probe_instructions.pkl \
  --eval_dataset_save_dir eval_datasets/instructions \
  --activations_cache_dir eval_activations_instructions \
  --pos_class_label assistant_follows_the_instruction \
  --neg_class_label assistant_does_not_follow_the_instruction \
  --results_file_name results_instructions.csv
```

`--eval_dataset_save_dir` globs every `*.jsonl` **directly** in that directory (non-recursively), using each filename stem as the dataset name, so point it at the concept's subdirectory — the baked-in default (`eval_datasets/`) has no files at its top level and finds nothing.

`--activations_cache_dir` attaches each blob to its dataset up front. A dataset that already carries `activations` is handed straight to the probe by `get_performances`, so the extraction model is never loaded at all — the point of reusing gemma-3-27b activations rather than recomputing them. A missing blob is a hard error unless `--allow_missing_cached_activations`.

Class labels must match both the eval data's `labels` values and what the probe was trained with. Output is a CSV, one row per split plus a `mean` row (auroc, accuracy, tpr_at_fpr).

Every blob is validated before use against the probe's `model_name` / `layer` and the dataset's row count, and refused on a mismatch.

## Memory pinning: `MAX_MEMORY`

**`MAX_MEMORY` is the environment variable to set for memory pinning.** It is accelerate's per-device budget, in the compact form `MAX_MEMORY="0=21GiB,cpu=45GiB"` (GPU keys are ordinals, plus `cpu` / `disk`). With `device_map="auto"` the model is placed layer by layer until a device's budget runs out and the rest is offloaded. Left unset, accelerate infers the budget from whatever is *free at load time*, so a busy or fragmented GPU can silently push weights all the way to **disk** offload — orders of magnitude slower than CPU offload. Pinning it also makes placement reproducible across loads.

Related settings, same mechanism:

- `MODEL_MAX_MEMORY` — per-model override, a JSON object keyed by model name, e.g. `MODEL_MAX_MEMORY='{"google/gemma-3-27b-it": "0=21GiB,cpu=45GiB"}'`. It wins over `MAX_MEMORY`.
- `OFFLOAD_BUFFERS` — default true; keeps buffers with the weights they belong to. Required once layers are offloaded, or accelerate warns about GPU buffer space and risks an OOM.

**Ordering matters.** tuberlens builds its settings object from `os.environ` at *import* time, and it does **not** read a `.env` itself. So `load_dotenv()` has to run before the `tuberlens` imports — which is why in both `train.py` and `evaluation.py` it sits above them (with `# noqa: E402`). Do not move the tuberlens imports back above `load_dotenv()`: a `MAX_MEMORY` in `.env` would be read too late and silently ignored. Exporting it in the shell (`MAX_MEMORY="0=21GiB,cpu=45GiB" .venv/bin/python train.py ...`) works either way.

Neither variable matters when the activation caches cover every split, since no extraction model is loaded for them.

## Repo layout

- `train.py` — training entry point (concept-agnostic).
- `evaluation.py` — evaluation entry point. Also holds `seed_everything` and the activation-cache helpers (`build_blob_index`, `read_activation_blob`, `validate_activation_blob`, `attach_cached_activations`) that `train.py` imports — the two files are coupled; keep those imports intact.
- `fetch_kaggle_eval_activations.py` — standalone downloader for the precomputed dev/eval activations; imports nothing from this repo, so it can be copied to a bare box on its own.
- `initial_training_set/` — one training seed per concept, selected via `--probe_training_data`. Readable (not a black box).
- `dev_samples/` — held-out dev sets, per-concept subdirectories, used as the training validation set via `--validation_data`. **Do not inspect** (see the rule below).
- `eval_datasets/` — held-out eval sets, per-concept subdirectories, consumed only by `evaluation.py`. **Do not inspect** (see the rule below).
- `.venv/` — project virtualenv with tuberlens installed editable.
- Probe pickles (`*.pkl`) are produced by training and consumed by evaluation; paths are CLI-controlled. The probe object carries its own `model_name`, `layer`, class labels and description, and evaluation relies on that metadata.

## Adding a concept

No code changes. Drop a training seed into `initial_training_set/`, add the concept's dev and eval subdirectories, publish its activations under a `<name>_dev` / `<name>_eval` concept, and pass the new paths and class labels on both command lines.

## Hard rule: `eval_datasets/` and `dev_samples/` are a black box

Never open, read, `cat`, `grep`, sample, or otherwise inspect the contents of any file in `eval_datasets/` or `dev_samples/`. They are held-out sets that must stay uncontaminated. The **only** allowed interaction is running `train.py` / `evaluation.py`, which read the files internally and output aggregate metrics. Do not copy their contents, names, or sample counts into code, docs, comments, logs, or commit messages. (Listing filenames for plumbing is fine; reading their contents is not.)

## Hard rule: the tuberlens library is off-limits to read

Never open, read, `cat`, `grep`, browse, or otherwise inspect the tuberlens source — not in `~/Documents/tuberlens`, not the installed copy under `.venv/`, and not via its repo on the web. Treat it as an opaque, read-only dependency: use it strictly through the public API already exercised by `train.py` and `evaluation.py`. Do not go digging through its internals to discover functions, arguments, or behavior. If something about tuberlens is unclear, rely on this repo's two scripts and their existing usage rather than reading the library. (This is stricter than the "don't edit tuberlens" note above — you may not even look inside it.)
