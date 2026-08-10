import argparse
import pickle
import random
from pathlib import Path as PATH

import numpy as np
import torch
from dotenv import load_dotenv

from tuberlens.interfaces.dataset import LabelledDataset
from tuberlens.model import LLMModel

# Load HF_TOKEN (and any other secrets) from the project-root .env.
# override=True so the .env value wins over any stale HF_TOKEN in the shell env.
load_dotenv(override=True)


def seed_everything(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True  # type: ignore
    torch.backends.cudnn.benchmark = False  # type: ignore


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate a concept probe against local eval datasets."
    )

    parser.add_argument(
        "--probe_path",
        type=str,
        default="rand.pkl",
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
        "(*.jsonl) for the concept, e.g. eval_datasets/hs_ls",
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
        help="Path to save activations",
    )
    parser.add_argument(
        "--using_kaggle",
        action="store_true",
        help="",
    )

    args = parser.parse_args()

    seed_everything(args.seed)

    PROBE_PATH = PATH(args.probe_path)
    probe = pickle.load(open(PROBE_PATH, "rb"))
    assert probe.model_name is not None
    assert probe.layer is not None
    print("Probe initialized:")
    print(probe.description)

    # Initialize the model so we can compute activations
    model = LLMModel.load(probe.model_name)

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
