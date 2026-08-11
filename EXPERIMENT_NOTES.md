# harmful_to_human probe: synthetic-data iteration log

Model `google/gemma-3-27b-it`, layer 32, probe type `linear_then_softmax` (baked in).
Memory pinned to `cuda:0=22GiB,cpu=45GiB`; eval activations for all four held-out splits
were fetched precomputed from Kaggle, so evaluation never re-runs the 27B extraction.

Training data was grown only by generating synthetic conversations (`synth/gen_v*.py`,
each script documents the hypothesis it tests). Eval splits are anonymised as a-d and
were never inspected; the only signal used to steer iteration was the per-split AUROC
that `evaluation.py` reports.

## Results (mean AUROC over the four held-out splits)

See `summarize.py` for the live table. Headline: **0.530 -> 0.912**.

## What each iteration taught

1. **Baseline (50 seed rows) = 0.530.** Essentially chance; the seed is far too small for
   a 5376-dim linear probe.
2. **Batch 1 (topic-matched pairs, refusal 2x2) -> 0.851.** The single biggest jump. Same
   user turn, one harmful and one safe assistant reply, so topic cannot carry the label.
3. **Batch 2 (tone decorrelated from harm, harm-by-omission, agentic and dilemma
   framings) -> 0.883.** Confirms the probe was partly keying on register: adding harmful
   advice in a warm professional voice, and safe advice delivered bluntly, helped.
4. **Batch 3 (lone user turns and third-person scenarios) -> 0.878, and -0.04 when added
   to a stronger mixture.** Consistently raised the hardest split and consistently wrecked
   the easiest one. Tested three times (v3, v4b, v10) and dropped every time: the probe
   does not tolerate samples with no assistant turn.
5. **Batch 4 (compliance with harmful requests, verbal/emotional harm, late-turn harm in
   long casual chats) -> 0.892.** Fixed a real asymmetry: until then every dangerous
   request in the data was answered with a refusal, so "dangerous request" predicted the
   negative class.
6. **Batch 5 (more matched pairs, new domains) -> 0.891, flat.** The matched-pair shape
   had saturated; more of it buys nothing.
7. **Batch 6 (refusal 2x2 at volume, pushback threads) -> 0.880, slightly negative.**
8. **Batch 7 (harmful vs benign request, both answered with the same content-free
   acknowledgement) -> 0.898.** Separated "harm in the request" from batch 3's odd shape,
   and the label semantics were the useful half.
9. **Batch 8 (3x more of batch 7) -> 0.882.** Dose matters: at ~28% of the data this
   shifts the probe toward request-only harm and costs the response-driven splits.
10. **v9 = drop the original seed, keep a ~7% dose of request-style rows -> 0.912.** Best.
11. **v10 (v9 plus a small dose of the batch-3 shapes) -> 0.889.** Confirms 4 again.

## Recipe that won

`synth/train_v9.jsonl` (459 rows, 206 harmful / 253 not):
batches 1, 2, 4, 5-pairs at full weight, batch 7 plus 30 rows of batch 9 as a minority
request-harm component, and none of the original 50-row seed or the lone-turn shapes.

Run-to-run noise, measured by retraining one mixture under a second seed, is about
+/-0.003 mean AUROC, so differences below ~0.006 are not meaningful.

## Reproducing

```bash
source run_env.sh
./run_iter.sh v9 synth/train_v9.jsonl   # train + evaluate, writes results/v9.csv
.venv/bin/python summarize.py
```

`run_env.sh` sets the memory pinning and a `sitecustomize` shim (`hfpatch/`) that
no-ops `huggingface_hub.login`. That shim exists because the box's `HF_TOKEN` expired
partway through the session; the gemma weights were already fully cached, but
`tuberlens.utils.hf_login` calls `login()` unconditionally and an expired token makes
model loading fail. With a valid token, drop `HF_LOGIN_NOOP`/`HF_HUB_OFFLINE` and
everything works unchanged.
