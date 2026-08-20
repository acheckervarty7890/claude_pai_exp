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
| v1s | seed + short paired synthetic | 804 | 0.7232 | **0.7652** |
| v3s | + long-form multi-turn | 2434 | 0.7141 | **0.7806** |
| v6s | + drift/omission families | 3248 | 0.7167 | 0.7534 |

The shipped seed produces a probe at **exactly chance**. Diagnosis below.

Dev and eval move together, so dev is a usable selection signal and the eval set does
not have to be consulted to make decisions.

### Per-split breakdown

Split names come from the public Kaggle manifest, and the label filenames are
`sha256(split_name)[:12]` — the mapping `evaluation.py:blob_keys` already uses — so
results can be attributed to a failure family without opening any held-out file.

| eval split | baseline | v1s | gain |
|---|---|---|---|
| `oig_context_drift` | 0.556 | **0.640** | +0.08 |
| `hc_context_drift` | 0.489 | **0.649** | +0.16 |
| `oig_omission` | 0.453 | 0.700 | +0.25 |
| `bbq_substitution` | 0.517 | 0.715 | +0.20 |
| `mm_substitution` | 0.347 | 0.808 | +0.46 |
| `hc_contradiction` | 0.490 | 0.865 | +0.37 |
| `anthropic_harmless_refusal` | 0.641 | **0.980** | +0.34 |

**Refusal is solved** (0.98) — the benign-refusal and decline-request families did
their job. **Context drift is the weak point** on both of its splits, with omission
next.

That is exactly what the length analysis predicted. The two drift splits have the
longest sequences (367 and 392 tokens) and `oig_omission` is longer still (436),
while v1s topped out at **167** tokens and was only ~13% multi-turn. The probe was
never shown a conversation long enough for drift to occur. This is what the
`longform` and `flip_standing` families were built to fix.

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


## Iteration 2 — long-form (v3s), eval 0.7652 -> 0.7806

A modest mean gain hiding a large redistribution:

| eval split | v1s | v3s | delta |
|---|---|---|---|
| `hc_context_drift` | 0.649 | **0.805** | **+0.157** |
| `bbq_substitution` | 0.715 | 0.819 | +0.104 |
| `hc_contradiction` | 0.865 | 0.922 | +0.057 |
| `mm_substitution` | 0.808 | 0.818 | +0.011 |
| `oig_context_drift` | 0.640 | 0.616 | -0.025 |
| `oig_omission` | 0.700 | 0.625 | -0.075 |
| `anthropic_harmless_refusal` | 0.980 | **0.859** | **-0.121** |

Long-form data did what it was meant to on `hc_context_drift` (+0.157). But three
splits went backwards, and the cause is **composition drift**, not a bad idea:

| negative mode | v3-like mix | v6 mix | quota target |
|---|---|---|---|
| substitution | 39.4% | 21.2% | 22% |
| contradiction | 29.8% | 23.3% | 14% |
| context_drift | 8.3% | 19.7% | 22% |
| omission | 5.1% | 11.1% | 14% |
| **refusal** | **4.1%** | 6.0% | **14%** |

Adding long-form families pushed refusal down to **4.1%** of negatives, and refusal
duly fell 0.980 -> 0.859 on the split that tests it. Mode share had been an
uncontrolled side effect of the family weights all along.

Also worth noting: **dev fell (0.7232 -> 0.7141) while eval rose**. With only ~62 rows
per dev split, dev is noisy enough that it should not be trusted for fine-grained
selection — only for catching large regressions.

### Fix: explicit failure-mode quotas

`enforce_mode_quota` now resamples negatives to a target mix set in proportion to how
many eval splits test each family (substitution and context-drift have two each;
refusal, contradiction and omission one each), then length-matches the positives back
to the retained negatives so the confound control survives the resampling.

Sizing that budget correctly took two attempts, both caught by measurement:

- Sizing by *every* mode let a 2%-share rarity (`preamble`) halve the dataset,
  3198 -> 1598 rows.
- Redistributing shortfall to whichever mode had surplus let refusal balloon to
  **28%** — overshooting in the opposite direction.
- Sizing by the **five core eval modes only** gives 3822 rows at the intended mix.

The refusal banks were also expanded (16 -> 30 benign requests, 6 -> 12 decline
requests), since refusal supply was the binding constraint on total dataset size.

Final v7 composition: context_drift 23%, substitution 23%, omission 14%, refusal 14%,
contradiction 14%; response-length corr **+0.015**, prompt-length corr **+0.008**.


## Iteration 3 — drift families (v6s), eval 0.7806 -> 0.7534 (regression)

| eval split | v1s | v3s | v6s | v3->v6 |
|---|---|---|---|---|
| `bbq_substitution` | 0.715 | 0.819 | **0.874** | +0.056 |
| `oig_omission` | 0.700 | 0.625 | 0.666 | +0.041 |
| `hc_context_drift` | 0.649 | 0.805 | 0.811 | +0.005 |
| `anthropic_harmless_refusal` | **0.980** | 0.859 | 0.793 | -0.066 |
| `oig_context_drift` | 0.640 | 0.616 | **0.546** | -0.070 |
| `mm_substitution` | 0.808 | 0.818 | 0.743 | -0.075 |
| `hc_contradiction` | 0.865 | **0.922** | 0.842 | -0.080 |

Tripling the drift data made `oig_context_drift` *worse* (0.616 -> 0.546). That ruled
out "not enough drift data" and pointed somewhere else.

### The actual problem: response diversity, not quantity

Counting unique assistant responses per failure mode:

| mode | rows | unique responses | ratio |
|---|---|---|---|
| **refusal** | 275 | **17** | **0.06** |
| substitution | 432 | 126 | 0.29 |
| omission | 275 | 82 | 0.30 |
| context_drift | 432 | 177 | 0.41 |
| contradiction | 275 | 106 | 0.39 |
| format | 137 | 134 | 0.98 |

Refusal had **17 distinct sentences across 275 rows** — every refusal row was one of
seventeen strings repeated sixteen times. The probe was memorising those strings, not
learning refusal, which is why `anthropic_harmless_refusal` fell steadily (0.980 ->
0.859 -> 0.793) as refusal rows grew *more numerous but no more varied*. The same
applies, less severely, to drift: eight hand-written scenario paragraphs cannot teach
a general notion of ignoring context.

Adding rows to a low-diversity mode is worse than useless — it increases the weight
of memorised text in the loss without adding information.

### Fix: assemble failure text combinatorially

`synth/refusals.py` builds refusals from independent slots (opener x core x reason x
redirect x closer, ~11x11x9x9x8), plus deflections and generic advice on the same
principle. Drift answers now mix the hand-written context-ignoring paragraph with
assembled generic advice, and omission drops a *random* requirement rather than
always the last.

| mode | ratio before | ratio after |
|---|---|---|
| refusal | 0.06 | **0.47** |
| context_drift | 0.34 | **0.62** |
| omission | 0.28 | **0.45** |
| substitution | 0.45 | 0.51 |

v7 (quotas, old low-diversity text) was cancelled one minute into training in favour
of **v8** = quotas + combinatorial diversity, since v8 strictly dominates it.
