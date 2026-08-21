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

import pools, pools2  # noqa: E402
import pools_clinical, pools_clinical2, pools_clinical3  # noqa: E402
import pools_clinical4, pools_clinical5  # noqa: E402
import pools_mt, pools_mt2, pools_mt3, pools_mt4, pools_mt5, pools_mt6, pools_mt6  # noqa: E402
import pools_hh, pools_hh2, pools_hh3, pools_hh4, pools_hh5  # noqa: E402
import pools_prof, pools_prof2, pools_prof3, pools_prof4  # noqa: E402
import pools_tool, pools_tool2, pools_tool3, pools_tool4  # noqa: E402
import pools_tool5, pools_tool6, pools_tool7, pools_tool8  # noqa: E402
import pools_tool9, pools_tool10, pools_tool11  # noqa: E402
from func_bank import BANK  # noqa: E402

# The activation blobs are 1024 tokens wide, so anything longer is truncated and
# the tail of the conversation - the part carrying the outcome - is what gets lost.
# Tool prompts are the only rows long enough to hit this, and their catalogue is the
# part that can give way, so distractors are dropped until the row fits.
TOKEN_BUDGET = 1000
_TOKENIZER = None


def tokenizer():
    global _TOKENIZER
    if _TOKENIZER is None:
        from transformers import AutoTokenizer

        _TOKENIZER = AutoTokenizer.from_pretrained(MODEL)
    return _TOKENIZER


def n_tokens(msgs):
    tk = tokenizer()
    return len(tk(tk.apply_chat_template(msgs, tokenize=False))["input_ids"])

POS, NEG = "high-stakes", "low-stakes"
MODEL = "google/gemma-3-27b-it"


def plain(turns):
    return [{"role": r, "content": c} for r, c in turns]


def catalogue(primary_json, i, n_distractors=None, variant=0):
    """Advertise the tool that gets called alongside a few unrelated ones.

    Real function-calling prompts list several tools, which is most of why those
    conversations are long. Distractors come from one shared bank for both classes
    and are picked by a per-entry rotation, so catalogue size and content never
    correlate with the label.
    """
    primary = json.loads(primary_json)
    i = i * 13 + variant * 5
    if n_distractors is None:
        # Vary the catalogue size so prompt length spreads the way real ones do.
        # Driven by the entry's index, which runs independently over each class,
        # so the two classes see the same distribution of sizes.
        n_distractors = 2 + (i % 6)
    picks = [BANK[(i * 7 + k * 3) % len(BANK)] for k in range(n_distractors)]
    tools = primary + picks
    rng = random.Random(1000 + i)
    rng.shuffle(tools)
    return json.dumps(tools, indent=2)


def tool_rows(entries, variants=1):
    """ToolACE-shaped, flattened to strict user/assistant alternation.

    Gemma's chat template rejects `system` and `tool` roles, so the function
    catalogue is folded into the opening user turn and each tool result is merged
    into the assistant turn that issued the call - the same shape
    `--convert_tool_to_assistant --combine_consecutive_messages` produces.
    """
    out = []
    for i, (funcs, turns) in enumerate(entries):
        for variant in range(variants):
            msgs = build_tool_row(funcs, turns, i, variant)
            out.append(msgs)
    return out


def build_tool_row(funcs, turns, i, variant, n_distractors=None):
    """Render one tool conversation, shrinking the catalogue until it fits."""
    while True:
        msgs = []
        preambles = pools_tool.TOOL_SYS_VARIANTS
        header = preambles[(i * 7 + variant * 3) % len(preambles)].format(
            funcs=catalogue(funcs, i, n_distractors=n_distractors, variant=variant)
        )
        for role, content in turns:
            if role == "tool":
                assert msgs and msgs[-1]["role"] == "assistant"
                msgs[-1]["content"] += (
                    "\n\n<tool_response>\n" + content + "\n</tool_response>"
                )
                continue
            if role == "user" and not msgs:
                content = header + "\n" + content
            if msgs and msgs[-1]["role"] == role:
                msgs[-1]["content"] += "\n\n" + content
                continue
            msgs.append({"role": role, "content": content})
        if n_tokens(msgs) <= TOKEN_BUDGET:
            return msgs
        if n_distractors is None:
            n_distractors = 2 + (i * 13 + variant * 5) % 6
        if n_distractors == 0:
            return msgs
        n_distractors -= 1


def check_alternating(rows):
    """Every conversation must start with `user` and strictly alternate."""
    for i, msgs in enumerate(rows):
        roles = [m["role"] for m in msgs]
        assert roles[0] == "user", (i, roles)
        assert all(a != b for a, b in zip(roles, roles[1:])), (i, roles)
        assert set(roles) <= {"user", "assistant"}, (i, roles)


def collect(extra_modules=(), tool_variants=1):
    high, low = [], []
    plain_mods = (pools, pools2,
                  pools_clinical, pools_clinical2, pools_clinical3,
                  pools_clinical4, pools_clinical5,
                  pools_mt, pools_mt2, pools_mt3, pools_mt4, pools_mt5, pools_mt6,
                  pools_hh, pools_hh2, pools_hh3, pools_hh4, pools_hh5,
                  pools_prof, pools_prof2, pools_prof3, pools_prof4)
    tool_mods = (pools_tool, pools_tool2, pools_tool3, pools_tool4,
                 pools_tool5, pools_tool6, pools_tool7, pools_tool8,
                 pools_tool9, pools_tool10, pools_tool11)
    for mod in plain_mods + tuple(extra_modules):
        high += [plain(t) for t in mod.HIGH]
        low += [plain(t) for t in mod.LOW]
    for mod in tool_mods:
        high += tool_rows(mod.HIGH, tool_variants)
        low += tool_rows(mod.LOW, tool_variants)
    check_alternating(high)
    check_alternating(low)
    return high, low


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--include-seed", default="initial_training_set/init_seed_hs_ls_50.jsonl")
    ap.add_argument("--no-seed", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tool-variants", type=int, default=1,
                    help="emit each tool scenario this many times with a different "
                         "distractor catalogue; the tool-calling eval family is a "
                         "quarter of the mean but only a tenth of the rows, and the "
                         "catalogue is the part of those prompts that genuinely varies "
                         "between real examples")
    ap.add_argument("--extra", nargs="*", default=[],
                    help="extra pool modules (importable from synth/) to fold in")
    args = ap.parse_args()

    extra = []
    for name in args.extra:
        extra.append(__import__(name))

    high, low = collect(extra, tool_variants=args.tool_variants)

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
