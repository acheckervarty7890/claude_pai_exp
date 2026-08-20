"""Print AUROC per eval family across runs, oldest first.

Split stems are hashed in the repo. The mapping to the four eval families comes
from the fetch manifest's split names, whose row counts match the label files, so
the table reads sensibly without touching the held-out data.
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


def label(path):
    return path.split("/")[-1].replace("results_", "").replace(".csv", "")


cols = {}
for path in sys.argv[1:]:
    df = pd.read_csv(path)
    cols[label(path)] = df.set_index(df.columns[0])["auroc"]

out = pd.DataFrame(cols)
out.index = [FAMILY.get(i, i) for i in out.index]
print("AUROC by eval family")
print(out.round(4).to_string())
