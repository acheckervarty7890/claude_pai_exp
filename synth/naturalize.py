"""Surface-variation layer applied to generated conversations.

Everything in `gen_synth` / `longform` is composed from a fixed set of phrasings, so
without this the probe can pick up on template regularities that carry no meaning —
"user turn starts with 'List exactly'" and so on. These perturbations touch only the
*user* side and only the wrapper around the instruction, so the compliant/violating
distinction of the paired responses is untouched: a pair still shares its prompt
exactly, because the same perturbation is applied to both members of the pair.
"""

from __future__ import annotations

import random

PREFIXES = [
    "", "", "", "Hi — ", "Hey, ", "Quick one: ", "OK so ", "Right, ",
    "Sorry to bother you, but ", "When you get a sec, ", "Morning! ",
]

SUFFIXES = [
    "", "", "", "\n\nThanks!", "\n\nAppreciate it.", "\n\nThanks in advance.",
    "\n\nNo rush.", "\n\nCheers.", "\n\nLet me know if that's not clear.",
]

CONTEXT_PREAMBLES = [
    "", "", "",
    "I'm putting together some notes for a colleague. ",
    "This is for a short internal wiki page. ",
    "I'm revising for an exam next week. ",
    "Writing this up for a newsletter, so format matters. ",
    "A client asked me this and I want to get it right. ",
    "I'm drafting training material for new starters. ",
]

# Light, realistic typos — applied rarely and never inside the constraint clause.
TYPOS = {
    "the": "teh", "and": "adn", "please": "pls", "you": "yuo",
    "with": "wiht", "that": "taht", "about": "abuot",
}


def _typo(text: str, rng: random.Random) -> str:
    words = text.split(" ")
    idxs = [i for i, w in enumerate(words) if w.lower() in TYPOS]
    if not idxs:
        return text
    i = rng.choice(idxs)
    words[i] = TYPOS[words[i].lower()]
    return " ".join(words)


def perturb_user(content: str, rng: random.Random) -> str:
    """Wrap a user instruction in incidental conversational surface.

    A turn that opens with a document delimiter gets its preamble placed *above* the
    block rather than glued onto it — "Right, --- CONTEXT ---" reads as corruption
    rather than as natural surface variation.
    """
    lead = rng.choice(CONTEXT_PREAMBLES) + rng.choice(PREFIXES)
    if content.lstrip().startswith("---"):
        out = (lead.strip() + "\n\n" + content) if lead.strip() else content
    else:
        out = lead + content
    if rng.random() < 0.12:
        out = _typo(out, rng)
    return out + rng.choice(SUFFIXES)


def naturalize_group(rows, rng: random.Random):
    """Apply one shared perturbation to every row produced by a single family call.

    Sharing it across the group is the whole point: the positive and the negatives
    were generated over the same prompt, and they must stay that way or the classes
    become separable by their wrapper text rather than by the response.
    """
    if not rows:
        return rows
    # A family call may branch on flavour, so key the perturbation per distinct user turn.
    seeds = {}
    out = []
    for r in rows:
        msgs = []
        for m in r.messages:
            if m["role"] != "user":
                msgs.append(m)
                continue
            key = m["content"]
            if key not in seeds:
                seeds[key] = perturb_user(key, rng)
            msgs.append({"role": "user", "content": seeds[key]})
        out.append(r._replace(messages=msgs))
    return out
