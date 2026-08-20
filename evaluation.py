"""Evaluate a trained concept probe against local eval datasets.

The eval sets ship as labels only, paired with precomputed activations, so the
normal path is ``--activations_cache_dir``: blobs fetched by
``fetch_kaggle_eval_activations.py`` are attached to the datasets up front and the
extraction model is never loaded. Without a cache the model is loaded and run over
the eval inputs instead — fine for a split that still carries its text, refused for
one that does not.

MEMORY PINNING
--------------
When the extraction model *is* loaded, how it is split across GPU/CPU is pinned by
the ``MAX_MEMORY`` environment variable (per-device budget handed to accelerate),
in the compact form ``MAX_MEMORY="0=21GiB,cpu=45GiB"``. Left unset, accelerate
infers the budget from whatever is free at load time and can silently spill layers
to disk offload. ``MODEL_MAX_MEMORY`` overrides it per model name (JSON object) and
``OFFLOAD_BUFFERS`` (default true) keeps buffers with the weights they belong to.

These are read by tuberlens at *import* time, so ``load_dotenv()`` has to run before
the tuberlens imports below — which is why it sits where it does. Setting them in
the shell (``MAX_MEMORY=... .venv/bin/python evaluation.py ...``) works either way.
"""

import argparse
import hashlib
import pickle
import random
from pathlib import Path as PATH

import numpy as np
import torch
from dotenv import load_dotenv

# Load HF_TOKEN, MAX_MEMORY and any other secrets/settings from the project-root .env.
# override=True so the .env value wins over any stale value in the shell env.
# This MUST run before the tuberlens imports: tuberlens.config builds its
# `global_settings` (MAX_MEMORY, MODEL_MAX_MEMORY, OFFLOAD_BUFFERS, DTYPE, ...) from
# os.environ at import time, so a .env loaded afterwards would arrive too late.
load_dotenv(override=True)

from tuberlens.interfaces.dataset import LabelledDataset  # noqa: E402

# The three tensor fields a tuberlens activation blob carries, and the field names
# `LabelledDataset.assign` expects for them.
ACTIVATION_FIELDS = ("activations", "attention_mask", "input_ids")

# Default file name of a fetched activation cache; the per-split blobs beside it are
# named "<split>-acts_full.pt" — the exact path tuberlens' get_performances derives
# via Path(save_path).with_stem(f"{name}-{stem}").
DEFAULT_CACHE_STEM = "acts_full.pt"


def seed_everything(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True  # type: ignore
    torch.backends.cudnn.benchmark = False  # type: ignore


def cached_activation_path(cache_dir, name: str, cache_stem: str = DEFAULT_CACHE_STEM):
    """Path a split's cached activations live at, matching tuberlens' naming.

    tuberlens derives a per-dataset save path as
    ``Path(save_path).with_stem(f"{name}-{stem}")``; the fetch script writes its blobs
    to that same layout, so both sides agree without either knowing about the other.
    """
    stem = PATH(cache_stem)
    return PATH(cache_dir) / f"{name}-{stem.stem}{stem.suffix or '.pt'}"


def blob_keys(split: str) -> tuple[str, str]:
    """The two names a label file may use for ``split``.

    A blob is named after the split it holds (``<split>-acts_full.pt``); a label file
    is named either the same way or by a short stable key derived from it. Both are
    accepted so the cache resolves either way.
    """
    return split, hashlib.sha256(split.encode("utf-8")).hexdigest()[:12]


def build_blob_index(cache_dir, cache_stem: str = DEFAULT_CACHE_STEM) -> dict:
    """Index a fetched activation cache under every name a dataset might carry."""
    cache_dir = PATH(cache_dir)
    stem = PATH(cache_stem)
    suffix = f"-{stem.stem}{stem.suffix or '.pt'}"

    index: dict[str, PATH] = {}
    for path in sorted(cache_dir.glob(f"*{suffix}")):
        split = path.name[: -len(suffix)]
        if not split:
            continue
        for key in blob_keys(split):
            index.setdefault(key, path)
    return index


def read_activation_blob(path, *, mmap: bool = False) -> dict:
    """Load a saved activation blob. ``mmap=True`` reads shapes/scalars only."""
    return torch.load(PATH(path), map_location="cpu", mmap=mmap)


def validate_activation_blob(
    blob: dict, path, *, name: str, model_name: str, layer: int, n_rows: int
) -> None:
    """Raise unless ``blob`` really is this probe's activations for ``n_rows`` inputs.

    Worth being strict: tuberlens' own activation loader drops the model/layer a blob
    was saved with and these caches are keyed by path alone, so a blob fetched from a
    remote store would otherwise be scored against the wrong probe in silence.
    """
    missing = set(ACTIVATION_FIELDS) - set(blob)
    if missing:
        raise ValueError(
            f"{name}: {path} is missing tensor field(s) {sorted(missing)} — "
            "it does not look like a tuberlens activation blob."
        )

    problems = []
    got_model = blob.get("model_name")
    if got_model is not None and got_model != model_name:
        problems.append(f"model_name={got_model!r} (probe expects {model_name!r})")
    got_layer = blob.get("layer")
    if got_layer is not None and int(got_layer) != int(layer):
        problems.append(f"layer={got_layer} (probe expects {layer})")
    rows = int(blob["activations"].shape[0])
    if rows != int(n_rows):
        problems.append(f"{rows} rows (the dataset has {n_rows})")
    if problems:
        raise ValueError(
            f"{name}: activations at {path} do not match this run — "
            + "; ".join(problems)
            + ". Refusing to use them."
        )


def attach_cached_activations(
    datasets: dict,
    cache_dir,
    *,
    model_name: str,
    layer: int,
    cache_stem: str = DEFAULT_CACHE_STEM,
    require_all: bool = True,
    verbose: bool = True,
) -> dict:
    """Attach precomputed activations to each dataset that has a blob in the cache.

    A dataset carrying ``activations`` in ``other_fields`` is passed straight through
    by ``get_performances``, so once every split is attached the extraction model is
    never loaded — the whole point of fetching the blobs.

    Returns a new ``{name: dataset}`` map; datasets with no blob are returned as-is
    (and their activations get computed later) unless ``require_all``.
    """
    cache_dir = PATH(cache_dir)
    if not cache_dir.is_dir():
        raise FileNotFoundError(f"Activation cache directory not found: {cache_dir}")

    index = build_blob_index(cache_dir, cache_stem)

    out, missing = {}, []
    for name, dataset in datasets.items():
        path = index.get(name)
        if path is None:
            missing.append(name)
            out[name] = dataset
            if verbose:
                print(
                    f"[activations] {name}: no cached blob in {cache_dir} "
                    f"(looked for {name} and its cache key)"
                )
            continue

        blob = read_activation_blob(path)
        validate_activation_blob(
            blob,
            path,
            name=name,
            model_name=model_name,
            layer=layer,
            n_rows=len(dataset),
        )
        out[name] = dataset.assign(**{f: blob[f] for f in ACTIVATION_FIELDS})
        if verbose:
            shape = tuple(blob["activations"].shape)
            print(f"[activations] {name}: loaded {shape} from {path.name}")

    if missing and require_all:
        raise FileNotFoundError(
            f"No cached activations for {', '.join(missing)} in {cache_dir}. "
            "Fetch them (fetch_kaggle_eval_activations.py --concept ... --cache-dir "
            f"{cache_dir}), or pass --allow_missing_cached_activations to compute the "
            "gaps with the extraction model."
        )
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate a concept probe against local eval datasets.",
        epilog="Memory pinning: set MAX_MEMORY (e.g. MAX_MEMORY='0=21GiB,cpu=45GiB') "
        "to pin how the extraction model is split across GPU/CPU; unset, accelerate "
        "guesses from free memory and may spill to disk offload. Not needed when "
        "--activations_cache_dir covers every split, since no model is then loaded.",
    )

    parser.add_argument(
        "--probe_path",
        type=str,
        default="probe_llama1b.pkl",
        help="Path to the trained probe (matches train.py --output_probe_path default)",
    )

    parser.add_argument(
        "--results_file_name",
        type=PATH,
        default="_evaluation_results.csv",
        help="File name to save evaluation results",
    )

    parser.add_argument(
        "--samples_per_class",
        type=int,
        default=None,
        help="Number of samples per class for evaluation",
    )
    parser.add_argument(
        "--eval_dataset_save_dir",
        type=PATH,
        default=PATH(__file__).parent / "eval_datasets",
        help="Directory that directly contains the local evaluation datasets "
        "(*.jsonl) for the concept, e.g. eval_datasets/highstakes",
    )
    parser.add_argument(
        "--pos_class_label",
        type=str,
        default="high-stakes",
        help="Positive-class label; must match the 'labels' values in the eval data "
        "and the label the probe was trained with (e.g. 'high-stakes', "
        "'harmful_to_human').",
    )
    parser.add_argument(
        "--neg_class_label",
        type=str,
        default="low-stakes",
        help="Negative-class label; must match the 'labels' values in the eval data "
        "(e.g. 'low-stakes', 'not_harmful_to_human').",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--combine_consecutive_messages",
        action="store_true",
        help="Whether to combine consecutive messages from the same speaker",
    )
    parser.add_argument(
        "--convert_tool_to_assistant",
        action="store_true",
        help="Whether to convert tool messages to assistant messages",
    )

    parser.add_argument(
        "--activations_save_path",
        type=str,
        default=None,
        help="Path to save activations computed during this run (only used for "
        "splits not already covered by --activations_cache_dir)",
    )
    parser.add_argument(
        "--activations_cache_dir",
        type=PATH,
        default=None,
        help="Directory of precomputed activation blobs from "
        "fetch_kaggle_eval_activations.py (its --cache-dir). Blobs are matched to "
        "eval datasets by file stem, validated against the probe, and attached "
        "directly — so the extraction model is never loaded.",
    )
    parser.add_argument(
        "--cache_stem",
        type=str,
        default=DEFAULT_CACHE_STEM,
        help="Blob file name inside --activations_cache_dir; each split is stored as "
        f"'<split>-<stem>' (default: {DEFAULT_CACHE_STEM})",
    )
    parser.add_argument(
        "--allow_missing_cached_activations",
        action="store_true",
        help="With --activations_cache_dir, compute activations for splits that have "
        "no cached blob instead of failing (this loads the extraction model)",
    )
    parser.add_argument(
        "--using_kaggle",
        action="store_true",
        help="Whether the script will upload activations to Kaggle",
    )

    args = parser.parse_args()

    seed_everything(args.seed)

    PROBE_PATH = PATH(args.probe_path)
    probe = pickle.load(open(PROBE_PATH, "rb"))
    assert probe.model_name is not None
    assert probe.layer is not None
    print("Probe initialized:")
    print(probe.description)

    pos_class_label = args.pos_class_label
    neg_class_label = args.neg_class_label

    # Load all evaluation datasets directly from the local directory (no download).
    eval_dir = PATH(args.eval_dataset_save_dir)
    if not eval_dir.is_dir():
        raise FileNotFoundError(f"Eval dataset directory not found: {eval_dir}")

    dataset_files = sorted(eval_dir.glob("*.jsonl"))
    if not dataset_files:
        raise FileNotFoundError(f"No .jsonl eval datasets found in {eval_dir}")

    eval_datasets = {
        path.stem: LabelledDataset.load_from(
            path,
            pos_class_label=pos_class_label,
            neg_class_label=neg_class_label,
            combine_consecutive_messages=args.combine_consecutive_messages,
            convert_tool_to_assistant=args.convert_tool_to_assistant,
        )
        for path in dataset_files
    }

    # Print dataset sizes
    for name, dataset in eval_datasets.items():
        print(f"{name}: {len(dataset)} samples")

    # Reuse precomputed activations where we have them. Datasets that already carry
    # `activations` are handed straight to the probe by get_performances, which only
    # loads the extraction model for the ones that don't.
    if args.activations_cache_dir is not None:
        eval_datasets = attach_cached_activations(
            eval_datasets,
            args.activations_cache_dir,
            model_name=probe.model_name,
            layer=probe.layer,
            cache_stem=args.cache_stem,
            require_all=not args.allow_missing_cached_activations,
        )

    needs_model = [
        name
        for name, dataset in eval_datasets.items()
        if "activations" not in dataset.other_fields
    ]
    # A labels-only split carries no text to run the model over. Computing
    # activations from it would score empty strings and quietly report meaningless
    # metrics, so refuse instead.
    labels_only = [
        name
        for name in needs_model
        if "labels_only" in eval_datasets[name].other_fields
    ]
    if labels_only:
        raise ValueError(
            f"{', '.join(labels_only)}: these splits carry labels only, so their "
            "activations cannot be computed. Point --activations_cache_dir at the "
            "cache holding their blobs (fetch_kaggle_eval_activations.py --concept "
            "<name>_eval --cache-dir ...)."
        )
    if needs_model:
        print(
            f"Will load {probe.model_name} to compute activations for: "
            + ", ".join(needs_model)
        )
    else:
        print("All splits have cached activations — the extraction model stays unloaded.")

    from tuberlens.evaluation import get_performances
    from tuberlens.interfaces.dataset import subsample_balanced_subset

    max_samples = (
        args.samples_per_class  # Downsample for faster evaluation (set to None for full evaluation)
    )
    performances = get_performances(
        probe,
        {
            name: subsample_balanced_subset(dataset, n_per_class=max_samples // 2)
            if max_samples is not None
            else dataset
            for name, dataset in eval_datasets.items()
        },
        activations_save_path=args.activations_save_path,
        using_kaggle=args.using_kaggle,
    )
    if not args.results_file_name.parent.exists():
        args.results_file_name.parent.mkdir(parents=True)

    performances.to_csv(
        args.results_file_name,
        index=False,
    )
