# Basic Configuration
import argparse
import os
import pickle
from pathlib import Path

from dotenv import load_dotenv
from evaluation import seed_everything

from tuberlens.interfaces.dataset import LabelledDataset
from tuberlens.interfaces.probes import ProbeSpec, ProbeType
from tuberlens.training import train_probe
from tuberlens.utils import create_train_test_split

# Load HF_TOKEN (and any other secrets) from the project-root .env.
# override=True so the .env value wins over any stale HF_TOKEN in the shell env.
load_dotenv(override=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train a concept probe (e.g. high-stakes/low-stakes, "
        "harmful/not-harmful) on an LLM's activations."
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
        default="initial_training_set/init_seed_hs_ls_200.jsonl",
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
    train_dataset, validation_dataset = create_train_test_split(
        dataset, split_field=args.split
    )

    print(
        f"Read {len(train_dataset)} samples for training and {len(validation_dataset)} samples for validation."
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
