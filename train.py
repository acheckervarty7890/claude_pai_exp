"""Train a concept probe on an LLM's activations.

Validation set: by default the training seed is split (``create_train_test_split``)
into train/validation. Pass ``--validation_data`` to instead train on the *whole*
seed and validate on the concept's held-out dev samples. Those ship as labels only,
so pair them with ``--validation_activations_dir``, which points at the precomputed
dev activations fetched by ``fetch_kaggle_eval_activations.py``.

MEMORY PINNING
--------------
Training always loads the extraction model (the training seed is raw text), and how
it is split across GPU/CPU is pinned by the ``MAX_MEMORY`` environment variable —
accelerate's per-device budget, compact form ``MAX_MEMORY="0=21GiB,cpu=45GiB"``.
Left unset, accelerate infers the budget from whatever is free at load time and can
silently spill layers to disk offload, which is orders of magnitude slower than CPU
offload. ``MODEL_MAX_MEMORY`` overrides it per model name (JSON object), and
``OFFLOAD_BUFFERS`` (default true) keeps buffers with the weights they belong to.

tuberlens reads these at *import* time, so ``load_dotenv()`` runs before the
tuberlens imports below. Setting them in the shell works either way.
"""

# Basic Configuration
import argparse
import os
import pickle
from pathlib import Path

import torch
from dotenv import load_dotenv

# Load HF_TOKEN, MAX_MEMORY and any other secrets/settings from the project-root .env.
# override=True so the .env value wins over any stale value in the shell env.
# This MUST run before the tuberlens imports: tuberlens.config builds its
# `global_settings` (MAX_MEMORY, MODEL_MAX_MEMORY, OFFLOAD_BUFFERS, DTYPE, ...) from
# os.environ at import time, so a .env loaded afterwards would arrive too late.
load_dotenv(override=True)

from evaluation import (  # noqa: E402
    ACTIVATION_FIELDS,
    DEFAULT_CACHE_STEM,
    build_blob_index,
    read_activation_blob,
    seed_everything,
    validate_activation_blob,
)
from tuberlens.interfaces.dataset import LabelledDataset  # noqa: E402
from tuberlens.interfaces.probes import ProbeSpec, ProbeType  # noqa: E402
from tuberlens.training import train_probe  # noqa: E402
from tuberlens.utils import create_train_test_split  # noqa: E402


def validation_activations_path(activations_save_path: str) -> Path:
    """Where train_probe looks for the validation set's activations.

    It derives the path as ``with_stem(f"val-{stem}")`` of ``activations_save_path``
    and, finding a file there, loads it instead of running the model. Staging the dev
    blob at exactly that path is what lets precomputed dev activations be reused.
    """
    p = Path(activations_save_path)
    return p.with_stem(f"val-{p.stem}")


def stage_validation_activations(
    dataset_names: list[str],
    validation_dataset: LabelledDataset,
    cache_dir,
    target: Path,
    *,
    model_name: str,
    layer: int,
    cache_stem: str = DEFAULT_CACHE_STEM,
) -> None:
    """Write the dev splits' cached activations to the path train_probe will read.

    A single split is symlinked (these blobs run to gigabytes, so no second copy);
    several are concatenated into a new blob, which requires a common sequence length
    — blobs are padded per-split, so mismatched splits cannot be stacked and are
    rejected rather than silently truncated.
    """
    if target.exists():
        print(f"[activations] validation blob already staged at {target}; reusing it")
        return

    index = build_blob_index(cache_dir, cache_stem)

    blobs = []
    for name in dataset_names:
        path = index.get(name)
        if path is None:
            raise FileNotFoundError(
                f"{name}: no cached activations in {cache_dir} (looked for {name} and "
                "its cache key). Fetch the concept's dev splits "
                "(fetch_kaggle_eval_activations.py --concept <name>_dev --cache-dir "
                f"{cache_dir}), or drop --validation_activations_dir to compute them "
                "with the extraction model."
            )
        blobs.append((name, path, read_activation_blob(path)))

    # Validate each blob against the run before anything is stacked or written.
    rows_per_split = []
    for name, path, blob in blobs:
        rows = int(blob["activations"].shape[0])
        rows_per_split.append(rows)
        validate_activation_blob(
            blob, path, name=name, model_name=model_name, layer=layer, n_rows=rows
        )
    if sum(rows_per_split) != len(validation_dataset):
        raise ValueError(
            f"Validation activations cover {sum(rows_per_split)} rows but the "
            f"validation dataset has {len(validation_dataset)}. The blobs and the "
            "--validation_data files are not the same splits."
        )

    target.parent.mkdir(parents=True, exist_ok=True)

    if len(blobs) == 1:
        # Symlink rather than copy: one of these blobs can be tens of GB.
        target.symlink_to(blobs[0][1].resolve())
        print(
            f"[activations] staged {len(validation_dataset)} validation rows "
            f"({dataset_names[0]}) at {target} -> {blobs[0][1]}"
        )
        return

    seq_lens = {int(b["activations"].shape[1]) for _, _, b in blobs}
    if len(seq_lens) > 1:
        raise ValueError(
            f"Cannot concatenate dev splits with different sequence lengths "
            f"{sorted(seq_lens)}. Pass a single --validation_data split, or ones "
            "whose blobs share a sequence length."
        )
    merged = {
        field: torch.cat([b[field] for _, _, b in blobs], dim=0)
        for field in ACTIVATION_FIELDS
    }
    for key in ("model_name", "layer"):
        value = blobs[0][2].get(key)
        if value is not None:
            merged[key] = value

    torch.save(merged, target)
    print(
        f"[activations] staged {len(validation_dataset)} validation rows "
        f"({', '.join(dataset_names)}) at {target}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train a concept probe (e.g. high-stakes/low-stakes, "
        "harmful/not-harmful) on an LLM's activations.",
        epilog="Memory pinning: set MAX_MEMORY (e.g. MAX_MEMORY='0=21GiB,cpu=45GiB') "
        "to pin how the extraction model is split across GPU/CPU; unset, accelerate "
        "guesses from free memory and may silently fall back to disk offload.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="meta-llama/Llama-3.2-1B-Instruct",
        help="Model name to use",
    )
    parser.add_argument("--layer", type=int, default=8, help="Layer number to probe")

    parser.add_argument(
        "--output_probe_path",
        type=str,
        default="probe_llama1b.pkl",
        help="Output path for the trained probe",
    )

    parser.add_argument(
        "--probe_training_data",
        type=str,
        default="initial_training_set/init_seed_hs_ls_50.jsonl",
        help="Path to the probe training data file for the concept being trained",
    )
    parser.add_argument(
        "--pos_class_label",
        type=str,
        default="high-stakes",
        help="Positive-class label; must match the 'labels' values in the training "
        "data (e.g. 'high-stakes', 'harmful_to_human').",
    )
    parser.add_argument(
        "--neg_class_label",
        type=str,
        default="low-stakes",
        help="Negative-class label; must match the 'labels' values in the training "
        "data (e.g. 'low-stakes', 'not_harmful_to_human').",
    )
    parser.add_argument(
        "--concept_description",
        type=str,
        default="the conversation is high-stakes",
        help="Short phrase describing the positive concept, used to build the probe "
        'description stored in the pickle (e.g. "the conversation is harmful to human").',
    )
    parser.add_argument(
        "--validation_data",
        type=Path,
        nargs="+",
        default=None,
        help="Dev sample file(s) (*.jsonl) to use as the validation set, or a "
        "directory of them. Given these, the whole training seed is used for "
        "training instead of being split. Labels must use the same class labels.",
    )
    parser.add_argument(
        "--validation_activations_dir",
        type=Path,
        default=None,
        help="Directory of precomputed dev activations from "
        "fetch_kaggle_eval_activations.py (its --cache-dir). Blobs are matched to "
        "--validation_data by file stem and staged where train_probe reads them, so "
        "the model is not run over the dev inputs. Needs --activations_save_path.",
    )
    parser.add_argument(
        "--cache_stem",
        type=str,
        default=DEFAULT_CACHE_STEM,
        help="Blob file name inside --validation_activations_dir; each split is "
        f"stored as '<split>-<stem>' (default: {DEFAULT_CACHE_STEM})",
    )
    parser.add_argument(
        "--split", type=str, default=None, help="Field to use for train-test split"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--activations_save_path",
        type=str,
        default=None,
        help="Path to save activations",
    )
    parser.add_argument(
        "--using_kaggle",
        action="store_true",
        help="Whether the script will upload activations to Kaggle",
    )

    args = parser.parse_args()

    seed_everything(args.seed)

    layer = args.layer

    pos_class_label = args.pos_class_label
    neg_class_label = args.neg_class_label
    probe_description = (
        f"A linear probe on {args.model} detecting whether {args.concept_description}."
    )

    training_data_path = Path(args.probe_training_data)

    dataset = LabelledDataset.load_from(
        training_data_path,
        pos_class_label=pos_class_label,
        neg_class_label=neg_class_label,
    )

    validation_names: list[str] = []
    if args.validation_data:
        # Dev samples as validation: keep the whole seed for training.
        validation_files = []
        for entry in args.validation_data:
            if entry.is_dir():
                validation_files.extend(sorted(entry.glob("*.jsonl")))
            else:
                validation_files.append(entry)
        if not validation_files:
            raise FileNotFoundError(
                f"No .jsonl dev samples found in {args.validation_data}"
            )

        validation_parts = [
            LabelledDataset.load_from(
                path,
                pos_class_label=pos_class_label,
                neg_class_label=neg_class_label,
            )
            for path in validation_files
        ]
        validation_names = [path.stem for path in validation_files]
        train_dataset = dataset
        validation_dataset = (
            validation_parts[0]
            if len(validation_parts) == 1
            else LabelledDataset.concatenate(validation_parts)
        )
        print(
            "Using dev samples as validation: "
            + ", ".join(f"{n} ({len(d)})" for n, d in zip(validation_names, validation_parts))
        )
    else:
        train_dataset, validation_dataset = create_train_test_split(
            dataset, split_field=args.split
        )

    print(
        f"Read {len(train_dataset)} samples for training and {len(validation_dataset)} samples for validation."
    )

    if (
        args.validation_activations_dir is None
        and "labels_only" in validation_dataset.other_fields
    ):
        raise ValueError(
            "The dev samples carry labels only, so their activations cannot be "
            "computed. Pass --validation_activations_dir (and "
            "--activations_save_path) to validate against the precomputed dev blobs."
        )

    if args.validation_activations_dir is not None:
        if not validation_names:
            raise ValueError(
                "--validation_activations_dir only applies to --validation_data; "
                "without it the validation set is a random slice of the seed and has "
                "no precomputed activations."
            )
        if args.activations_save_path is None:
            raise ValueError(
                "--validation_activations_dir needs --activations_save_path: the "
                "staged validation blob is named after it."
            )
        stage_validation_activations(
            validation_names,
            validation_dataset,
            args.validation_activations_dir,
            validation_activations_path(args.activations_save_path),
            model_name=args.model,
            layer=layer,
            cache_stem=args.cache_stem,
        )

    probe = train_probe(
        train_dataset,
        validation_dataset,
        args.model,
        layer,
        pos_class_label=pos_class_label,
        neg_class_label=neg_class_label,
        probe_description=probe_description,
        probe_spec=ProbeSpec(
            name=ProbeType.linear_then_softmax,
            hyperparams={},
        ),
        activations_save_path=args.activations_save_path,
        using_kaggle=args.using_kaggle,
    )

    os.makedirs(Path(args.output_probe_path).parent, exist_ok=True)
    with open(Path(args.output_probe_path), "wb") as f:
        pickle.dump(probe, f)
