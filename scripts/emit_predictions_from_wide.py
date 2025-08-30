import pandas as pd
from pathlib import Path

df = pd.read_csv("data/truth_labels.tsv")        # needs variant_id
wide = pd.read_csv("data/tool_scores_wide.tsv")  # variant_id, SpliceAI, CADD, REVEL ...

m = df[["variant_id"]].merge(wide, on="variant_id", how="inner")

outdir = Path("results/predictions"); outdir.mkdir(parents=True, exist_ok=True)
for col in m.columns:
    if col in {"variant_id"}: 
        continue
    sub = m[["variant_id", col]].dropna().rename(columns={col: "score"})
    if sub.empty:
        continue
    sub["tool"] = col
    sub.to_csv(outdir / f"{col}.tsv", index=False)
print("Wrote per-tool TSVs to results/predictions/")
