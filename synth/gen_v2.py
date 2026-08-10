#!/usr/bin/env python
"""Build the v2 training JSONL: all v1 pools plus the tool-focused v2 pools.

Two changes from gen_v1 beyond the extra data:

* the function-calling system prompt is drawn from several realistic wrapper styles
  instead of one fixed template, so the probe can't key on a single boilerplate;
* the v2 tool pools break the "write call => high stakes" correlation, with read-only
  high-stakes cores (TOOLS_DOMAIN) and trivial write cores (TOOLS_ACTION).
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import pools_v1 as P1
import pools_v2 as P2
from gen_v1 import GENERIC_SYSTEMS, HS_WHY, LS_WHY, NEG, POS, rec

TOOL_SYSTEM_STYLES = [
    (
        "You are a function-calling AI assistant. You have access to the following tools:\n"
        "{tools}\n"
        "When a tool is needed, respond with the call in the form [tool_name(arg=value)]. "
        "Do not invent parameters that are not in the schema."
    ),
    (
        "You are an expert in composing functions. You are given a question and a set of possible "
        "functions. Based on the question, you will need to make one or more function calls to "
        "achieve the purpose. If none of the functions can be used, point it out and refuse to "
        "answer. If the given question lacks the parameters required by the function, also point "
        "it out.\n\nHere is a list of functions in JSON format that you can invoke:\n{tools}\n\n"
        "The output MUST strictly adhere to the following format, and NO other text may be "
        "included:\n[func_name1(params_name1=params_value1, ...), func_name2(...)]"
    ),
    (
        "You are a helpful assistant with tool access. Tools available to you:\n"
        "<tools>\n{tools}\n</tools>\n"
        "Call a tool by emitting the call inline. Only use the tools listed above."
    ),
    (
        "# Assistant\n\nYou operate on behalf of the user and may call the tools below to act in "
        "external systems.\n\n## Tools\n{tools}\n\n## Rules\n- Prefer a tool call over guessing.\n"
        "- Ask for any parameter you do not have.\n- Report what the tool returned."
    ),
]

FOLLOWUP_PROMPTS = [
    "Go ahead and do the same thing again for the other one on the list.",
    "Thanks. Now do the same for the second item.",
    "Right. Run that once more for the other record.",
]


def tool_records(pool, kind, shapes, rng, out, pid_start, hs_scale, ls_scale):
    """Render a (tools, user, call, result, final) pool into message lists."""
    pid = pid_start
    for i, (hs, ls) in enumerate(pool):
        for shape in shapes:
            pid += 1
            style = TOOL_SYSTEM_STYLES[(i + len(shape)) % len(TOOL_SYSTEM_STYLES)]
            for label, core, why, scale in (
                (POS, hs, HS_WHY, rng.choice(hs_scale)),
                (NEG, ls, LS_WHY, rng.choice(ls_scale)),
            ):
                tools, user, call, result, final = core
                sysmsg = {"role": "system", "content": style.format(tools=tools)}
                if shape == "call":
                    msgs = [sysmsg, {"role": "user", "content": user},
                            {"role": "assistant", "content": call}]
                elif shape == "result":
                    msgs = [sysmsg, {"role": "user", "content": user},
                            {"role": "assistant", "content": f"{call}\n\n{result}\n\n{final}"}]
                else:
                    msgs = [
                        sysmsg,
                        {"role": "user", "content": user},
                        {"role": "assistant", "content": f"{call}\n\n{result}\n\n{final}"},
                        {"role": "user", "content": rng.choice(FOLLOWUP_PROMPTS)},
                        {"role": "assistant", "content": call},
                    ]
                out.append(rec(msgs, label, pid, i, why, scale, f"{kind}_{shape}"))
    return pid


def build(seed: int = 11):
    rng = random.Random(seed)
    out: list[dict] = []
    pid = 20_000

    # --- v1 non-tool pools, unchanged in shape ---------------------------------
    for i, (hs, ls) in enumerate(P1.EVERYDAY):
        pid += 1
        use_system = i % 2 == 0
        for label, text, why, scale in (
            (POS, hs, HS_WHY, rng.choice([8, 9, 9, 10])),
            (NEG, ls, LS_WHY, rng.choice([1, 2, 2, 3])),
        ):
            msgs = ([{"role": "system", "content": rng.choice(GENERIC_SYSTEMS)}] if use_system else [])
            msgs = msgs + [{"role": "user", "content": text}]
            out.append(rec(msgs, label, pid, i, why, scale, "everyday"))

    for i, (hs, ls) in enumerate(P1.MULTITURN):
        pid += 1
        use_system = i % 3 == 0
        for label, core, why, scale in (
            (POS, hs, HS_WHY, rng.choice([8, 9, 9, 10])),
            (NEG, ls, LS_WHY, rng.choice([1, 2, 2, 3])),
        ):
            u1, a1, u2 = core
            msgs = ([{"role": "system", "content": rng.choice(GENERIC_SYSTEMS)}] if use_system else [])
            msgs = msgs + [
                {"role": "user", "content": u1},
                {"role": "assistant", "content": a1},
                {"role": "user", "content": u2},
            ]
            out.append(rec(msgs, label, pid, i, why, scale, "multiturn"))

    for i, (hs, ls) in enumerate(P1.BENCHMARK):
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

    for i, (sysmsg, hs, ls) in enumerate(P1.PROFESSIONAL):
        pid += 1
        for label, text, why, scale in (
            (POS, hs, HS_WHY, rng.choice([8, 9, 9, 10])),
            (NEG, ls, LS_WHY, rng.choice([1, 1, 2])),
        ):
            msgs = [{"role": "system", "content": sysmsg}, {"role": "user", "content": text}]
            out.append(rec(msgs, label, pid, i, why, scale, "professional"))

    # --- tool pools ------------------------------------------------------------
    pid = tool_records(P1.TOOLS, "tool", ("call", "result", "followup"), rng, out, pid,
                       [8, 9, 9, 10], [1, 2, 2])
    pid = tool_records(P2.TOOLS_DOMAIN, "tooldom", ("call", "result"), rng, out, pid,
                       [8, 9, 9, 10], [1, 2, 2])
    pid = tool_records(P2.TOOLS_ACTION, "toolact", ("call", "result"), rng, out, pid,
                       [8, 9, 9, 10], [1, 2, 2])

    # multi-call / refusal turns: (tools, user, whole_assistant_turn)
    for i, (hs, ls) in enumerate(P2.TOOLS_MULTI):
        pid += 1
        style = TOOL_SYSTEM_STYLES[i % len(TOOL_SYSTEM_STYLES)]
        for label, core, why, scale in (
            (POS, hs, HS_WHY, rng.choice([8, 9, 9, 10])),
            (NEG, ls, LS_WHY, rng.choice([1, 2, 2])),
        ):
            tools, user, reply = core
            msgs = [
                {"role": "system", "content": style.format(tools=tools)},
                {"role": "user", "content": user},
                {"role": "assistant", "content": reply},
            ]
            out.append(rec(msgs, label, pid, i, why, scale, "toolmulti"))

    rng.shuffle(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("../synthetic_data/synth_v2.jsonl"))
    ap.add_argument("--seed-file", type=Path, default=Path("../initial_training_set/init_seed_hs_ls_200.jsonl"))
    ap.add_argument("--combined", type=Path, default=Path("../synthetic_data/train_v2.jsonl"))
    args = ap.parse_args()

    rows = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")

    n_pos = sum(r["labels"] == POS for r in rows)
    by_shape: dict[str, int] = {}
    for r in rows:
        key = r["ids"].rsplit("_", 2)[0][4:]
        by_shape[key] = by_shape.get(key, 0) + 1
    print(f"wrote {len(rows)} synthetic rows ({n_pos} {POS} / {len(rows) - n_pos} {NEG}) -> {args.out}")
    print("  by shape:", dict(sorted(by_shape.items())))

    with args.combined.open("w") as fh:
        for line in args.seed_file.read_text().splitlines():
            if line.strip():
                fh.write(line + "\n")
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(f"wrote combined seed+synthetic -> {args.combined}")
