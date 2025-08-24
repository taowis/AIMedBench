# Cloud/HPC Feasibility (sketch)

## Footprint (demo scale)
- CPU-only; runs in seconds on a laptop.

## Production sketch
- **Executor:** GCP Batch or HPC scheduler
- **Storage:** GCS buckets; partitioned by cohort/date
- **Orchestration:** Snakemake profiles or Nextflow
- **Containers:** Docker/Apptainer images for each tool
- **Observability:** logs + cost (per run), artifact registry

## Controls
- Version pinning (tool + ref build)
- Model card links where available
- Auto-generated `results/report.md`
