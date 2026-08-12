# Shared environment for training/evaluating the gemma-3-27b probe.
# Source this before calling train.py / evaluation.py.
#
# MODEL_MAX_MEMORY pins the model across the 24GB GPU and system RAM, as
# accelerate's `max_memory` spec. tuberlens' GlobalSettings is a pydantic
# BaseSettings, so this env var is parsed as JSON straight into config.
export MODEL_MAX_MEMORY='{"google/gemma-3-27b-it": {"cuda:0": "22GiB", "cpu": "45GiB"}}'

# BATCH_SIZE stays 1: activation extraction then never pads, so a sample's
# activations are identical regardless of what it is batched with. Keeping
# train and eval activations on the same footing matters more here than speed.
export BATCH_SIZE=1

export MODEL="google/gemma-3-27b-it"
export LAYER=32

export POS_LABEL="assistant_follows_the_instruction"
export NEG_LABEL="assistant_does_not_follow_the_instruction"
export CONCEPT_DESC="the assistant follows the instruction"
export EVAL_DIR="eval_datasets/follows_instructions"

# Cache dir for eval activations: the model and layer are fixed across
# iterations, so these are computed once and reused by every later eval.
export ACT_DIR="activations_cache"
