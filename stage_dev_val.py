"""Stage the concept's dev activations as ONE validation blob for train.py.

train.py's own `stage_validation_activations` refuses to concatenate dev splits whose
blobs have different sequence lengths (they are padded per-split). The hu_ha dev
splits do differ (121/135/257/285), so this script right-pads every split to the
longest and writes the merged blob to the path train_probe reads
(`with_stem("val-<stem>")` of --activations_save_path). train.py sees the file
already staged and reuses it.

Padding is safe here: the fetched blobs are right-padded (verified — every row's
attention_mask is a prefix of ones), so appending zero rows with attention_mask=0
adds only masked-out positions.

Row order MUST match how train.py builds the validation dataset: the *.jsonl files in
--validation_data sorted by name, each blob matched by its cache key
(sha256(split)[:12]).
"""

import argparse
from pathlib import Path

import torch

from evaluation import (
    ACTIVATION_FIELDS,
    DEFAULT_CACHE_STEM,
    build_blob_index,
    read_activation_blob,
    validate_activation_blob,
)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--validation_data", type=Path, required=True,
                    help="Directory of dev *.jsonl label files (order = sorted names)")
    ap.add_argument("--validation_activations_dir", type=Path, required=True)
    ap.add_argument("--activations_save_path", type=str, required=True,
                    help="Same value passed to train.py; the blob goes to its val- sibling")
    ap.add_argument("--model", type=str, default="google/gemma-3-27b-it")
    ap.add_argument("--layer", type=int, default=32)
    ap.add_argument("--cache_stem", type=str, default=DEFAULT_CACHE_STEM)
    ap.add_argument("--force", action="store_true", help="Overwrite an existing staged blob")
    args = ap.parse_args()

    p = Path(args.activations_save_path)
    target = p.with_stem(f"val-{p.stem}")
    if target.exists() and not args.force:
        print(f"[stage] {target} already exists; pass --force to rebuild")
        return

    names = [f.stem for f in sorted(args.validation_data.glob("*.jsonl"))]
    if not names:
        raise FileNotFoundError(f"No .jsonl files in {args.validation_data}")
    index = build_blob_index(args.validation_activations_dir, args.cache_stem)

    blobs = []
    for name in names:
        path = index.get(name)
        if path is None:
            raise FileNotFoundError(
                f"{name}: no cached activations in {args.validation_activations_dir}"
            )
        blob = read_activation_blob(path)
        rows = int(blob["activations"].shape[0])
        validate_activation_blob(blob, path, name=name, model_name=args.model,
                                 layer=args.layer, n_rows=rows)
        # Right-padding is what makes zero-padding below correct; refuse if it is not.
        mask = blob["attention_mask"]
        if not torch.equal(mask, (torch.arange(mask.shape[1])[None, :] < mask.sum(1)[:, None]).to(mask.dtype)):
            raise ValueError(f"{name}: {path} is not right-padded; cannot pad to a common length")
        blobs.append((name, path, blob))

    t_max = max(int(b["activations"].shape[1]) for _, _, b in blobs)
    print(f"[stage] padding {len(blobs)} split(s) to sequence length {t_max}")

    merged = {}
    for field in ACTIVATION_FIELDS:
        parts = []
        for name, _, blob in blobs:
            t = blob[field]
            pad = t_max - t.shape[1]
            if pad:
                shape = (t.shape[0], pad) + tuple(t.shape[2:])
                t = torch.cat([t, torch.zeros(shape, dtype=t.dtype)], dim=1)
            parts.append(t)
        merged[field] = torch.cat(parts, dim=0)
    merged["model_name"] = args.model
    merged["layer"] = args.layer

    target.parent.mkdir(parents=True, exist_ok=True)
    torch.save(merged, target)
    rows = ", ".join(f"{n} ({int(b['activations'].shape[0])})" for n, _, b in blobs)
    print(f"[stage] wrote {merged['activations'].shape[0]} validation rows to {target}")
    print(f"[stage] order: {rows}")


if __name__ == "__main__":
    main()
