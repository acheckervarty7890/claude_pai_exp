"""Build a synthetic training JSONL for the high-stakes / low-stakes probe.

Rows match the seed's schema exactly: {"inputs": <json string of a message list>,
"labels": "high-stakes" | "low-stakes"}. Pools are authored by hand in pools*.py;
this script only formats them, balances the classes and (optionally) concatenates
the original seed.
"""
import argparse
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import pools, pools_clinical, pools_clinical2, pools_clinical3  # noqa: E402
import pools_mt, pools_mt2, pools_mt3, pools_mt4  # noqa: E402
import pools_hh, pools_hh2, pools_hh3  # noqa: E402
import pools_prof, pools_prof2  # noqa: E402
import pools_tool, pools_tool2, pools_tool3, pools_tool4  # noqa: E402
from func_bank import BANK  # noqa: E402

POS, NEG = "high-stakes", "low-stakes"


def plain(turns):
    return [{"role": r, "content": c} for r, c in turns]


def catalogue(primary_json, i, n_distractors=4):
    """Advertise the tool that gets called alongside a few unrelated ones.

    Real function-calling prompts list several tools, which is most of why those
    conversations are long. Distractors come from one shared bank for both classes
    and are picked by a per-entry rotation, so catalogue size and content never
    correlate with the label.
    """
    primary = json.loads(primary_json)
    picks = [BANK[(i * 7 + k * 3) % len(BANK)] for k in range(n_distractors)]
    tools = primary + picks
    rng = random.Random(1000 + i)
    rng.shuffle(tools)
    return json.dumps(tools, indent=2)


def tool_rows(entries):
    """ToolACE-shaped, flattened to strict user/assistant alternation.

    Gemma's chat template rejects `system` and `tool` roles, so the function
    catalogue is folded into the opening user turn and each tool result is merged
    into the assistant turn that issued the call - the same shape
    `--convert_tool_to_assistant --combine_consecutive_messages` produces.
    """
    out = []
    for i, (funcs, turns) in enumerate(entries):
        msgs = []
        header = pools_tool.TOOL_SYS.format(funcs=catalogue(funcs, i))
        for role, content in turns:
            if role == "tool":
                assert msgs and msgs[-1]["role"] == "assistant"
                msgs[-1]["content"] += "\n\n<tool_response>\n" + content + "\n</tool_response>"
                continue
            if role == "user" and not msgs:
                content = header + "\n" + content
            if msgs and msgs[-1]["role"] == role:
                msgs[-1]["content"] += "\n\n" + content
                continue
            msgs.append({"role": role, "content": content})
        out.append(msgs)
    return out


def check_alternating(rows):
    """Every conversation must start with `user` and strictly alternate."""
    for i, msgs in enumerate(rows):
        roles = [m["role"] for m in msgs]
        assert roles[0] == "user", (i, roles)
        assert all(a != b for a, b in zip(roles, roles[1:])), (i, roles)
        assert set(roles) <= {"user", "assistant"}, (i, roles)


def collect(extra_modules=()):
    high, low = [], []
    plain_mods = (pools, pools_clinical, pools_clinical2, pools_clinical3,
                  pools_mt, pools_mt2, pools_mt3, pools_mt4,
                  pools_hh, pools_hh2, pools_hh3,
                  pools_prof, pools_prof2)
    tool_mods = (pools_tool, pools_tool2, pools_tool3, pools_tool4)
    for mod in plain_mods + tuple(extra_modules):
        high += [plain(t) for t in mod.HIGH]
        low += [plain(t) for t in mod.LOW]
    for mod in tool_mods:
        high += tool_rows(mod.HIGH)
        low += tool_rows(mod.LOW)
    check_alternating(high)
    check_alternating(low)
    return high, low


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--include-seed", default="initial_training_set/init_seed_hs_ls_50.jsonl")
    ap.add_argument("--no-seed", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--extra", nargs="*", default=[],
                    help="extra pool modules (importable from synth/) to fold in")
    args = ap.parse_args()

    extra = []
    for name in args.extra:
        extra.append(__import__(name))

    high, low = collect(extra)

    rows = []
    if not args.no_seed:
        seed_path = Path(args.include_seed)
        rows += [json.loads(l) for l in seed_path.read_text().splitlines() if l.strip()]

    for msgs in high:
        rows.append({"inputs": json.dumps(msgs, ensure_ascii=False), "labels": POS})
    for msgs in low:
        rows.append({"inputs": json.dumps(msgs, ensure_ascii=False), "labels": NEG})

    rng = random.Random(args.seed)
    rng.shuffle(rows)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    npos = sum(r["labels"] == POS for r in rows)
    print(f"wrote {len(rows)} rows to {out}  ({npos} {POS} / {len(rows)-npos} {NEG})")


if __name__ == "__main__":
    main()
