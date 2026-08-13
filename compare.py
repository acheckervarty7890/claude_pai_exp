"""Print per-dataset and mean AUROC for every results CSV, side by side."""

import sys
from pathlib import Path

import pandas as pd

results = sorted(Path("results").glob("eval_*.csv"), key=lambda p: p.stat().st_mtime)
if not results:
    sys.exit("no results yet")

frames = {}
metric = None
for path in results:
    df = pd.read_csv(path)
    if metric is None:
        cands = [c for c in df.columns if "auroc" in c.lower()]
        metric = cands[0] if cands else df.columns[-1]
    name_col = "dataset" if "dataset" in df.columns else df.columns[0]
    s = df.set_index(name_col)[metric]
    # tuberlens already appends its own "mean" row; drop it so the summary
    # below is a mean over datasets rather than over datasets plus their mean.
    frames[path.stem.replace("eval_", "")] = s.drop(index="mean", errors="ignore")

table = pd.DataFrame(frames)
table.loc["** MEAN **"] = table.mean()
print(f"metric: {metric}\n")
print(table.round(4).to_string())

if table.shape[1] > 1:
    base, last = table.columns[0], table.columns[-1]
    delta = table[last] - table[base]
    print(f"\ndelta ({last} - {base}):")
    print(delta.round(4).to_string())
