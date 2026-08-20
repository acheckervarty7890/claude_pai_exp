# Experiment 1 — raising eval AUROC on the *follows-instruction* concept

Branch: `experiment_1_dev`. Concept: `assistant_follows_the_instruction` vs
`assistant_does_not_follow_the_instruction`.

The only permitted lever is **synthetic training data**. `evaluation.py` is used as
shipped (CLI arguments only — no code changes). Model selection is done on the
**dev** splits; the **eval** splits are read only to confirm each iteration's result,
so the held-out set is not being tuned against directly.

## Setup

| item | value |
|---|---|
| extraction model | `google/gemma-3-27b-it`, layer **32** (dictated by the published activation blobs) |
| probe type | `linear_then_softmax` (fixed by the harness) |
| memory pinning | `MAX_MEMORY="0=22GiB,cpu=45GiB"`, `OFFLOAD_BUFFERS=true` |
| dev / eval | 7 splits each, labels-only, precomputed activations from Kaggle |

### Memory pinning — the `cuda:0` form does not work

The task asked for `"cuda:0=22GiB,cpu=45GiB"`. That fails, and **not** inside
tuberlens. tuberlens parses it correctly and hands accelerate
`max_memory={'cuda:0': '22GiB', 'cpu': '45GiB'}`; accelerate then rejects it:

```
ValueError: Device cuda:0 is not recognized, available devices are
integers(for GPU/XPU), 'mps', 'cpu' and 'disk'
```

Accelerate requires **integer** GPU keys, so no tuberlens patch could have made
`cuda:0` work — the constraint lives a layer below. The ordinal form encodes the
identical budget and is what every run uses:

```
[tuberlens] loading google/gemma-3-27b-it on device_map='auto'; max_memory={0: '22GiB', 'cpu': '45GiB'}
Some parameters are on the meta device because they were offloaded to the cpu.
```

Confirmed healthy: 23.4 GB resident on the RTX 3090, remainder on CPU, **no disk
offload**. Throughput ≈ 1.6 s/row for activation extraction.

## Results

Mean AUROC across the 7 splits (higher is better; 0.5 = chance).

| iteration | training data | rows | dev mean AUROC | eval mean AUROC |
|---|---|---|---|---|
| baseline | shipped seed only | 50 | 0.4808 | **0.4991** |

The shipped seed produces a probe at **exactly chance**. Diagnosis below.

## Why the seed fails

Inspecting `init_seed_instructions_50.jsonl` (training data — fair game):

1. **Length confound.** Negative responses average **184** characters, positives
   **92**. The strongest learnable signal in the seed is "long, rambling answer =
   did not follow", which is a property of how the seed was written, not of the
   concept.
2. **Uniform shape.** All 50 rows are 2-turn, single-constraint, format-style
   requests ("in exactly two sentences", "one word only").
3. **Narrow failure modes.** The seed's negatives are almost entirely *verbosity /
   preamble* violations.

Meanwhile the dev/eval split names (from the public Kaggle manifest, not from the
held-out files) advertise five quite different failure families:

`anthropic_harmless_refusal`, `bbq_substitution`, `mm_substitution`,
`hc_context_drift`, `oig_context_drift`, `hc_contradiction`, `oig_omission`

— i.e. **refusal, substitution, context drift, contradiction, omission**. Only one
of those is really represented in the seed, and 40 training rows cannot support a
5376-dimensional probe regardless.

## Approach

`synth/gen_synth.py` + `synth/banks.py` generate paired data:

- **Paired generation** — every instruction yields both a compliant and a violating
  response over the *same* prompt, so topic and register cancel between classes.
- **Length inversion + stratified matching** — violation modes that shorten the
  answer (omission, terse substitution, curt refusal) are mixed with ones that
  lengthen it (overrun, preamble, drift to prose); `balance_by_length` then matches
  the two classes bucket-by-bucket on response length.
- **Coverage of all five eval failure families**, plus multi-turn conversations for
  context-drift and scope-contradiction.
- **Refusal-shaped positives** (`DECLINE_REQUESTS`): requests whose *correct* answer
  is itself a polite refusal, so the probe cannot collapse into a refusal detector.

Effect on the confound: v1 positives average **123** chars vs negatives **128**
(seed: 92 vs 184).
