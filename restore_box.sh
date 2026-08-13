#!/usr/bin/env bash
# Re-apply the out-of-tree state that a box reset wipes.
#
# The tuberlens checkout lives in .venv/src/tuberlens, which is gitignored, so
# the max_memory patch it carries does not survive a lost box. This restores it
# from tuberlens_max_memory.patch and sanity-checks the pieces the runs need.
#
#   bash restore_box.sh
#
# Not restored here (they only cost time, not information): the HuggingFace
# model cache and activations_cache/ — both refill on the next run.
set -euo pipefail

cd "$(dirname "$0")"

TUBERLENS=".venv/src/tuberlens"

if git -C "$TUBERLENS" diff --quiet; then
  echo "applying tuberlens_max_memory.patch"
  git -C "$TUBERLENS" apply "$(pwd)/tuberlens_max_memory.patch"
else
  echo "tuberlens already patched (working tree dirty) — leaving it alone"
fi

source run_env.sh
.venv/bin/python - <<'PY'
import os

from tuberlens.config import global_settings
from tuberlens.model import _normalize_max_memory

spec = global_settings.MODEL_MAX_MEMORY.get(os.environ["MODEL"])
assert spec, "MODEL_MAX_MEMORY has no entry for $MODEL — is run_env.sh sourced?"
print("max_memory:", _normalize_max_memory(spec))
print("HF_TOKEN set:", bool(os.getenv("HF_TOKEN")))
PY
