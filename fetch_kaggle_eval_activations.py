#!/usr/bin/env python
"""Download precomputed eval activations from Kaggle into a local activation cache.

STANDALONE: this file imports nothing from this repo, so it can be copied to a bare box
on its own. Its only third-party requirements are ``kaggle`` (the download) and ``torch``
(reading a blob's header to validate it).

Each blob is written to ``<cache-dir>/<split>-acts_full.pt`` — the exact path tuberlens'
``get_performances`` derives via ``Path(save_path).with_stem(f"{name}-{stem}")`` — so a
later eval finds it in ``get_activations``' local-first branch and never loads the 27B
extraction model. That is the whole point: these are full-split gemma-3-27b activations,
tens of GB and hours of forward passes to recompute.

WHAT THIS FILE DOES NOT CONTAIN
-------------------------------
It carries **no split inventory**: no split names, no row counts, no per-concept dataset
slugs. All of that lives in a small manifest published alongside the blobs, fetched at
run time. Reading this file tells you the concept names and nothing about how any eval
set is cut. Add a concept, rename a split or re-cut a split's row count and this file
does not change — republish the manifest instead
(``scripts/publish_eval_manifest.py`` in the source repo).

So the whole interface is the concept name::

    python fetch_kaggle_eval_activations.py --list
    python fetch_kaggle_eval_activations.py --concept instructions_eval --dry-run
    python fetch_kaggle_eval_activations.py --concept instructions_eval
    python fetch_kaggle_eval_activations.py --concept instructions_dev

Concepts come in ``_eval`` and ``_dev`` pairs: separate Kaggle datasets, separate row
counts. The manifest may also define aliases for older names, which are accepted and
reported.

**Do not point an eval and a dev concept at the same ``--cache-dir``.** Some concepts
reuse the same split stems for both, and a cache is keyed by stem alone, so they would
overwrite each other. The default (``eval_activations_<concept>``) keeps them apart, and
the row/seq_len validation below fails loudly if they are ever mixed.

``--cache-dir`` defaults to ``./eval_activations_<concept>``; point it at the run's
``output.activations_cache_dir`` to prefill that directly. Everything else — Kaggle
handles, file names, extraction model, layer, expected shapes — is resolved from the
manifest.

VALIDATION
----------
Every blob, freshly downloaded *or* already sitting in the cache, is checked against the
manifest's ``model_name``/``layer`` and against the split's expected ``(rows, seq_len)``
before it may be used. ``LLMModel.load_activations`` discards the model/layer a blob was
saved with, and these caches otherwise load *by path without checking their inputs*:
fine for a content-keyed blob you computed yourself, not for one fetched from a remote
store. A split that cannot be fetched raises rather than falling back to computing it.

``seq_len`` is validated, not just the row count, because a row count is not always a
unique fingerprint within a concept — the instruction-following splits include four with
200 rows and two with 194, so a rows-only check cannot tell a swapped blob from the right
one. Sequence length separates all of them. It is enforced only where the manifest
supplies it, so an older manifest still works.

Auth: ``KAGGLE_CONFIG_DIR`` must name the DIRECTORY holding kaggle.json (the API joins
the filename on itself, and ``os.makedirs`` a wrong path, so pointing it at the file
fails silently), or export ``KAGGLE_API_TOKEN``.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

# The manifest is the only address baked into this file. Everything about the eval
# splits themselves is resolved from it at run time.
MANIFEST_OWNER = "anku7890"
MANIFEST_SLUG = "probe-eval-activations-manifest"
MANIFEST_FILE = "eval_activations_manifest.json"

DEFAULT_CACHE_STEM = "acts_full.pt"


class KaggleActivationError(RuntimeError):
    """A Kaggle activation blob could not be fetched, or failed validation."""


def _slugify(split: str) -> str:
    """Return ``split`` in the character set Kaggle allows in a dataset slug.

    Kaggle slugs are lowercase alphanumerics and hyphens — an underscore is rejected at
    creation time, so a split whose stem contains one has no dataset naming it verbatim.
    Runs of anything else collapse to a single hyphen; leading/trailing hyphens drop.
    """
    out: list[str] = []
    for ch in split.lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-")


@dataclass(frozen=True)
class KaggleActivationSource:
    """Where a split's precomputed activations live on Kaggle.

    ``dataset_slug`` and ``file_name`` are templates formatted with two keys: ``split``
    (the stem exactly as it appears on disk) and ``slug`` (that stem through
    :func:`_slugify`). A literal string with no placeholder is fine when every split maps
    to the same object.
    """

    owner: str
    dataset_slug: str
    file_name: str

    def handle(self, split: str) -> str:
        return f"{self.owner}/{self.dataset_slug.format(split=split, slug=_slugify(split))}"

    def file_for(self, split: str) -> str:
        return self.file_name.format(split=split, slug=_slugify(split))


@dataclass(frozen=True)
class ConceptSpec:
    """One concept's entry, as resolved from the manifest."""

    name: str
    description: str
    source: KaggleActivationSource
    model_name: str
    layer: int
    cache_stem: str
    splits: dict[str, dict]          # stem -> {"rows": int, "seq_len": int | None}
    input_ids_scrubbed: bool
    notes: str

    def rows(self, split: str) -> int:
        return int(self.splits[split]["rows"])

    def seq_len(self, split: str) -> int | None:
        v = self.splits[split].get("seq_len")
        return None if v is None else int(v)


def _authenticate():
    """Return an authenticated ``KaggleApi``.

    ``KaggleApi.authenticate()`` ends in ``print_auth_help(); exit(1)`` when no credential
    source resolves, and its anonymous fallback is disabled whenever the library is
    imported rather than run as the ``kaggle`` CLI. ``SystemExit`` is a ``BaseException``,
    so an ordinary ``except Exception`` would let it escape and kill the process — convert
    it into our own error instead.
    """
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError as e:  # pragma: no cover - depends on the environment
        raise KaggleActivationError(
            "The 'kaggle' package is not installed in this environment. "
            "Install it with: pip install kaggle"
        ) from e

    api = KaggleApi()
    try:
        api.authenticate()
    except SystemExit as e:
        raise KaggleActivationError(
            "Kaggle authentication failed. Set KAGGLE_CONFIG_DIR to the DIRECTORY holding "
            "kaggle.json (not the file itself), or export KAGGLE_API_TOKEN with a token "
            "from https://www.kaggle.com/settings/api."
        ) from e
    return api


def _download_one(api, handle: str, remote_name: str, staging: Path, *, what: str, quiet: bool) -> Path:
    """Fetch ``handle:remote_name`` into ``staging`` and return the single file that lands.

    ``dataset_download_file`` names its output from the download URL rather than from the
    requested file name, and Kaggle may serve a large file zipped — so what actually
    arrives has to be discovered rather than assumed.
    """
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)
    try:
        api.dataset_download_file(handle, remote_name, path=str(staging), quiet=quiet)
    except Exception as e:
        raise KaggleActivationError(f"{what}: download of {handle}:{remote_name} failed: {e}") from e

    for archive in sorted(staging.glob("*.zip")):
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(staging)
        archive.unlink()

    landed = sorted(p for p in staging.rglob("*") if p.is_file())
    if not landed:
        raise KaggleActivationError(f"{what}: the download produced no file.")
    if len(landed) > 1:
        raise KaggleActivationError(
            f"{what}: expected one file in the download, got {[p.name for p in landed]}."
        )
    return landed[0]


def load_manifest(api=None, *, owner: str = MANIFEST_OWNER, slug: str = MANIFEST_SLUG,
                  file_name: str = MANIFEST_FILE, local: Path | None = None,
                  cache_dir: Path | None = None, verbose: bool = True) -> dict:
    """Return the parsed manifest, from ``local`` if given, else from Kaggle.

    ``local`` exists so the source repo (which holds the manifest anyway) and an offline
    box can both drive this script without a round trip.
    """
    if local is not None:
        try:
            return json.loads(Path(local).read_text())
        except Exception as e:
            raise KaggleActivationError(f"could not read manifest {local}: {e}") from e

    if api is None:
        api = _authenticate()
    staging = (cache_dir or Path(".")) / ".staging-manifest"
    handle = f"{owner}/{slug}"
    try:
        if verbose:
            print(f"[kaggle] fetching manifest {handle}:{file_name} ...")
        blob = _download_one(api, handle, file_name, staging, what="manifest", quiet=True)
        try:
            return json.loads(blob.read_text())
        except Exception as e:
            raise KaggleActivationError(f"manifest {handle}:{file_name} is not valid JSON: {e}") from e
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def concept_from_manifest(manifest: dict, concept: str) -> ConceptSpec:
    """Resolve one concept out of a parsed manifest, or raise with the valid names.

    An ``aliases`` map lets an older concept name keep working after the inventory is
    reorganised — resolved once, not chased transitively, so a cyclic alias can't hang.
    """
    concepts = manifest.get("concepts") or {}
    resolved = concept
    if resolved not in concepts:
        alias_target = (manifest.get("aliases") or {}).get(concept)
        if alias_target in concepts:
            print(f"[manifest] concept {concept!r} is an alias for {alias_target!r}")
            resolved = alias_target
    if resolved not in concepts:
        raise KaggleActivationError(
            f"unknown concept {concept!r}. The manifest offers: "
            f"{', '.join(sorted(concepts)) or '(none)'}"
        )
    concept = resolved
    c = concepts[concept]
    owner = c.get("owner") or manifest.get("owner")
    if not owner:
        raise KaggleActivationError(f"{concept}: the manifest sets no owner.")

    splits_raw = c.get("splits") or {}
    if not splits_raw:
        raise KaggleActivationError(f"{concept}: the manifest lists no splits.")
    # Accept both {stem: rows} and {stem: {"rows": .., "seq_len": ..}} so an older,
    # flat manifest still resolves.
    splits: dict[str, dict] = {}
    for stem, spec in splits_raw.items():
        splits[stem] = {"rows": spec, "seq_len": None} if isinstance(spec, int) else dict(spec)

    missing = [k for k in ("dataset_slug", "file_name", "model_name", "layer") if c.get(k) is None]
    if missing:
        raise KaggleActivationError(f"{concept}: the manifest entry is missing {', '.join(missing)}.")

    return ConceptSpec(
        name=concept,
        description=str(c.get("description") or ""),
        source=KaggleActivationSource(str(owner), str(c["dataset_slug"]), str(c["file_name"])),
        model_name=str(c["model_name"]),
        layer=int(c["layer"]),
        cache_stem=str(c.get("cache_stem") or DEFAULT_CACHE_STEM),
        splits=splits,
        input_ids_scrubbed=bool(c.get("input_ids_scrubbed", False)),
        notes=str(c.get("notes") or ""),
    )


def _blob_header(path: Path) -> dict:
    """Read a saved activation blob's metadata without paging its tensors into RAM.

    ``mmap=True`` maps the tensor storages instead of reading them, so this is ~instant
    even for an 11 GB blob; only shapes and the small scalar fields are touched.
    """
    try:
        import torch
    except ImportError as e:  # pragma: no cover - depends on the environment
        raise KaggleActivationError(
            "The 'torch' package is not installed in this environment, so downloaded "
            "blobs cannot be validated. Install it with: pip install torch"
        ) from e

    return torch.load(path, map_location="cpu", mmap=True)


def _validate_blob(path: Path, *, split: str, model_name: str, layer: int,
                   n_rows: int, seq_len: int | None = None) -> None:
    """Raise unless the blob at ``path`` matches the probe and split it is claimed for."""
    try:
        data = _blob_header(path)
    except KaggleActivationError:
        raise
    except Exception as e:
        raise KaggleActivationError(f"{split}: could not read {path}: {e}") from e

    missing = {"activations", "attention_mask", "input_ids"} - set(data)
    if missing:
        raise KaggleActivationError(
            f"{split}: {path} is missing tensor field(s) {sorted(missing)} — "
            "it does not look like a tuberlens activation blob."
        )

    problems = []
    got_model = data.get("model_name")
    if got_model is not None and got_model != model_name:
        problems.append(f"model_name={got_model!r} (expected {model_name!r})")
    got_layer = data.get("layer")
    if got_layer is not None and int(got_layer) != int(layer):
        problems.append(f"layer={got_layer} (expected {layer})")
    shape = tuple(data["activations"].shape)
    if int(shape[0]) != int(n_rows):
        problems.append(f"{shape[0]} rows (split has {n_rows})")
    # seq_len is what distinguishes splits whose row counts collide within a concept.
    if seq_len is not None and len(shape) > 1 and int(shape[1]) != int(seq_len):
        problems.append(f"seq_len={shape[1]} (expected {seq_len})")
    if problems:
        raise KaggleActivationError(
            f"{split}: activations at {path} do not match this run — "
            + "; ".join(problems)
            + ". Refusing to use them."
        )


def prefetch_eval_activations(activations_cache_dir: str | Path, concept: ConceptSpec, *,
                              splits: list[str] | None = None, api=None,
                              verbose: bool = True) -> dict[str, str]:
    """Populate the eval activation cache from Kaggle, one file per split.

    Splits already present locally are validated and left alone; nothing is
    re-downloaded. Returns a ``{split: status}`` map where status is ``cached`` (already
    local) or ``downloaded``.
    """
    cache_dir = Path(activations_cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(concept.cache_stem).stem
    suffix = Path(concept.cache_stem).suffix or ".pt"

    wanted = splits or list(concept.splits)
    unknown = [s for s in wanted if s not in concept.splits]
    if unknown:
        raise KaggleActivationError(
            f"{concept.name}: the manifest has no split(s) {', '.join(unknown)}. "
            f"It offers: {', '.join(concept.splits)}"
        )

    targets = {s: cache_dir / f"{s}-{stem}{suffix}" for s in wanted}
    pending = [s for s, t in targets.items() if not t.exists()]

    statuses: dict[str, str] = {}
    for split in wanted:
        target = targets[split]
        rows, seq = concept.rows(split), concept.seq_len(split)
        if target.exists():
            _validate_blob(target, split=split, model_name=concept.model_name,
                           layer=concept.layer, n_rows=rows, seq_len=seq)
            statuses[split] = "cached"
            if verbose:
                print(f"[kaggle] {split}: already cached at {target}")
            continue

        if api is None:  # authenticate lazily — a full local cache needs no network
            api = _authenticate()
            if verbose:
                print(
                    f"[kaggle] authenticated as {api.get_config_value('username')}; "
                    f"fetching {len(pending)} split(s): {', '.join(pending)}"
                )

        handle, remote_name = concept.source.handle(split), concept.source.file_for(split)
        staging = cache_dir / f".staging-{split}"
        try:
            if verbose:
                print(f"[kaggle] {split}: downloading {handle}:{remote_name} ...")
            blob = _download_one(api, handle, remote_name, staging, what=split, quiet=not verbose)
            _validate_blob(blob, split=split, model_name=concept.model_name,
                           layer=concept.layer, n_rows=rows, seq_len=seq)
            # Same filesystem as the cache, so this is a rename, not a 2nd copy.
            blob.replace(target)
            statuses[split] = "downloaded"
            if verbose:
                print(f"[kaggle] {split}: {target.name} "
                      f"({target.stat().st_size / 1e9:.2f} GB) validated and cached")
        finally:
            shutil.rmtree(staging, ignore_errors=True)

    return statuses


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--concept", help="Which probe concept's eval splits to fetch "
                                      "(names come from the manifest; see --list)")
    ap.add_argument("--list", action="store_true",
                    help="List the concepts the manifest offers, and exit")
    ap.add_argument("--cache-dir", type=Path, default=None,
                    help="Activation cache to fill (default: ./eval_activations_<concept>). "
                         "Point this at the run's output.activations_cache_dir to prefill it.")
    ap.add_argument("--splits", nargs="*", default=None,
                    help="Split stems to fetch (default: all of the concept's splits)")
    ap.add_argument("--manifest", type=Path, default=None,
                    help="Read the manifest from this local JSON instead of Kaggle")
    ap.add_argument("--manifest-owner", default=MANIFEST_OWNER)
    ap.add_argument("--manifest-slug", default=MANIFEST_SLUG)
    ap.add_argument("--manifest-file", default=MANIFEST_FILE)
    ap.add_argument("--dry-run", action="store_true",
                    help="Print the plan (handles, targets, what is already there); download nothing")
    args = ap.parse_args(argv)

    if not args.list and not args.concept:
        ap.error("one of --concept or --list is required")

    try:
        manifest = load_manifest(local=args.manifest, owner=args.manifest_owner,
                                 slug=args.manifest_slug, file_name=args.manifest_file,
                                 cache_dir=args.cache_dir)
    except KaggleActivationError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if args.list:
        print("concepts in the manifest:\n")
        items = sorted((manifest.get("concepts") or {}).items(),
                       key=lambda kv: (kv[1].get("concept") or kv[0], kv[1].get("kind") or ""))
        for name, c in items:
            splits = c.get("splits") or {}
            n_rows = sum((s if isinstance(s, int) else s.get("rows", 0)) for s in splits.values())
            print(f"  {name:<22} {len(splits)} split(s) / {n_rows:>5} rows  "
                  f"{c.get('model_name')} layer {c.get('layer')}")
            if c.get("description"):
                print(f"  {'':<22} {c['description']}")
        aliases = manifest.get("aliases") or {}
        if aliases:
            print("\naliases: " + ", ".join(f"{a} -> {t}" for a, t in sorted(aliases.items())))
        return 0

    try:
        concept = concept_from_manifest(manifest, args.concept)
    except KaggleActivationError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    # Keyed on the RESOLVED name, not what was typed: an alias and its target must share
    # one cache dir or the same blobs get downloaded twice under two names.
    cache_dir = (args.cache_dir or Path(f"eval_activations_{concept.name}")).resolve()
    stem = Path(concept.cache_stem).stem
    suffix = Path(concept.cache_stem).suffix or ".pt"
    wanted = args.splits or list(concept.splits)

    print(f"concept   {concept.name}  {concept.description}")
    print(f"cache     {cache_dir}")
    print(f"probe     {concept.model_name} layer {concept.layer}")
    if not concept.input_ids_scrubbed:
        print("WARNING   these blobs still carry real input_ids — the eval text is "
              "recoverable by decoding them")
    if concept.notes:
        print(f"note      {concept.notes}")
    print()
    for split in wanted:
        if split not in concept.splits:
            print(f"  {split:<28} NOT IN MANIFEST")
            continue
        target = cache_dir / f"{split}-{stem}{suffix}"
        seq = concept.seq_len(split)
        shape = f"{concept.rows(split)} x {seq if seq is not None else '?'}"
        print(f"  {split:<28} {shape:>12}  {'present' if target.exists() else 'MISSING'}")
        print(f"  {'':<28} kaggle.com/datasets/{concept.source.handle(split)}"
              f"  ({concept.source.file_for(split)})")
        print(f"  {'':<28} -> {target}")
    print()

    if args.dry_run:
        print("--dry-run: nothing downloaded. Blobs already present were NOT validated; "
              "re-run without --dry-run to validate them and fetch the rest.")
        return 0

    try:
        statuses = prefetch_eval_activations(cache_dir, concept, splits=args.splits)
    except KaggleActivationError as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        return 1

    print()
    for split, state in sorted(statuses.items()):
        print(f"  {split:<28} {state}")
    total_gb = sum((cache_dir / f"{s}-{stem}{suffix}").stat().st_size for s in statuses) / 1e9
    print(f"\n{len(statuses)} split(s) ready in {cache_dir} ({total_gb:.2f} GB).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
