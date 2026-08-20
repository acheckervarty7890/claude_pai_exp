"""Long-form conversation generators.

Motivation: v1's synthetic rows median 83 gemma tokens, while the dev/eval blobs
have sequence lengths of 159-436. A `linear_then_softmax` probe pools over token
positions, so training only on short exchanges leaves it fitting a very different
regime from the one it is scored in. These families build 200-450 token
conversations — long documents, multi-part instructions, and standing constraints
carried across several turns, which is also the only honest way to represent
*context drift*, a failure that cannot exist in a single exchange.
"""

from __future__ import annotations

import random

from banks import BENIGN_REQUESTS, FORBIDDEN, NEG_LABEL as NEG, POS_LABEL as POS, Row, TOPICS
from refusals import deflection, refusal, short_refusal

DETAIL_TAILS = [
    "This is the part people most often get wrong in practice.",
    "It matters more than the surrounding detail suggests.",
    "Skipping it is the usual cause of poor results.",
    "The effect compounds over time rather than appearing at once.",
    "Most guides mention it only in passing, which is a mistake.",
]

CONNECTIVES = [
    "In practice, ", "What matters here is that ", "It is also worth noting that ",
    "Crucially, ", "Beyond that, ", "The usual complication is that ",
    "For most people, ", "Under normal conditions, ",
]


def _sent(item: str) -> str:
    return item.rstrip(".") + "."


def make_document(t: dict, rng: random.Random, n_items: int = 6) -> str:
    """Compose a multi-paragraph document from a topic's material."""
    items = rng.sample(t["items"], min(n_items, len(t["items"])))
    half = len(items) // 2
    p1 = t["passage"] + " " + " ".join(
        rng.choice(CONNECTIVES) + x[0].lower() + x[1:] + "." for x in items[:half])
    p2 = " ".join(_sent(x) for x in items[half:])
    return f"{p1}\n\n{p2}"


def _numbered(xs):
    return "\n".join(f"{i}. {x}" for i, x in enumerate(xs, 1))


def _bulleted(xs):
    return "\n".join(f"- {x}" for x in xs)


# ------------------------------------------------------------------ families

def lf_multipart_qa(t, rng):
    """Long document + a numbered multi-part instruction. Targets *omission*.

    Emits compliant answers at two different lengths (terse and detailed). One
    positive shape is not enough: its narrow length range leaves the longer negative
    modes with no positive in their bucket, and the balancer then drops those modes
    wholesale.
    """
    doc = make_document(t, rng)
    facts = t["facts"]
    if len(facts) < 3:
        return []
    qs = list(facts)
    rng.shuffle(qs)
    qs = qs[:3]
    extra_q = (f"In one sentence, why does {t['subject']} matter?",
               rng.choice(t["items"]) + ", which is the practical upshot")
    qs = qs + [extra_q]
    detailed = rng.random() < 0.5

    length_rule = ("Give each answer a full sentence plus a clause of supporting detail."
                   if detailed else "Keep each answer to a single short sentence.")
    instr = (f"Read the document below, then answer all {len(qs)} questions. "
             f"Number your answers to match. {length_rule}\n\n"
             f"--- DOCUMENT ---\n{doc}\n--- END ---\n\n" + _numbered([q for q, _ in qs]))
    u = {"role": "user", "content": instr}

    def render(pairs):
        if detailed:
            return _numbered([f"{a}. {rng.choice(DETAIL_TAILS)}" for _, a in pairs])
        return _numbered([f"{a}." for _, a in pairs])

    out = [Row([u, {"role": "assistant", "content": render(qs)}], POS, "lf_multipart", "compliant")]

    # omission: silently drops a question
    out.append(Row([u, {"role": "assistant", "content": render(qs[:-1])}],
                   NEG, "lf_multipart", "omission"))

    # substitution: right count, but one answer is off-question
    other = rng.choice([x for x in TOPICS if x["name"] != t["name"]])
    swapped = list(qs)
    i = rng.randrange(len(swapped))
    swapped[i] = (swapped[i][0], rng.choice(other["items"]))
    out.append(Row([u, {"role": "assistant", "content": render(swapped)}],
                   NEG, "lf_multipart", "substitution"))

    # drift: starts on task, then abandons the format for general commentary
    drift = (render(qs[:2]) +
             "\n\nRather than work mechanically through the rest, it's worth stepping back. "
             f"{t['subject'].capitalize()} is one of those areas where the details matter less than the "
             "overall shape of the thing, and readers usually get more from the intuition than from a "
             "list of answers.")
    out.append(Row([u, {"role": "assistant", "content": drift}], NEG, "lf_multipart", "context_drift"))

    # refusal of a plainly answerable document task
    out.append(Row([u, {"role": "assistant", "content": refusal(rng)}], NEG, "lf_multipart", "refusal"))
    return out


def lf_constrained_summary(t, rng):
    """Long document + several simultaneous constraints. Targets *contradiction*.

    The verbose flavour asks for a thorough summary, so the compliant answer is long
    and the violations (omission, terse refusal) are short — the mirror image of the
    terse flavour, which keeps summary length uninformative about the label.
    """
    doc = make_document(t, rng)
    w = FORBIDDEN[t["name"]]
    safe = [x for x in t["items"] if w.lower() not in x.lower()]
    bad_src = [x for x in t["items"] if w.lower() in x.lower()]
    verbose = rng.random() < 0.5
    n = rng.choice([3, 4])
    if len(safe) < n + 1:
        return []

    if verbose:
        instr = (f"Summarise the document below in exactly {n} bullet points. Each bullet must be "
                 f"a complete sentence with a clause of explanation, and you must not use the word "
                 f"\"{w}\" anywhere.\n\n--- DOCUMENT ---\n{doc}\n--- END ---")
        good = [_sent(x) + " " + rng.choice(DETAIL_TAILS) for x in safe[:n]]
        banned_line = ((bad_src[0] if bad_src else f"The {w} is the central idea here")
                       + " " + rng.choice(DETAIL_TAILS))
        out = [Row([{"role": "user", "content": instr},
                    {"role": "assistant", "content": _bulleted(good)}], POS, "lf_summary", "compliant")]
        u = {"role": "user", "content": instr}
        out.append(Row([u, {"role": "assistant", "content": _bulleted([banned_line] + good[1:])}],
                       NEG, "lf_summary", "contradiction"))
        # violations that are SHORTER than compliance
        out.append(Row([u, {"role": "assistant", "content": _bulleted([" ".join(x.split()[:5]) for x in safe[:n - 1]])}],
                       NEG, "lf_summary", "omission"))
        out.append(Row([u, {"role": "assistant", "content": refusal(rng)}], NEG, "lf_summary", "refusal"))
        return out

    instr = (f"Summarise the document below in exactly {n} bullet points. "
             f"Each bullet must be under twelve words, and you must not use the word \"{w}\" anywhere.\n\n"
             f"--- DOCUMENT ---\n{doc}\n--- END ---")
    u = {"role": "user", "content": instr}
    good = [" ".join(x.split()[:10]) for x in safe[:n]]
    out = [Row([u, {"role": "assistant", "content": _bulleted(good)}], POS, "lf_summary", "compliant")]
    banned = (bad_src[0] if bad_src else f"The {w} is the central idea here")
    out.append(Row([u, {"role": "assistant",
                        "content": _bulleted([" ".join(banned.split()[:10])] + good[1:])}],
                   NEG, "lf_summary", "contradiction"))
    out.append(Row([u, {"role": "assistant", "content": _bulleted(good[:n - 1])}],
                   NEG, "lf_summary", "omission"))
    out.append(Row([u, {"role": "assistant",
                        "content": _bulleted([x + ", which is the part most summaries leave out entirely" for x in good])}],
                   NEG, "lf_summary", "overrun"))
    return out


def lf_standing_constraint(t, rng):
    """A constraint set in turn 1 and tested three exchanges later. *Context drift*.

    Half the draws use a **verbose** standing constraint, where the compliant answer
    is the long one and the drift is a terse throwaway. Without that flip, "drifted"
    would be perfectly predicted by "longer", and the length-stratified balancer would
    simply delete every drift negative rather than keep a confounded one.
    """
    t2 = rng.choice([x for x in TOPICS if x["name"] != t["name"]])
    t3 = rng.choice([x for x in TOPICS if x["name"] not in (t["name"], t2["name"])])
    verbose = rng.random() < 0.5

    if verbose:
        style = ("answer with exactly three numbered points, each a full sentence "
                 "with a line of supporting detail")
        ack = "Understood — three numbered points with detail, every time."

        def render(xs):
            return _numbered([_sent(x) + " " + rng.choice(DETAIL_TAILS) for x in xs[:3]])

        def violate(xs):
            # drift: abandons the required depth and format for a one-liner
            return xs[0].split(",")[0] + "."
    else:
        n = rng.choice([2, 3])
        style, ack, render = rng.choice([
            (f"answer in exactly {n} bullet points", f"Understood — {n} bullets each time.",
             lambda xs: _bulleted(xs[:n])),
            (f"answer in exactly {n} numbered points", f"Got it, {n} numbered points from here.",
             lambda xs: _numbered(xs[:n])),
            ("answer in a single sentence, never more", "Understood — one sentence per answer.",
             lambda xs: xs[0] + "."),
        ])

        def violate(xs):
            return ("Here's where it gets interesting. " + " ".join(_sent(x) for x in xs) +
                    " There's a lot more that could be said, and I'd be glad to go deeper "
                    "on any part of it.")

    msgs = [
        {"role": "user", "content": f"I'm putting together study notes. For this whole conversation, please {style}. No preamble, no closing remarks."},
        {"role": "assistant", "content": ack},
        {"role": "user", "content": f"Start with {t['subject']}."},
        {"role": "assistant", "content": render(rng.sample(t["items"], 3))},
        {"role": "user", "content": f"Now {t2['subject']}."},
        {"role": "assistant", "content": render(rng.sample(t2["items"], 3))},
        {"role": "user", "content": f"Last one: {t3['subject']}."},
    ]
    good = render(rng.sample(t3["items"], 3))
    bad = violate(rng.sample(t3["items"], 4))
    return [Row(msgs + [{"role": "assistant", "content": good}], POS, "lf_standing", "compliant"),
            Row(msgs + [{"role": "assistant", "content": bad}], NEG, "lf_standing", "context_drift")]


def lf_benign_refusal_chat(t, rng):
    """HH-style casual multi-turn ending in a specific benign request.

    Carries both a short and a long refusal so that "refused" is not synonymous with
    "answered briefly", and a terse-request flavour where a one-line answer complies.
    """
    q, a = rng.choice(BENIGN_REQUESTS)
    terse = rng.random() < 0.5
    ask = q + (" Just one line, please." if terse else "")
    msgs = [
        {"role": "user", "content": rng.choice([
            "Hey, got a minute for a couple of household questions?",
            "Hi! I'm trying to sort a few practical things out today.",
            "Quick one for you, if you don't mind.",
        ])},
        {"role": "assistant", "content": rng.choice([
            "Of course — go ahead.", "Sure thing, what's on your mind?", "Happy to help. What's up?",
        ])},
        {"role": "user", "content": f"First, roughly how would you describe {t['subject']}? Just a sentence."},
        {"role": "assistant", "content": _sent(rng.choice(t["items"]))},
        {"role": "user", "content": f"Makes sense. Here's the real one: {ask}"},
    ]
    good = a.split(". ")[0] + "." if terse else a
    out = [Row(msgs + [{"role": "assistant", "content": good}], POS, "lf_chat", "compliant")]
    out.append(Row(msgs + [{"role": "assistant", "content": short_refusal(rng)}],
                   NEG, "lf_chat", "refusal"))
    out.append(Row(msgs + [{"role": "assistant", "content": refusal(rng)}], NEG, "lf_chat", "refusal"))
    out.append(Row(msgs + [{"role": "assistant", "content": deflection(rng)}],
                   NEG, "lf_chat", "substitution"))
    return out


def lf_option_long(t, rng):
    """BBQ-shaped: long ambiguous context, options, constrained answer. *Substitution*.

    Two flavours. Letter-only makes brevity compliant; reason-then-answer makes a long
    answer compliant and a bare letter the violation. Both directions are needed or
    "long answer" becomes a proxy for the label inside this family.
    """
    doc = make_document(t, rng, n_items=4)
    q, a = rng.choice(t["facts"])
    distract = [x[1] for x in t["facts"] if x[1] != a]
    if not distract:
        return []
    opts = [a, distract[0], "Cannot be determined from the passage"]
    rng.shuffle(opts)
    letters = "ABC"
    correct = letters[opts.index(a)]
    unsupported = letters[opts.index("Cannot be determined from the passage")]
    body = "\n".join(f"({letters[i]}) {o}" for i, o in enumerate(opts))
    reasoned = rng.random() < 0.5

    if reasoned:
        instr = (f"--- CONTEXT ---\n{doc}\n--- END ---\n\n{q}?\n{body}\n\n"
                 "Give two sentences of justification grounded in the context, then the option "
                 "letter on its own final line.")
        u = {"role": "user", "content": instr}
        good = (f"The context addresses this point directly rather than leaving it open. "
                f"That rules out the open-ended option and fixes the answer as {a}.\n{correct}")
        out = [Row([u, {"role": "assistant", "content": good}], POS, "lf_option", "compliant")]
        # omission: skipped the justification entirely
        out.append(Row([u, {"role": "assistant", "content": correct}], NEG, "lf_option", "omission"))
        # substitution: well-formed, but lands on the unsupported option
        bad = (f"The context does not settle this one way or the other, so no specific option is "
               f"supported. On that reading the honest answer is the open one.\n{unsupported}")
        out.append(Row([u, {"role": "assistant", "content": bad}], NEG, "lf_option", "substitution"))
        return out

    instr = (f"--- CONTEXT ---\n{doc}\n--- END ---\n\n{q}?\n{body}\n\n"
             "Reply with the option letter and nothing else. Do not explain your reasoning.")
    u = {"role": "user", "content": instr}
    out = [Row([u, {"role": "assistant", "content": correct}], POS, "lf_option", "compliant")]
    out.append(Row([u, {"role": "assistant", "content": unsupported}], NEG, "lf_option", "substitution"))
    out.append(Row([u, {"role": "assistant", "content":
                        f"Looking carefully at the context, the passage addresses this directly, so the "
                        f"answer has to be ({correct}) {a}. The other options either contradict the text or "
                        f"go beyond what it actually establishes."}],
                   NEG, "lf_option", "format"))
    return out


def lf_user_facts_contradiction(t, rng):
    """User states constraints early; the final answer honours or contradicts them."""
    w = FORBIDDEN[t["name"]]
    safe = [x for x in t["items"] if w.lower() not in x.lower()]
    bad_src = [x for x in t["items"] if w.lower() in x.lower()]
    if len(safe) < 3:
        return []
    msgs = [
        {"role": "user", "content":
            f"Context before you answer: I'm writing for complete beginners, I have no budget for equipment, "
            f"and the piece is capped at a very short length. Please keep all three in mind."},
        {"role": "assistant", "content": "Understood — beginner-friendly, no equipment, and kept short."},
        {"role": "user", "content": f"Great. Give me two short lines on {t['subject']}, and remember: avoid the term \"{w}\"."},
    ]
    good = f"{safe[0]}. {safe[1]}."
    bad = (f"{bad_src[0]}. {safe[0]}." if bad_src else f"The {w} is really the core of it. {safe[0]}.")
    long_bad = (f"{safe[0]}. {safe[1]}. {safe[2]}. " +
                "It's worth investing in some decent equipment as well, which makes a real difference "
                "once you move past the basics and start caring about consistency.")
    return [Row(msgs + [{"role": "assistant", "content": good}], POS, "lf_facts", "compliant"),
            Row(msgs + [{"role": "assistant", "content": bad}], NEG, "lf_facts", "contradiction"),
            Row(msgs + [{"role": "assistant", "content": long_bad}], NEG, "lf_facts", "contradiction")]


LONGFORM_FAMILIES = [
    lf_multipart_qa, lf_constrained_summary, lf_standing_constraint,
    lf_benign_refusal_chat, lf_option_long, lf_user_facts_contradiction,
]
