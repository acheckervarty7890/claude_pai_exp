"""Collate results/*.csv into one table of eval AUROC per run."""
import csv
from pathlib import Path

ORDER = ["v0", "v1", "v2", "v3", "v4a", "v4b", "v5", "v5ns", "v6", "v7", "v5_s7", "final"]
DESC = {
    "v0": "seed only (50)",
    "v1": "+batch1 (149)",
    "v2": "+batch2 (296)",
    "v3": "+batch3 shapes (376)",
    "v4a": "b1+b2+b4, no b3 (347)",
    "v4b": "all incl. b3 (427)",
    "v5": "v4a+b5 pairs (431)",
    "v5ns": "v5 without seed (381)",
    "v6": "v5+batch6 (495)",
    "v7": "v5+batch7 acks (479)",
    "v5_s7": "v5 data, seed 7 (431)",
    "final": "final probe",
}

rows = []
for tag in ORDER:
    p = Path("results") / f"{tag}.csv"
    if not p.exists():
        continue
    d = {r["dataset"]: float(r["auroc"]) for r in csv.DictReader(p.open())}
    rows.append((tag, d))

hdr = ["run", "description", "mean", "a", "b", "c", "d"]
print(f"{hdr[0]:<7}{hdr[1]:<26}" + "".join(f"{h:>8}" for h in hdr[2:]))
best = max(rows, key=lambda r: r[1]["mean"])[0] if rows else None
for tag, d in rows:
    mark = "  <- best" if tag == best else ""
    print(f"{tag:<7}{DESC.get(tag,''):<26}" + "".join(f"{d[k]:>8.4f}" for k in ["mean","a","b","c","d"]) + mark)
