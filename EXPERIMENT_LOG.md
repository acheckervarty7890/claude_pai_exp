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

### Iterating on the generator

Three problems surfaced while building the data, each fixed in turn:

**1. Length balancing was deleting failure modes.** Applied globally, it removed
*every* `lf_standing` context-drift negative — drift is intrinsically longer than
compliance, so no length bucket contained both classes. Fix: each long-form family
now emits a **terse-target** and a **verbose-target** flavour (e.g. "answer in 3
bullets" vs "answer in 3 numbered points with supporting detail"), so compliance is
not always the shorter class, and balancing is stratified per family.

**2. Uniform sampling inside a bucket wiped out modes.** `refusal` vanished from
`lf_chat` entirely, despite `anthropic_harmless_refusal` being an eval split.
Fix: negative selection is round-robin across modes.

**3. Sequence-length mismatch.** v1 rows had a median of 83 gemma tokens against
dev/eval sequence lengths of 159-436. Since `linear_then_softmax` pools over token
positions, that is a different regime from the one being scored. `synth/longform.py`
adds multi-paragraph documents, multi-part instructions and standing constraints
carried across 8 turns — the only shape in which *context drift* can exist at all.

| dataset | p10 | p50 | p90 | max |
|---|---|---|---|---|
| seed | 34 | 67 | 92 | 135 |
| v1 | 51 | 83 | 126 | 167 |
| v2+ | 74 | 164 | 272 | 341 |

### Context-flip pairs

The remaining loophole: every family above holds the prompt fixed and varies the
response, so a probe can still succeed on **response-only** features ("is a bulleted
list", "is a refusal") that need not transfer to real conversations.

`synth/flip.py` closes it from the other side — one **byte-identical** assistant turn
paired with two instructions, one it satisfies and one it violates. Response-only
features then carry exactly zero information. The sharpest case is the refusal flip:
the same polite decline is compliant when a decline was requested and non-compliant
when help was requested, which is precisely the `anthropic_harmless_refusal`
distinction.

`synth/registers.py` additionally adds email, code, tabular and creative-writing
tasks, since `banks.TOPICS` is otherwise all expository prose.

Confound status of the final generator:

| metric | seed | synthetic |
|---|---|---|
| response-length / label correlation | **+0.395** | **+0.014** |
| prompt-length / label correlation | — | **-0.006** |
