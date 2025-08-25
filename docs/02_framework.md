# Evaluation Framework (v0.2)

## Datasets
- **Synthetic small set** (`data/simulated_variants.tsv`) with seeded labels.
- **Tiny ClinVar-style set** (`data/clinvar_tiny.tsv`): cols `variant_id,label` (1=pathogenic, 0=benign).

## Variant key
`variant_id = chrom:pos:ref:alt` (1-based, GRCh38 by default).

---

## Evaluation Dimensions

### Research setting
- **Discrimination:** AUROC, AUPRC
- **Robustness:** performance under domain shift (noise, subsampling, ancestry stratification)
- **Scalability:** runtime, cost/latency profiling on HPC/GCP
- **Reproducibility:** deterministic runs, containerized workflows

### Clinical setting
- **Calibration:** Brier score, reliability curves
- **Thresholded metrics:** Sensitivity, Specificity, PPV, NPV at clinically meaningful cutoffs
- **Safety checks:** false positives on benigns, misclassification of VUS
- **Interpretability:** ability to provide variant/gene-level insights that clinicians can act upon
- **Provenance:** auditability and clear documentation of results

---

## Protocol
1. Validate I/O (schemas & reference build).
2. Aggregate tool scores by `variant_id` (mean if duplicated per tool).
3. Compute metrics with 95% CIs (bootstrap).
4. Plot ROC/PR + calibration curves.
5. Write `results/metrics.tsv` and `results/report.md`.
6. Include both research and clinical evaluation summaries.

---

## Robustness & Fairness
- **Sub-cohorts:** coding vs non-coding; splice-site vs deep intronic; gene panels
- **Shift tests:** add label noise (5–10%), simulate coverage differences
- **Fairness:** ancestry- and sex-stratified performance where data is available

---

## Reproducibility
- Snakemake workflow with pinned environment (`envs/environment.yml`)
- Docker/Apptainer container images for portability
- Clear provenance via auto-generated `results/manifest.json`

---

_Version 0.2 — Updated with Clinical vs Research Evaluation Priorities_
