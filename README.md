# AIMedBench: Rigorous Evaluation of AI/ML Tools in Rare Disease Genomics

This repository demonstrates **how to rigorously evaluate third-party AI/ML tools** for **rare disease diagnostics** — focusing on  
**reproducibility, fairness, clinical translation, and safety**. It’s intentionally lightweight so reviewers can run it quickly.

> ⚡ Note: This is an **evaluation framework**, not a method development project.  
> Demo baselines (e.g. random, position-based) are included only to illustrate the pipeline; the primary purpose is to benchmark **external AI/ML tools**.

---

## What’s here
- `docs/` — concise design docs: tool landscape, evaluation framework, cloud/HPC feasibility.
- `workflow/` — a Snakemake pipeline running a reproducible demo benchmark end-to-end.
- `src/` — clear Python scripts: data IO, baselines (demo only), metric computation, and report generation.
- `data/` — tiny example datasets (synthetic + ClinVar-style) for fast demo runs.
- `notebooks/` — minimal notebooks for quick visualization and “drop-in predictions” examples.
- `results/` — pipeline outputs: metrics tables, plots, and reports.

---

## 📂 Repository Structure

```
AIMedBench/
├── README.md                         # Project overview and usage instructions
├── LICENSE                           # Open-source license (MIT)
├── .gitignore                        # Files and directories ignored by Git
├── pyproject.toml                     # Python project metadata and dependencies
├── Dockerfile                        # Container image definition for reproducible runs
├── envs/
│   └── environment.yml               # Conda environment specification
├── docs/
│   ├── 01_landscape.md               # Survey of external AI/ML tools to evaluate
│   ├── 02_framework.md               # Evaluation framework (datasets, metrics, clinical vs research priorities)
│   ├── 03_feasibility.md             # Cloud/HPC feasibility and deployment considerations
│   └── Artificial_Intelligence_and_Machine_Learning_in_Bioinformatics-Kaitao_Lai.pdf
│                                     # Reference paper (2018 book chapter)
├── workflow/
│   └── Snakefile                     # Snakemake workflow for running benchmarks end-to-end
├── src/
│   ├── utils.py                      # Helper functions (e.g., build variant IDs)
│   ├── predictions_random.py         # Demo baseline predictor (random scores)
│   ├── predictions_position.py       # Demo baseline predictor (position-based heuristic)
│   ├── aggregate.py                  # Functions to load and merge external tool predictions
│   ├── evaluate.py                   # Metric computation (AUROC, AUPRC, Brier score, etc.)
│   ├── report.py                     # Report generation (Research vs Clinical metrics sections)
│   └── main.py                       # Main pipeline script to run evaluation + reporting
├── data/
│   ├── simulated_variants.tsv        # Synthetic toy variants (demo input)
│   ├── clinvar_tiny.tsv              # Tiny ClinVar-style dataset (pathogenic vs benign)
│   └── truth_labels.tsv              # Ground-truth labels for demo evaluation
├── predictions/
│   └── external/
│       └── spliceai_sample.csv       # Example external tool predictions (SpliceAI demo)
├── notebooks/
│   ├── spliceai_demo.ipynb           # Jupyter notebook: evaluate SpliceAI predictions
│   └── benchmark_dashboard.ipynb     # Jupyter notebook: simple dashboard of results
├── results/                          # Auto-generated outputs from pipeline
│   ├── metrics.tsv                   # Evaluation metrics table
│   ├── report.md                     # Markdown report with research vs clinical metrics
│   └── manifest.json                 # Provenance metadata (datasets, configs, outputs)
├── configs/
│   └── gcp_config.yaml               # Example configuration for GCP/HPC deployment
└── tests/
└── test_metrics.py               # Unit test for metrics computation
```

---

## Evaluation focus
The framework distinguishes priorities in **two settings**:  

- **Research setting**:  
  - Discrimination metrics (AUROC, AUPRC)  
  - Robustness under domain shift  
  - Cost/latency profiling  

- **Clinical setting**:  
  - Calibration (Brier score, reliability curves)  
  - Sensitivity/specificity at clinically meaningful thresholds  
  - False positive/negative rates on benign/pathogenic variants  
  - Interpretability and reproducibility  

---

## The plan → this repo (abridged)
- Curate candidate tools, validate inputs, define datasets & metrics → see `docs/01_landscape.md` and `docs/02_framework.md`.
- Formalize benchmarks and robustness tests → pipeline skeleton (`workflow/Snakefile`) + metric engine (`src/evaluate.py`).
- Clinical feasibility & safety sign-off → `docs/03_feasibility.md` + generated reports in `results/`.

---

## Quickstart (local)
```bash
# Option A: conda
conda env create -f envs/environment.yml
conda activate rd-eval
python -m pip install -e .

# Run the demo benchmark
snakemake -j 1 --directory . --cores 1

# Option B: Docker
docker build -t rd-eval:latest .
docker run --rm -v $PWD:/work -w /work rd-eval:latest   bash -lc "snakemake -j 1 --directory . --cores 1"
```

---

## Where to plug real tools
- Place **external tool predictions** as TSV/CSV into `predictions/external/` with columns:  
  `variant_id,score,tool`  
- The pipeline will automatically aggregate and re-compute metrics side-by-side with baselines.  
- Example: `notebooks/spliceai_demo.ipynb` demonstrates loading SpliceAI predictions and evaluating them.

---

## 📖 Reference & Background
This repo operationalises evaluation best-practices I co-authored in:  

**Lai et al. (2018) Artificial Intelligence and Machine Learning in Bioinformatics (Elsevier)**  

[![Read the paper](https://img.shields.io/badge/Paper-PDF-blue)](docs/Artificial_Intelligence_and_Machine_Learning_in_Bioinformatics-Kaitao_Lai.pdf)

Click to view the PDF.

---

_Repo last updated: 2025-08-25_
