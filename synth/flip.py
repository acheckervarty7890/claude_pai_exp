"""Context-flipped pairs: the same response, opposite labels.

Every other family varies the response and holds the prompt fixed. That leaves a
loophole — a probe can score well by reading properties of the *response alone*
("is a bulleted list", "is very short", "is a refusal"), which are only correlated
with compliance inside the generated distribution and need not survive transfer to
real conversations.

These families close it from the other side. One assistant turn is paired with two
different instructions: one it satisfies and one it violates. The response text is
byte-identical across the pair, so response-only features carry *zero* information
and the only way to separate the classes is to represent the instruction and the
response together.

The refusal flip is the sharpest case: an identical polite decline is compliant when
a decline was asked for and non-compliant when help was asked for.
"""

from __future__ import annotations

import json
import random

from banks import DECLINE_REQUESTS, NEG_LABEL as NEG, POS_LABEL as POS, Row, TOPICS


def _numbered(xs):
    return "\n".join(f"{i}. {x}" for i, x in enumerate(xs, 1))


def _bulleted(xs):
    return "\n".join(f"- {x}" for x in xs)


def _pair(instr_ok, instr_bad, response, family, mode):
    """One response, two instructions, opposite labels."""
    return [
        Row([{"role": "user", "content": instr_ok},
             {"role": "assistant", "content": response}], POS, family, "compliant"),
        Row([{"role": "user", "content": instr_bad},
             {"role": "assistant", "content": response}], NEG, family, mode),
    ]


def flip_one_word(t, rng):
    q, a = rng.choice(t["facts"])
    ctx = f"{q}?\n\nPassage: {t['passage']}"
    ok = rng.choice([
        f"Answer in a single word, using only the passage.\n\n{ctx}",
        f"One word only — no sentence, no explanation.\n\n{ctx}",
    ])
    bad = rng.choice([
        f"Answer in exactly two full sentences, explaining your reasoning.\n\n{ctx}",
        f"Give three bullet points covering the answer and its context.\n\n{ctx}",
        f"Answer in a complete sentence of at least fifteen words.\n\n{ctx}",
    ])
    return _pair(ok, bad, a, "flip_terse", "omission")


def flip_bullets(t, rng):
    n = rng.choice([3, 4])
    items = rng.sample(t["items"], n)
    body = _bulleted(items)
    ok = rng.choice([
        f"Give exactly {n} bullet points on {t['subject']}. Bullets only.",
        f"In {n} bullet points and nothing else, cover {t['subject']}.",
    ])
    bad = rng.choice([
        f"Explain {t['subject']} in one flowing sentence. Do not use a list.",
        f"Give exactly {n + 2} bullet points on {t['subject']}. Bullets only.",
        f"Describe {t['subject']} as a numbered list, numbered 1 to {n}.",
        f"Write a short prose paragraph about {t['subject']}. No bullets or numbering.",
    ])
    return _pair(ok, bad, body, "flip_bullets", "format")


def flip_numbered(t, rng):
    n = rng.choice([3, 4])
    items = rng.sample(t["items"], n)
    body = _numbered(items)
    ok = f"List {n} {t['plural']} of {t['subject']} as a numbered list, no preamble."
    bad = rng.choice([
        f"List {n} {t['plural']} of {t['subject']} as bullet points, not numbered.",
        f"Summarise {t['subject']} in a single sentence.",
        f"List {n + 2} {t['plural']} of {t['subject']} as a numbered list.",
    ])
    return _pair(ok, bad, body, "flip_numbered", "format")


def flip_prose(t, rng):
    items = rng.sample(t["items"], 3)
    body = (f"{items[0]}, and {items[1][0].lower() + items[1][1:]}. "
            f"{items[2]}. Taken together these are what make {t['subject']} work the way it does.")
    ok = rng.choice([
        f"Write a short prose paragraph on {t['subject']}. No lists or bullet points.",
        f"Describe {t['subject']} in two or three sentences of continuous prose.",
    ])
    bad = rng.choice([
        f"Give exactly three bullet points on {t['subject']}. Bullets only, no prose.",
        f"Answer with a single word summarising {t['subject']}.",
        f"Reply with a JSON object about {t['subject']} and no prose at all.",
    ])
    return _pair(ok, bad, body, "flip_prose", "format")


def flip_json(t, rng):
    items = rng.sample(t["items"], 2)
    body = json.dumps({"topic": t["subject"], "steps": items}, ensure_ascii=False)
    ok = f"Reply with a JSON object only (keys \"topic\" and \"steps\") about {t['subject']}."
    bad = rng.choice([
        f"Explain {t['subject']} in plain English prose. No JSON, no code, no braces.",
        f"Give two bullet points on {t['subject']}. Plain text only.",
    ])
    return _pair(ok, bad, body, "flip_json", "format")


def flip_refusal(t, rng):
    """Identical decline text: compliant when a decline was requested, not otherwise.

    This is the pair that most directly targets `anthropic_harmless_refusal` — the
    split is about refusing things that did not warrant refusal, and the only way to
    tell the two apart is what was asked.
    """
    ask, decline = rng.choice(DECLINE_REQUESTS)
    benign = rng.choice([
        f"Could you explain {t['subject']} to me in a couple of sentences?",
        f"I'd like a quick rundown of {t['subject']}, please.",
        f"What should I know about {t['subject']} before I start?",
        f"Give me two practical tips on {t['subject']}.",
    ])
    return _pair(ask, benign, decline, "flip_refusal", "refusal")


def flip_language_scope(t, rng):
    """Same answer; one instruction forbids the very term the answer leans on."""
    items = [x for x in t["items"]]
    pick = rng.choice(items)
    key = pick.split()[0].lower().strip(",.")
    body = f"{pick}. That is the part most people underestimate."
    ok = f"In two sentences, tell me something worth knowing about {t['subject']}."
    bad = (f"In two sentences, tell me something worth knowing about {t['subject']}. "
           f"Do not use the word \"{key}\" anywhere in your answer.")
    return _pair(ok, bad, body, "flip_scope", "contradiction")


def flip_multiturn_constraint(t, rng):
    """Same final answer; the standing constraint set in turn 1 differs."""
    n = 3
    items = rng.sample(t["items"], n)
    answer = _bulleted(items)
    t2 = rng.choice([x for x in TOPICS if x["name"] != t["name"]])
    q = f"Now cover {t['subject']}."

    def convo(setup, ack, prior):
        return [{"role": "user", "content": setup},
                {"role": "assistant", "content": ack},
                {"role": "user", "content": f"Start with {t2['subject']}."},
                {"role": "assistant", "content": prior},
                {"role": "user", "content": q},
                {"role": "assistant", "content": answer}]

    prior_items = rng.sample(t2["items"], n)
    ok = convo(f"For this whole conversation, answer in exactly {n} bullet points.",
               f"Understood — {n} bullets each time.", _bulleted(prior_items))
    bad = convo("For this whole conversation, answer in one sentence only. Never use lists.",
                "Understood — one sentence each time.",
                prior_items[0] + ".")
    return [Row(ok, POS, "flip_standing", "compliant"),
            Row(bad, NEG, "flip_standing", "context_drift")]


FLIP_FAMILIES = [
    flip_one_word, flip_bullets, flip_numbered, flip_prose, flip_json,
    flip_refusal, flip_language_scope, flip_multiturn_constraint,
]
