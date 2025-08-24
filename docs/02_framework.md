# Evaluation Framework (v0.1)

## Datasets
- **Synthetic small set** (`data/simulated_variants.tsv`) with seeded labels.
- **Tiny ClinVar-style set** (`data/clinvar_tiny.tsv`): cols `variant_id,label` (1=pathogenic, 0=benign).

## Variant key
`variant_id = chrom:pos:ref:alt` (1-based, GRCh38 by default).

## Metrics
- **Discrimination:** AUROC, AUPRC
- **Calibration:** Brier score; reliability curve bins
- **Thresholded:** F1, sensitivity, specificity @ chosen operating points
- **Safety checks:** false positive rate on benigns; misclassification of VUS; shift tests on simulated noise

## Protocol
1. Validate I/O (schemas & reference build).
2. Aggregate tool scores by `variant_id` (mean if duplicated per tool).
3. Compute metrics with 95% CIs (bootstrap).
4. Plot ROC/PR + calibration.
5. Write `results/metrics.tsv` and `results/report.md`.

## Robustness
- **Sub-cohorts:** coding vs non-coding; splice-site vs deep intronic; gene panels
- **Shift:** add label noise (5–10%), subsample coverage
- **Fairness:** ancestry-stratified when data available

## Reproducibility
- Snakemake + pinned env
- Deterministic seeds
- Clear provenance in `results/manifest.json`
