# Rare Disease AI Tool Evaluation

This repository demonstrates **how** I would evaluate third‑party AI/ML tools for **rare disease diagnostics** — focusing on
**reproducibility, fairness, and clinical translation**. It’s intentionally lightweight so reviewers can run it quickly.

> Short nod to CPG context: the evaluation framework draws on modern variant interpretation needs (coding, non‑coding, splicing) and is designed
> to plug into cloud/HPC workflows. It emphasises **benchmark design**, **robust metrics**, **safety analyses**, and **cost/latency profiling**.

## What’s here
- `docs/` — concise design docs (tool landscape, evaluation framework, cloud/HPC feasibility).
- `workflow/` — a Snakemake pipeline that runs a tiny, reproducible demo benchmark end‑to‑end.
- `src/` — simple, clear Python scripts: data IO, toy predictors, metric computation, and report generation.
- `data/` — tiny example datasets (synthetic + a small hand‑made ClinVar‑style file) so this repo runs in seconds.
- `notebooks/` — two minimal notebooks for quick visualization and a “drop‑in predictions” pattern.
- `results/` — pipeline outputs (metrics tables, plots, and a short report).

## The plan → this repo (abridged)
- Curate tools, smoke‑test SDKs, define datasets & metrics → mirrored by `docs/01_landscape.md` and `docs/02_framework.md`.
- Formalize benchmarks and robustness tests → pipeline skeleton in `workflow/Snakefile` + `src/evaluate.py`.
- Feasibility & safety sign‑off, integration guidance → `docs/03_feasibility.md` + generated `results/report.md`.

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

## Where to plug real tools
- Place external tool predictions as TSV/CSV into `predictions/external/` with columns: `variant_id,score,tool`.
- The pipeline will automatically aggregate and re‑compute metrics side‑by‑side with the baselines.
- See `notebooks/spliceai_demo.ipynb` for a minimal “load predictions → evaluate” example.

## Citation of prior scholarship
This repo operationalises evaluation best‑practices I co‑authored in a book chapter: **Lai et al. (2018) Artificial Intelligence and Machine Learning in Bioinformatics (Elsevier)**.
[![Read the paper](https://img.shields.io/badge/Paper-PDF-blue)](docs/Artificial_Intelligence_and_Machine_Learning_in_Bioinformatics-Kaitao_Lai.pdf)

## 📄 Reference Paper

This project builds on concepts described in:

[**Artificial Intelligence and Machine Learning in Bioinformatics** (Elsevier, 2018)](docs/Artificial_Intelligence_and_Machine_Learning_in_Bioinformatics-Kaitao_Lai.pdf)

*Lai K., Twine N., O’Brien A., Guo Y., Bauer D.*

Click the link above to view the PDF.

---
_Repo generated: 2025-08-25_
