"""Shared helpers for the synthetic hu_ha pools.

Each pool module exposes lists of ``(label, messages)`` pairs. ``build.py`` collects
them, de-duplicates, balances the classes and writes the JSONL that ``train.py``
consumes (``{"inputs": <json string of messages>, "labels": <class label>}``).
"""

POS = "harmful_to_human"       # the exchange harms a human
NEG = "not_harmful_to_human"   # it does not


def U(text):
    return {"role": "user", "content": text}


def A(text):
    return {"role": "assistant", "content": text}


def pair(label, *msgs):
    return (label, list(msgs))
