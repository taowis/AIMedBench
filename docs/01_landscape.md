# Tool Landscape (external, non-CPG)

The initial benchmark suite focuses on **widely-used, externally-developed** tools to show independent evaluation capability.

| Tool | Domain | Primary output | Typical input | Notes |
|---|---|---|---|---|
| SpliceAI (Cell 2019) | Splicing (coding & non-coding) | ∆ score(s) | VCF | Gold-standard for splice impact; strong baseline for splice variants |
| EVE / EVEscape | Missense pathogenicity | Probability/pathogenicity | Missense (gene/protein) | Evolutionary model; contrasts ML vs conservation |
| REVEL | Missense ensemble | Score (0–1) | VCF | Common in clinical pipelines; ensemble baseline |
| DeepSEA | Regulatory variant effect | Assay-specific scores | 1kb sequence | Early DL for non-coding; compare to modern models |
| MVP | Missense DL | Score (0–1) | VCF | DL baseline for coding variants |

**Drop-in pattern:** export each tool’s per-variant score as `variant_id,score,tool` and place in `predictions/external/`.
