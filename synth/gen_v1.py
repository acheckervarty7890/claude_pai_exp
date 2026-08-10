#!/usr/bin/env python
"""Render the hand-authored scenario pools into a probe training JSONL.

Output schema matches initial_training_set/init_seed_hs_ls_200.jsonl exactly so the
result can be concatenated with the seed and loaded by the same LabelledDataset call.

Conversations are emitted in the *post-processed* form the evaluation path produces
(no `tool` role, no two consecutive messages from the same speaker), so training-time
and eval-time message shapes line up even though train.py loads without the
combine_consecutive_messages / convert_tool_to_assistant flags.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import pools_v1 as P

POS = "high-stakes"
NEG = "low-stakes"

GENERIC_SYSTEMS = [
    "You are a helpful AI assistant.",
    "You are a helpful, harmless and honest AI assistant.",
    "You are an AI assistant. Answer the user's questions as well as you can.",
    "You are a knowledgeable assistant chatting with a member of the public.",
]

TOOL_SYSTEM = (
    "You are a function-calling AI assistant. You have access to the following tools:\n"
    "{tools}\n"
    "When a tool is needed, respond with the call in the form [tool_name(arg=value)]. "
    "Do not invent parameters that are not in the schema."
)


def rec(messages, label, pair_id, idx, rationale, scale, shape):
    """One JSONL record in the seed's schema."""
    return {
        "inputs": json.dumps(messages),
        "ids": f"syn_{shape}_{'hs' if label == POS else 'ls'}_{idx}",
        "pair_id": pair_id,
        "original_labels": label,
        "scale_label_explanation": rationale,
        "scale_label_confidence": 8,
        "scale_label_score": None,
        "scale_labels": scale,
        "scale_label_model": "synthetic-authored",
        "labels": label,
        "label_explanation": rationale,
    }


HS_WHY = (
    "Synthetic sample authored as the high-stakes member of a matched pair: the situation "
    "carries serious, hard-to-reverse consequences for health, safety, money, liberty or rights."
)
LS_WHY = (
    "Synthetic sample authored as the low-stakes member of a matched pair: same surface domain "
    "and register, but the outcome is routine, reversible and inconsequential."
)


def build(seed: int = 7):
    rng = random.Random(seed)
    out: list[dict] = []
    pid = 10_000

    # --- A. everyday chat: bare user turn, half of them behind a generic system prompt
    for i, (hs, ls) in enumerate(P.EVERYDAY):
        pid += 1
        use_system = i % 2 == 0
        for label, text, why, scale in (
            (POS, hs, HS_WHY, rng.choice([8, 9, 9, 10])),
            (NEG, ls, LS_WHY, rng.choice([1, 2, 2, 3])),
        ):
            msgs = []
            if use_system:
                msgs.append({"role": "system", "content": rng.choice(GENERIC_SYSTEMS)})
            msgs.append({"role": "user", "content": text})
            out.append(rec(msgs, label, pid, i, why, scale, "everyday"))

    # --- B. multi-turn advice: user / assistant / user
    for i, (hs, ls) in enumerate(P.MULTITURN):
        pid += 1
        use_system = i % 3 == 0
        for label, core, why, scale in (
            (POS, hs, HS_WHY, rng.choice([8, 9, 9, 10])),
            (NEG, ls, LS_WHY, rng.choice([1, 2, 2, 3])),
        ):
            u1, a1, u2 = core
            msgs = []
            if use_system:
                msgs.append({"role": "system", "content": rng.choice(GENERIC_SYSTEMS)})
            msgs += [
                {"role": "user", "content": u1},
                {"role": "assistant", "content": a1},
                {"role": "user", "content": u2},
            ]
            out.append(rec(msgs, label, pid, i, why, scale, "multiturn"))

    # --- C. benchmark-style: emitted both as a single first turn and as a two-turn exchange
    for i, (hs, ls) in enumerate(P.BENCHMARK):
        for shape in ("bench1", "bench2"):
            pid += 1
            for label, core, why, scale in (
                (POS, hs, HS_WHY, rng.choice([7, 8, 9])),
                (NEG, ls, LS_WHY, rng.choice([1, 2, 3])),
            ):
                u1, a1, u2 = core
                if shape == "bench1":
                    msgs = [{"role": "user", "content": u1}]
                else:
                    msgs = [
                        {"role": "user", "content": u1},
                        {"role": "assistant", "content": a1},
                        {"role": "user", "content": u2},
                    ]
                out.append(rec(msgs, label, pid, i, why, scale, shape))

    # --- D. agentic tool transcripts, three shapes per core
    #   call      : system(tools) / user / assistant(call)            -- the request + the call
    #   result    : ... / assistant(call + folded tool result + answer)
    #   followup  : ... / user(second request) / assistant(second call)
    for i, (hs, ls) in enumerate(P.TOOLS):
        for shape in ("call", "result", "followup"):
            pid += 1
            for label, core, why, scale in (
                (POS, hs, HS_WHY, rng.choice([8, 9, 9, 10])),
                (NEG, ls, LS_WHY, rng.choice([1, 2, 2])),
            ):
                tools, user, call, result, final = core
                sysmsg = {"role": "system", "content": TOOL_SYSTEM.format(tools=tools)}
                if shape == "call":
                    msgs = [sysmsg, {"role": "user", "content": user}, {"role": "assistant", "content": call}]
                elif shape == "result":
                    # tool role converted to assistant, then merged with its neighbours
                    merged = f"{call}\n\n{result}\n\n{final}"
                    msgs = [sysmsg, {"role": "user", "content": user}, {"role": "assistant", "content": merged}]
                else:
                    msgs = [
                        sysmsg,
                        {"role": "user", "content": user},
                        {"role": "assistant", "content": f"{call}\n\n{result}\n\n{final}"},
                        {"role": "user", "content": "Go ahead and do the same thing again for the other one on the list."},
                        {"role": "assistant", "content": call},
                    ]
                out.append(rec(msgs, label, pid, i, why, scale, f"tool_{shape}"))

    # --- E. professional personas: system + single user turn
    for i, (sysmsg, hs, ls) in enumerate(P.PROFESSIONAL):
        pid += 1
        for label, text, why, scale in (
            (POS, hs, HS_WHY, rng.choice([8, 9, 9, 10])),
            (NEG, ls, LS_WHY, rng.choice([1, 1, 2])),
        ):
            msgs = [
                {"role": "system", "content": sysmsg},
                {"role": "user", "content": text},
            ]
            out.append(rec(msgs, label, pid, i, why, scale, "professional"))

    rng.shuffle(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("synthetic_data/synth_v1.jsonl"))
    ap.add_argument("--seed-file", type=Path, default=Path("initial_training_set/init_seed_hs_ls_200.jsonl"))
    ap.add_argument("--combined", type=Path, default=Path("synthetic_data/train_v1.jsonl"))
    args = ap.parse_args()

    rows = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")

    n_pos = sum(r["labels"] == POS for r in rows)
    by_shape: dict[str, int] = {}
    for r in rows:
        by_shape[r["ids"].split("_")[1]] = by_shape.get(r["ids"].split("_")[1], 0) + 1
    print(f"wrote {len(rows)} synthetic rows ({n_pos} {POS} / {len(rows) - n_pos} {NEG}) -> {args.out}")
    print("  by shape:", dict(sorted(by_shape.items())))

    with args.combined.open("w") as fh:
        for line in args.seed_file.read_text().splitlines():
            if line.strip():
                fh.write(line + "\n")
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(f"wrote combined seed+synthetic -> {args.combined}")
