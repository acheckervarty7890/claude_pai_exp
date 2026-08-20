"""Combinatorial refusal and deflection text.

Diagnostic that prompted this: in the v7 mix, the `refusal` mode had **17 unique
response strings across 275 rows** — a uniqueness ratio of 0.06, against 0.39-0.41
for the other modes. The probe was being shown the same handful of sentences sixteen
times each, which teaches it those specific strings rather than the concept of
refusing. `anthropic_harmless_refusal` duly slid from 0.980 (v1s) to 0.793 (v6s) as
refusal rows grew more numerous but no more varied.

Assembling refusals from independent slots turns a handful of hand-written sentences
into thousands of distinct ones that still read naturally, so the mode's uniqueness
ratio comes up to match everything else.
"""

from __future__ import annotations

import random

OPENERS = [
    "I'm sorry, but", "Unfortunately,", "I'm afraid", "Regrettably,",
    "I have to be honest —", "Apologies, but", "Much as I'd like to help,",
    "I appreciate you asking, but", "Thanks for thinking of me, but",
    "I've considered it, and", "To be straightforward with you,",
]

CORES = [
    "I can't help with that",
    "that isn't something I'm able to assist with",
    "I'm not able to advise on this one",
    "this falls outside what I can usefully offer",
    "I'd rather not weigh in here",
    "I don't think I'm the right source for this",
    "I'm going to have to pass on this",
    "I can't give you an answer on that",
    "this isn't a question I should be answering",
    "I'm not comfortable offering guidance here",
    "I won't be able to take this one on",
]

REASONS = [
    "",
    ", as there are too many variables involved",
    ", since the details matter more than I can account for",
    " — the risk of steering you wrong is too high",
    ", because circumstances differ so much case to case",
    " given how much depends on your specific situation",
    ", as I'd only be speculating",
    " without knowing far more than I do",
    ", since getting it wrong could cause real problems",
]

REDIRECTS = [
    "",
    " You'd be better served by someone who can look at the specifics.",
    " A qualified professional would be the right person to ask.",
    " I'd suggest seeking advice from someone with direct experience.",
    " It's worth asking someone who works in this area day to day.",
    " Someone closer to the situation could give you a far better answer.",
    " I hope you're able to find a good source for it.",
    " Do check with an appropriate expert instead.",
    " There are people much better placed than me to answer this.",
]

CLOSERS = [
    "", "", "", "",
    " Sorry not to be more useful.",
    " I hope you understand.",
    " Apologies for not being more help here.",
    " I wish I could be more helpful on this one.",
]


def refusal(rng: random.Random) -> str:
    """One assembled refusal. ~11 x 11 x 9 x 9 x 8 slot combinations."""
    opener = rng.choice(OPENERS)
    core = rng.choice(CORES)
    body = f"{opener} {core}{rng.choice(REASONS)}."
    return (body + rng.choice(REDIRECTS) + rng.choice(CLOSERS)).strip()


def short_refusal(rng: random.Random) -> str:
    """A curt refusal, so refusing is not tied to answer length."""
    return f"{rng.choice(OPENERS)} {rng.choice(CORES)}.".strip()


# ------------------------------------------------------------------ deflection

DEFLECT_OPENERS = [
    "That's a really common question,",
    "This comes up a lot,",
    "It's an interesting one,",
    "People ask about this often,",
    "There's a lot written on this,",
    "Opinions vary widely here,",
    "It's genuinely debated,",
]

DEFLECT_MIDDLES = [
    "and there's a surprising amount of disagreement about it",
    "and the honest answer is that it depends",
    "and reasonable people land in very different places",
    "and the research is less settled than you'd expect",
    "and much of the usual advice contradicts itself",
    "and what works for one person often fails for another",
]

DEFLECT_TAILS = [
    " A great deal comes down to your particular circumstances and what you're trying to achieve.",
    " The right approach really varies with context, budget and how much time you have.",
    " I'd think carefully about what matters most to you before committing to any one route.",
    " It's worth weighing the trade-offs rather than looking for a single correct answer.",
    " Most people end up settling on something through trial and error.",
    " The general principles matter more than any specific recommendation.",
]


def deflection(rng: random.Random) -> str:
    """Talks around the question without answering it — a substitution failure."""
    return (f"{rng.choice(DEFLECT_OPENERS)} {rng.choice(DEFLECT_MIDDLES)}."
            f"{rng.choice(DEFLECT_TAILS)}")


# ------------------------------------------------------------------ generic advice

GENERIC_ADVICE = [
    "Start by writing down what you actually need, then work backwards from there.",
    "Begin with the simplest version that could work and add complexity only when it earns its place.",
    "Set a clear goal first, since everything else follows from what you're optimising for.",
    "Break it into stages and get the first one genuinely finished before moving on.",
    "Establish a baseline you can measure against, or you won't know whether changes help.",
    "Get advice from someone who has done it before — it will save you weeks.",
    "Build in a margin for things going wrong, because they usually do.",
    "Review it after a couple of weeks and adjust based on what you've learned.",
    "Keep a record of what you tried, so you don't repeat the same dead ends.",
    "Focus on consistency rather than intensity; it compounds far better over time.",
]


def generic_advice(rng: random.Random, n: int = 3) -> str:
    """Plausible, on-topic-sounding advice that ignores the stated constraints."""
    return " ".join(rng.sample(GENERIC_ADVICE, min(n, len(GENERIC_ADVICE))))


# ------------------------------------------------------------------ contradiction

BANNED_FRAMES = [
    "The {w} is really the heart of it.",
    "You can't discuss this without the {w}.",
    "It all comes back to the {w} in the end.",
    "Most of the difficulty here is about the {w}.",
    "The {w} is what everything else hangs off.",
    "Start with the {w} and the rest follows.",
    "People underestimate how much the {w} matters here.",
    "Any serious account has to begin with the {w}.",
    "The {w} explains nearly all of the behaviour.",
    "Everything interesting about this involves the {w}.",
]

BANNED_TAILS = [
    "", "", "",
    " That's the piece worth remembering.",
    " Everything else is detail by comparison.",
    " It's the one thing I'd want you to take away.",
    " Once that clicks, the rest is straightforward.",
]


def banned_term_sentence(word: str, rng: random.Random) -> str:
    """A sentence that deliberately uses a forbidden term, in varied phrasing."""
    return rng.choice(BANNED_FRAMES).format(w=word) + rng.choice(BANNED_TAILS)
