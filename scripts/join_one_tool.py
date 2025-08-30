import pandas as pd
from pathlib import Path

# 1) Your variants (must have chrom,pos,ref,alt,variant_id)
v = pd.read_csv("data/simulated_variants.tsv", sep="\t", dtype=str)
v["pos"] = v["pos"].astype(int)
v["variant_id"] = v["chrom"].astype(str) + ":" + v["pos"].astype(str) + ":" + v["ref"] + ":" + v["alt"]

# 2) Tool file (example format): chrom, pos, ref, alt, score
tool_name = "SpliceAI"
tool = pd.read_csv("data/tools/SpliceAI_scores.tsv.gz", sep="\t", dtype=str)
tool["pos"] = tool["pos"].astype(int)
tool["score"] = pd.to_numeric(tool["score"], errors="coerce")

# 3) Inner join and emit to results/predictions
m = v.merge(tool, on=["chrom","pos","ref","alt"], how="inner")
pred = m[["variant_id","score"]].dropna()
pred["tool"] = tool_name

outdir = Path("results/predictions"); outdir.mkdir(parents=True, exist_ok=True)
pred.to_csv(outdir / f"{tool_name}.tsv", index=False)
print(f"Wrote results/predictions/{tool_name}.tsv with {len(pred)} rows")
