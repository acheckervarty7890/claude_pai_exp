"""Print the per-split eval CSVs side by side, newest run last.

Split stems are hashed in the repo; the mapping to the four eval families comes
from the fetch manifest's split names (row counts match), so the table is
readable without touching the held-out files themselves.
"""
import sys
import pandas as pd

FAMILY = {
    "33cf450b4eea": "anthropic_hh",
    "706fcbc9e21c": "multi_turn",
    "c5c436ad8e80": "clinical",
    "e1a1ee570ae0": "toolace",
    "mean": "MEAN",
}

frames = {}
for path in sys.argv[1:]:
    df = pd.read_csv(path).set_index(df_col := pd.read_csv(path).columns[0])
    frames[path.split("/")[-1].replace("results_", "").replace(".csv", "")] = df["auroc"]

out = pd.DataFrame(frames)
out.index = [FAMILY.get(i, i) for i in out.index]
print("AUROC by eval family")
print(out.round(4).to_string())
