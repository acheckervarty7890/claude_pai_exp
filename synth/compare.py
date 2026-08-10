#!/usr/bin/env python
"""Print a side-by-side table of every evaluation CSV in results/."""

import sys
from pathlib import Path

import pandas as pd

results_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "results")
frames = {}
for csv in sorted(results_dir.glob("*.csv")):
    df = pd.read_csv(csv).set_index("dataset")
    frames[csv.stem.replace("_eval", "")] = df["auroc"]

table = pd.DataFrame(frames)
base = table.columns[0]
print(table.round(4).to_string())
print()
for col in table.columns[1:]:
    delta = table.loc["mean", col] - table.loc["mean", base]
    print(f"{col}: mean AUROC {table.loc['mean', col]:.4f}  ({delta:+.4f} vs {base})")
