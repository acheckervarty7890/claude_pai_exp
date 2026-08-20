"""Generate synthetic training data for the follows-instruction concept.

Design notes
------------
The shipped 50-row seed is narrow in a way that actively hurts: every row is a
2-turn, short, format-constraint exchange, and its negatives run ~2x longer than
its positives (184 vs 92 chars). A probe fit on that learns "long rambling answer
= did not follow", which is a property of the seed, not of the concept.

So this generator is built around two ideas:

1. **Paired generation.** Every instruction yields both a compliant and a
   violating response over the *same* prompt. Topic, vocabulary and register
   cancel between the two classes, leaving the instruction-following distinction
   as the only thing that separates them.

2. **Deliberate length inversion.** Violations are spread across modes that make
   the answer *shorter* (omission, terse substitution, curt refusal) as well as
   longer (overrun, preamble, drift into prose). `balance_by_length` then does a
   final length-stratified match so the two classes have near-identical length
   distributions, killing the shortcut outright.

Negative modes mirror the failure families the eval splits are named for:
refusal, substitution, context drift, contradiction and omission.
"""

from __future__ import annotations

import argparse
import collections
import json
import random
from pathlib import Path

from banks import (BENIGN_REQUESTS, DECLINE_REQUESTS, FORBIDDEN, NEG_LABEL as NEG,
                   POS_LABEL as POS, Row, TOPICS)
from longform import LONGFORM_FAMILIES
from naturalize import naturalize_group
from drift import DRIFT_FAMILIES
from flip import FLIP_FAMILIES, flip_refusal
from refusals import deflection, refusal, short_refusal
from registers import REGISTER_FAMILIES


def _n_words(text: str) -> int:
    return len(text.split())


def _numbered(items):
    return "\n".join(f"{i}. {t}" for i, t in enumerate(items, 1))


def _bulleted(items):
    return "\n".join(f"- {t}" for t in items)


def _prose(items):
    """Join items into a flowing paragraph — the classic 'ignored the format' answer."""
    joined = ", ".join(t[0].lower() + t[1:] for t in items[:-1])
    return f"{joined}, and {items[-1][0].lower() + items[-1][1:]}."


# Phrasing pools, so an instruction family is not one memorisable string.
ASK_LIST = [
    "List exactly {n} {plural} of {subject}. Use a numbered list and no introduction.",
    "Give me {n} {plural} of {subject} — numbered, exactly {n}, nothing before the list.",
    "I need precisely {n} {plural} of {subject}, as a numbered list. Skip any preamble.",
    "Write out {n} {plural} of {subject} in a numbered list. Do not add an intro sentence.",
]
ASK_BULLETS = [
    "Give me {n} {plural} of {subject} as bullet points, {n} bullets exactly.",
    "In {n} bullet points and nothing else, cover {n} {plural} of {subject}.",
]
ASK_SUMMARY = [
    "Summarise the passage below in {n} words or fewer.\n\nPassage: {passage}",
    "In no more than {n} words, summarise this passage.\n\nPassage: {passage}",
    "Condense the following into {n} words maximum.\n\nPassage: {passage}",
]
ASK_EXTRACT = [
    "Using only the passage below, answer in a single word. {q}?\n\nPassage: {passage}",
    "Answer with one word only, drawing solely on this passage. {q}?\n\nPassage: {passage}",
    "{q}? Reply with a single word and use nothing beyond the passage.\n\nPassage: {passage}",
]
ASK_NOWORD = [
    "Explain {subject} in exactly two sentences without using the word \"{w}\".",
    "In two sentences, and never using the word \"{w}\", explain {subject}.",
]
ASK_JSON = [
    "Reply with a JSON object only, with the keys \"topic\" and \"steps\" "
    "(\"steps\" being an array of {n} strings), covering {subject}. No text outside the JSON.",
    "Return only JSON: an object with \"topic\" and a \"steps\" array of {n} strings about {subject}.",
]

FILLER_OPENERS = [
    "That's a great question! ", "Certainly — happy to help with this. ",
    "Interesting topic. ", "Of course. ", "Good one. ",
]


# ---------------------------------------------------------------- families

def fam_numbered_list(t, rng):
    n = rng.choice([3, 4, 5])
    other = rng.choice([x for x in TOPICS if x["name"] != t["name"]])
    items = rng.sample(t["items"], n)
    instr = rng.choice(ASK_LIST).format(n=n, plural=t["plural"], subject=t["subject"])
    u = {"role": "user", "content": instr}
    out = [Row([u, {"role": "assistant", "content": _numbered(items)}], POS, "numbered_list", "compliant")]

    # omission: one item short, each remaining item padded so length still matches
    short = [f"{x}, which matters more than people expect" for x in items[:-1]]
    out.append(Row([u, {"role": "assistant", "content": _numbered(short)}], NEG, "numbered_list", "omission"))
    # overrun: too many items
    extra = rng.sample([x for x in t["items"] if x not in items], min(2, len(t["items"]) - n))
    out.append(Row([u, {"role": "assistant", "content": _numbered(items + extra)}], NEG, "numbered_list", "overrun"))
    # preamble: explicitly forbidden intro
    pre = rng.choice(FILLER_OPENERS) + f"Here are {n} {t['plural']} of {t['subject']}:\n"
    out.append(Row([u, {"role": "assistant", "content": pre + _numbered(items)}], NEG, "numbered_list", "preamble"))
    # format violation: prose instead of a numbered list
    out.append(Row([u, {"role": "assistant", "content": _prose(items)}], NEG, "numbered_list", "format"))
    # substitution: right shape, wrong subject
    sub = rng.sample(other["items"], n)
    out.append(Row([u, {"role": "assistant", "content": _numbered(sub)}], NEG, "numbered_list", "substitution"))
    return out


def fam_bullets(t, rng):
    n = rng.choice([3, 4])
    items = rng.sample(t["items"], n)
    instr = rng.choice(ASK_BULLETS).format(n=n, plural=t["plural"], subject=t["subject"])
    u = {"role": "user", "content": instr}
    out = [Row([u, {"role": "assistant", "content": _bulleted(items)}], POS, "bullets", "compliant")]
    out.append(Row([u, {"role": "assistant", "content": _numbered(items)}], NEG, "bullets", "format"))
    out.append(Row([u, {"role": "assistant", "content": _bulleted(items[:-1])}], NEG, "bullets", "omission"))
    return out


def fam_summary(t, rng):
    n = rng.choice([8, 10, 12, 15])
    instr = rng.choice(ASK_SUMMARY).format(n=n, passage=t["passage"])
    u = {"role": "user", "content": instr}
    # A compliant summary: trimmed to the budget.
    words = t["passage"].replace(".", "").split()
    good = " ".join(words[:n])
    out = [Row([u, {"role": "assistant", "content": good}], POS, "summary", "compliant")]
    # overrun: reproduces the whole passage plus commentary
    out.append(Row([u, {"role": "assistant", "content": t["passage"] + " It's a genuinely fascinating area with a lot of nuance worth exploring further."}],
                   NEG, "summary", "overrun"))
    # substitution: summarises something else entirely
    other = rng.choice([x for x in TOPICS if x["name"] != t["name"]])
    out.append(Row([u, {"role": "assistant", "content": " ".join(other["passage"].replace(".", "").split()[:n])}],
                   NEG, "summary", "substitution"))
    # refusal of a perfectly answerable request
    out.append(Row([u, {"role": "assistant", "content": refusal(rng)}], NEG, "summary", "refusal"))
    return out


def fam_extract(t, rng):
    q, a = rng.choice(t["facts"])
    instr = rng.choice(ASK_EXTRACT).format(q=q, passage=t["passage"])
    u = {"role": "user", "content": instr}
    out = [Row([u, {"role": "assistant", "content": a}], POS, "extract", "compliant")]
    # substitution: answers a different question from the same passage
    others = [x for x in t["facts"] if x[0] != q]
    if others:
        out.append(Row([u, {"role": "assistant", "content": rng.choice(others)[1]}], NEG, "extract", "substitution"))
    # overrun: correct fact, but buried in commentary the instruction forbade
    out.append(Row([u, {"role": "assistant", "content": f"Based on the passage, the answer would be {a}, though it's worth noting that the surrounding context adds quite a bit of useful detail here."}],
                   NEG, "extract", "overrun"))
    # contradiction: denies what the passage plainly says
    out.append(Row([u, {"role": "assistant", "content": "Unclear"}], NEG, "extract", "contradiction"))
    # refusal of an answerable question
    out.append(Row([u, {"role": "assistant", "content": short_refusal(rng)}], NEG, "extract", "refusal"))
    return out


def fam_forbidden_word(t, rng):
    w = FORBIDDEN[t["name"]]
    instr = rng.choice(ASK_NOWORD).format(subject=t["subject"], w=w)
    u = {"role": "user", "content": instr}
    safe = [x for x in t["items"] if w.lower() not in x.lower()][:2]
    if len(safe) < 2:
        return []
    good = f"{safe[0]}. {safe[1]}."
    out = [Row([u, {"role": "assistant", "content": good}], POS, "forbidden_word", "compliant")]
    bad_src = [x for x in t["items"] if w.lower() in x.lower()]
    bad = f"{bad_src[0]}. {safe[0]}." if bad_src else f"The {w} is central here. {safe[0]}."
    out.append(Row([u, {"role": "assistant", "content": bad}], NEG, "forbidden_word", "contradiction"))
    # overrun: four sentences when two were demanded
    out.append(Row([u, {"role": "assistant", "content": f"{safe[0]}. {safe[1]}. {t['items'][-1]}. There is quite a lot more to say about it as well."}],
                   NEG, "forbidden_word", "overrun"))
    return out


def fam_json(t, rng):
    n = rng.choice([2, 3])
    items = rng.sample(t["items"], n)
    instr = rng.choice(ASK_JSON).format(n=n, subject=t["subject"])
    u = {"role": "user", "content": instr}
    good = json.dumps({"topic": t["subject"], "steps": items}, ensure_ascii=False)
    out = [Row([u, {"role": "assistant", "content": good}], POS, "json", "compliant")]
    out.append(Row([u, {"role": "assistant", "content": f"Here's the JSON you asked for:\n```json\n{good}\n```\nLet me know if you'd like more detail."}],
                   NEG, "json", "format"))
    out.append(Row([u, {"role": "assistant", "content": _prose(items)}], NEG, "json", "format"))
    out.append(Row([u, {"role": "assistant", "content": json.dumps({"subject": t["subject"], "points": items}, ensure_ascii=False)}],
                   NEG, "json", "substitution"))
    return out


def fam_benign_refusal(rng):
    q, a = rng.choice(BENIGN_REQUESTS)
    u = {"role": "user", "content": q}
    out = [Row([u, {"role": "assistant", "content": a}], POS, "benign", "compliant")]
    # assembled rather than picked from a list: see refusals.py for why
    out.append(Row([u, {"role": "assistant", "content": refusal(rng)}], NEG, "benign", "refusal"))
    out.append(Row([u, {"role": "assistant", "content": short_refusal(rng)}], NEG, "benign", "refusal"))
    out.append(Row([u, {"role": "assistant", "content": deflection(rng)}], NEG, "benign", "substitution"))
    return out


def fam_decline(rng):
    """Positives whose *correct* answer is refusal-shaped — decorrelates refusal language."""
    q, a = rng.choice(DECLINE_REQUESTS)
    u = {"role": "user", "content": q}
    out = [Row([u, {"role": "assistant", "content": a}], POS, "decline", "compliant")]
    out.append(Row([u, {"role": "assistant", "content": "I'd be glad to help you accept it! Here's a warm note saying you'll be delighted to attend and are looking forward to it enormously."}],
                   NEG, "decline", "contradiction"))
    out.append(Row([u, {"role": "assistant", "content": deflection(rng)}], NEG, "decline", "substitution"))
    return out


def fam_drift(t, rng):
    """Multi-turn: a constraint is set up front, then honoured or abandoned later."""
    n = rng.choice([2, 3])
    setup = rng.choice([
        f"For the rest of this conversation, answer every question in exactly {n} bullet points. No prose.",
        f"Ground rule for this chat: every answer must be {n} bullet points, nothing else.",
        f"Please reply to everything from here on in {n} bullets — no paragraphs, no intros.",
    ])
    ack = rng.choice(["Understood — {n} bullets from here on.", "Got it. {n} bullets each time.",
                      "Sure, I'll keep every answer to {n} bullets."]).format(n=n)
    q1 = f"What's the essence of {t['subject']}?"
    a1 = _bulleted(rng.sample(t["items"], n))
    other = rng.choice([x for x in TOPICS if x["name"] != t["name"]])
    q2 = f"And how does that compare with {other['subject']}?"
    a2_good = _bulleted(rng.sample(other["items"], n))
    a2_drift = _prose(rng.sample(other["items"], n + 1))

    base = [{"role": "user", "content": setup}, {"role": "assistant", "content": ack},
            {"role": "user", "content": q1}, {"role": "assistant", "content": a1},
            {"role": "user", "content": q2}]
    out = [Row(base + [{"role": "assistant", "content": a2_good}], POS, "drift", "compliant"),
           Row(base + [{"role": "assistant", "content": a2_drift}], NEG, "drift", "context_drift")]
    # drift that also shrinks, so the mode is not synonymous with "longer"
    out.append(Row(base + [{"role": "assistant", "content": rng.choice(other["items"]) + "."}],
                   NEG, "drift", "context_drift"))
    return out


def fam_scope_contradiction(t, rng):
    """A stated restriction that the final answer either respects or breaks."""
    w = FORBIDDEN[t["name"]]
    setup = rng.choice([
        f"I'm writing for absolute beginners, so never mention \"{w}\" in your answers.",
        f"Keep the jargon out — in particular, don't use the term \"{w}\" at any point.",
    ])
    ack = "Understood, I'll avoid that term."
    q = f"So, briefly: how would you describe {t['subject']}?"
    safe = [x for x in t["items"] if w.lower() not in x.lower()][:2]
    bad_src = [x for x in t["items"] if w.lower() in x.lower()]
    if len(safe) < 2:
        return []
    base = [{"role": "user", "content": setup}, {"role": "assistant", "content": ack},
            {"role": "user", "content": q}]
    good = f"{safe[0]}, and {safe[1][0].lower() + safe[1][1:]}."
    bad = (f"{bad_src[0]}, and {safe[0][0].lower() + safe[0][1:]}." if bad_src
           else f"The {w} really is the heart of it, and {safe[0][0].lower() + safe[0][1:]}.")
    return [Row(base + [{"role": "assistant", "content": good}], POS, "scope", "compliant"),
            Row(base + [{"role": "assistant", "content": bad}], NEG, "scope", "contradiction")]


def fam_option_letter(t, rng):
    """BBQ-shaped: pick one option, reply with the letter only."""
    q, a = rng.choice(t["facts"])
    distract = [x[1] for x in t["facts"] if x[1] != a]
    if not distract:
        return []
    opts = [a, distract[0], "Not enough information"]
    rng.shuffle(opts)
    letters = "ABC"
    correct = letters[opts.index(a)]
    body = "\n".join(f"({letters[i]}) {o}" for i, o in enumerate(opts))
    instr = (f"Read the passage and answer with the option letter only — a single character, "
             f"no explanation.\n\nPassage: {t['passage']}\n\n{q}?\n{body}")
    u = {"role": "user", "content": instr}
    wrong = letters[opts.index("Not enough information")]
    out = [Row([u, {"role": "assistant", "content": correct}], POS, "option", "compliant")]
    out.append(Row([u, {"role": "assistant", "content": wrong}], NEG, "option", "substitution"))
    out.append(Row([u, {"role": "assistant", "content": f"({correct}) {a} — the passage states this directly, so that's the one that fits best here."}],
                   NEG, "option", "format"))
    return out


def fam_ordering(t, rng):
    items = t["items"][:4]
    instr = f"Put these {t['plural']} of {t['subject']} in the order they happen, numbered 1 to 4, nothing else:\n" + \
            "\n".join(f"- {x}" for x in rng.sample(items, 4))
    u = {"role": "user", "content": instr}
    out = [Row([u, {"role": "assistant", "content": _numbered(items)}], POS, "ordering", "compliant")]
    shuffled = items[::-1]
    out.append(Row([u, {"role": "assistant", "content": _numbered(shuffled)}], NEG, "ordering", "contradiction"))
    out.append(Row([u, {"role": "assistant", "content": _numbered(items[:3])}], NEG, "ordering", "omission"))
    out.append(Row([u, {"role": "assistant", "content": "Here's the correct sequence, with a note on why each step follows the last:\n" + _numbered(items)}],
                   NEG, "ordering", "preamble"))
    return out


def fam_single_sentence(t, rng):
    instr = rng.choice([
        f"In exactly one sentence, explain {t['subject']}.",
        f"Give a one-sentence explanation of {t['subject']} — one sentence, no more.",
    ])
    u = {"role": "user", "content": instr}
    a, b = rng.sample(t["items"], 2)
    out = [Row([u, {"role": "assistant", "content": f"{a}, and {b[0].lower() + b[1:]}, which together define how it works."}],
               POS, "one_sentence", "compliant")]
    out.append(Row([u, {"role": "assistant", "content": f"{a}. {b}. There is more to it than that, of course."}],
                   NEG, "one_sentence", "overrun"))
    return out


# ---------------------------------------------------------------- assembly

def generate(n_target: int, seed: int, longform_weight: int = 3,
             naturalize: bool = True, register_weight: int = 1,
             flip_weight: int = 2, drift_weight: int = 2,
             refusal_weight: int = 2) -> list[Row]:
    rng = random.Random(seed)
    rows: list[Row] = []
    topic_fams = [fam_numbered_list, fam_bullets, fam_summary, fam_extract, fam_forbidden_word,
                  fam_json, fam_drift, fam_scope_contradiction, fam_option_letter,
                  fam_ordering, fam_single_sentence]
    guard = 0
    while len(rows) < n_target * 3 and guard < 6000:
        guard += 1
        t = rng.choice(TOPICS)
        # long-form families are drawn more often: they are the ones that match the
        # 159-436 token sequence lengths the probe is actually scored over.
        def emit(group):
            rows.extend(naturalize_group(group, rng) if naturalize else group)

        for _ in range(longform_weight):
            lt = rng.choice(TOPICS)
            emit(rng.choice(LONGFORM_FAMILIES)(lt, rng))
        emit(rng.choice(topic_fams)(t, rng))
        if register_weight:
            for _ in range(register_weight):
                emit(rng.choice(REGISTER_FAMILIES)(t, rng))
        for _ in range(flip_weight):
            emit(rng.choice(FLIP_FAMILIES)(rng.choice(TOPICS), rng))
        # drift/omission families are weighted up: after v1 these were the three worst
        # eval splits (context drift 0.640/0.649, omission 0.700).
        for _ in range(drift_weight):
            emit(rng.choice(DRIFT_FAMILIES)(t, rng))
        # refusal is one whole eval split but the thinnest supply, so it is drawn
        # several times per round -- otherwise the mode quota below has to shrink the
        # entire dataset to hit its refusal share.
        for _ in range(refusal_weight):
            emit(fam_benign_refusal(rng))
            emit(fam_decline(rng))
            emit(flip_refusal(rng.choice(TOPICS), rng))
    # de-duplicate on exact conversation text
    seen, uniq = set(), []
    for r in rows:
        k = json.dumps(r.messages, sort_keys=True)
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    return uniq



# Share of negatives to aim for per failure mode, proportional to how many eval
# splits test each one: substitution and context drift have two splits each
# (bbq_/mm_ and hc_/oig_), refusal, contradiction and omission one each. The
# remainder goes to the format-style violations the original seed was made of.
#
# This exists because mode share was previously whatever fell out of the family
# weights, and it drifted badly: in the v3 mix refusal was 4.1% of negatives, and
# refusal duly regressed from 0.980 to 0.859 on the eval split that tests it.
CORE_MODES = ("substitution", "context_drift", "refusal", "contradiction", "omission")

MODE_QUOTA = {
    "substitution": 0.22,
    "context_drift": 0.22,
    "refusal": 0.14,
    "contradiction": 0.14,
    "omission": 0.14,
    "format": 0.07,
    "overrun": 0.05,
    "preamble": 0.02,
}


def enforce_mode_quota(rows: list[Row], rng: random.Random,
                       quota: dict | None = None) -> list[Row]:
    """Resample negatives toward `quota`, then length-match positives to them.

    Two-step so neither property is lost: the quota fixes *which failure modes* the
    probe sees, and the length-stratified positive match keeps response length
    uninformative about the label afterwards.
    """
    quota = quota or MODE_QUOTA
    pos = [r for r in rows if r.label == POS]
    neg = [r for r in rows if r.label == NEG]
    if not pos or not neg:
        return rows

    by_mode = collections.defaultdict(list)
    for r in neg:
        by_mode[r.mode].append(r)
    for v in by_mode.values():
        rng.shuffle(v)

    # Size the negative set by the *core* modes only -- the five failure families the
    # eval splits actually test. Sizing by every mode let a 2%-share rarity
    # (preamble) shrink the dataset by half; sizing by whichever mode had surplus let
    # refusal balloon to 28%. Core-only keeps the proportions that matter honest and
    # lets the incidental format-style modes fill in with whatever exists.
    core = [m for m in CORE_MODES if quota.get(m)]
    budget = min(len(neg), len(pos))
    feasible = min((len(by_mode.get(m, [])) / quota[m] for m in core), default=budget)
    budget = int(min(budget, feasible))

    take = {}
    for m, q in quota.items():
        take[m] = min(int(budget * q), len(by_mode.get(m, [])))

    kept_neg = []
    for m, n in take.items():
        kept_neg.extend(by_mode.get(m, [])[:n])

    kept_pos = _match_lengths(pos, kept_neg, rng)
    out = kept_pos + kept_neg
    rng.shuffle(out)
    return out


def _match_lengths(pool: list[Row], target: list[Row], rng: random.Random,
                   bins: int = 10) -> list[Row]:
    """Pick from `pool` so its response-length histogram mirrors `target`'s."""
    def alen(r):
        return len(r.messages[-1]["content"])

    lens = sorted(alen(r) for r in target)
    edges = [lens[int(len(lens) * i / bins)] for i in range(1, bins)]

    def bucket(r):
        v = alen(r)
        return sum(v > e for e in edges)

    want = collections.Counter(bucket(r) for r in target)
    have = collections.defaultdict(list)
    for r in pool:
        have[bucket(r)].append(r)
    for v in have.values():
        rng.shuffle(v)

    out, deficit = [], 0
    for b, n in want.items():
        got = have[b][:n]
        out.extend(got)
        deficit += n - len(got)
    if deficit:
        leftover = [r for b in have for r in have[b][want.get(b, 0):]]
        rng.shuffle(leftover)
        out.extend(leftover[:deficit])
    return out


def _pick_across_modes(rows: list[Row], k: int, rng: random.Random) -> list[Row]:
    """Take k rows, cycling across failure modes instead of sampling uniformly.

    Uniform sampling inside a length bucket wiped out whole modes — `refusal`
    disappeared from lf_chat entirely, even though `anthropic_harmless_refusal` is
    one of the eval splits. Round-robin keeps every mode represented right up to the
    point where the bucket runs out of it.
    """
    by_mode = collections.defaultdict(list)
    for r in rows:
        by_mode[r.mode].append(r)
    for v in by_mode.values():
        rng.shuffle(v)
    modes = sorted(by_mode)
    picked = []
    while len(picked) < k:
        progressed = False
        for m in modes:
            if by_mode[m] and len(picked) < k:
                picked.append(by_mode[m].pop())
                progressed = True
        if not progressed:
            break
    return picked


def balance_by_length(rows: list[Row], rng: random.Random, bins: int = 8) -> list[Row]:
    """Length-stratified class matching, applied **within each family**.

    Bucket rows by the character length of the assistant turn and keep equal numbers
    of positives and negatives in each bucket. Stratifying per family matters: done
    globally it silently deleted every `lf_standing` context-drift negative, because
    drift is intrinsically longer than compliance and no bucket held both classes.
    Per family — now that each family emits both terse-target and verbose-target
    flavours — the buckets overlap and every failure mode survives.
    """
    def alen(r):
        return len(r.messages[-1]["content"])

    by_family = collections.defaultdict(list)
    for r in rows:
        by_family[r.family].append(r)

    out = []
    for fam, frows in by_family.items():
        lens = sorted(alen(r) for r in frows)
        edges = [lens[int(len(lens) * i / bins)] for i in range(1, bins)]

        def bucket(r):
            v = alen(r)
            return sum(v > e for e in edges)

        by = collections.defaultdict(lambda: {POS: [], NEG: []})
        for r in frows:
            by[bucket(r)][r.label].append(r)
        for b in sorted(by):
            p, n = by[b][POS], by[b][NEG]
            k = min(len(p), len(n))
            if k == 0:
                continue
            out.extend(rng.sample(p, k))
            out.extend(_pick_across_modes(n, k, rng))
    rng.shuffle(out)
    return out


def _corr(xs, ys) -> float:
    n = len(xs)
    if not n:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    return num / (dx * dy) if dx and dy else 0.0


def prompt_corr(rows: list[Row]) -> float:
    """Correlation between *user*-side length and the label.

    The flip families pair one response with two different instructions, so the
    instruction is where a new shortcut could appear if the violating prompt were
    systematically longer.
    """
    xs = [sum(len(m["content"]) for m in r.messages if m["role"] == "user") for r in rows]
    ys = [1.0 if r.label == NEG else 0.0 for r in rows]
    return _corr(xs, ys)


def length_corr(rows: list[Row]) -> float:
    """Point-biserial correlation between assistant-turn length and the label.

    This is the number that matters: near 0 means a probe cannot cheat by reading
    response length. The shipped seed sits around +0.5.
    """
    xs = [len(r.messages[-1]["content"]) for r in rows]
    ys = [1.0 if r.label == NEG else 0.0 for r in rows]
    return _corr(xs, ys)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=1200, help="approximate target row count")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--include-seed", type=Path, default=None,
                    help="original seed jsonl to prepend (kept verbatim)")
    ap.add_argument("--no-balance", action="store_true")
    ap.add_argument("--no-quota", action="store_true",
                    help="skip failure-mode quota rebalancing")
    ap.add_argument("--no-naturalize", action="store_true",
                    help="skip the user-turn surface-variation layer")
    ap.add_argument("--register-weight", type=int, default=1,
                    help="email/code/table/creative family draws per round")
    ap.add_argument("--flip-weight", type=int, default=2,
                    help="context-flip (same response, opposite label) draws per round")
    ap.add_argument("--drift-weight", type=int, default=2,
                    help="context-drift / long-context omission draws per round")
    ap.add_argument("--refusal-weight", type=int, default=2,
                    help="benign-refusal / decline / refusal-flip draws per round")
    ap.add_argument("--longform-weight", type=int, default=3,
                    help="long-form family draws per generation round (0 = v1 behaviour)")
    args = ap.parse_args()

    rng = random.Random(args.seed + 991)
    rows = generate(args.n, args.seed, longform_weight=args.longform_weight,
                    naturalize=not args.no_naturalize,
                    register_weight=args.register_weight,
                    flip_weight=args.flip_weight,
                    drift_weight=args.drift_weight,
                    refusal_weight=args.refusal_weight)
    if not args.no_balance:
        rows = balance_by_length(rows, rng)
    if not args.no_quota:
        rows = enforce_mode_quota(rows, rng)
    rng.shuffle(rows)
    rows = rows[: args.n]
    # trim to a class-balanced set
    pos = [r for r in rows if r.label == POS]
    neg = [r for r in rows if r.label == NEG]
    k = min(len(pos), len(neg))
    rows = pos[:k] + neg[:k]
    rng.shuffle(rows)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        if args.include_seed:
            for line in open(args.include_seed):
                if line.strip():
                    f.write(line if line.endswith("\n") else line + "\n")
        for r in rows:
            f.write(json.dumps({"inputs": json.dumps(r.messages, ensure_ascii=False),
                                "labels": r.label}, ensure_ascii=False) + "\n")

    # report
    fam = collections.Counter((r.family, r.mode) for r in rows)
    plen = [len(r.messages[-1]["content"]) for r in rows if r.label == POS]
    nlen = [len(r.messages[-1]["content"]) for r in rows if r.label == NEG]
    turns = collections.Counter(len(r.messages) for r in rows)
    print(f"wrote {args.out}  rows={len(rows)} (+seed)" if args.include_seed else
          f"wrote {args.out}  rows={len(rows)}")
    print(f"  pos={len(plen)} neg={len(nlen)}")
    print(f"  assistant-turn chars: pos mean {sum(plen)/len(plen):.0f}  neg mean {sum(nlen)/len(nlen):.0f}")
    print(f"  turns: {dict(sorted(turns.items()))}")
    print(f"  response-length/label corr: {length_corr(rows):+.3f}  (seed is about +0.4)")
    print(f"  prompt-length/label corr:   {prompt_corr(rows):+.3f}")
    modes = collections.Counter(r.mode for r in rows if r.label == NEG)
    tot = sum(modes.values()) or 1
    print("  negative-mode mix: " + ", ".join(
        f"{m} {100 * n / tot:.0f}%" for m, n in modes.most_common()))
    for (f_, m), c in sorted(fam.items()):
        print(f"    {f_:16s} {m:16s} {c}")


if __name__ == "__main__":
    main()
