from __future__ import annotations
import pandas as pd
from pathlib import Path
from src.utils import load_variants_table
from src.predictions_random import score as random_score
from src.predictions_position import score as pos_score
from src.aggregate import load_external_predictions
from src.evaluate import evaluate_predictions
from src.report import write_manifest, write_markdown_report

DATA_VARIANTS = 'data/simulated_variants.tsv'
TRUTH = 'data/truth_labels.tsv'
EXTERNAL_DIR = 'predictions/external'
RESULTS_DIR = 'results'

def main():
    Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)
    variants = load_variants_table(DATA_VARIANTS)
    truth = pd.read_csv(TRUTH)
    # Baselines
    preds = [random_score(variants, seed=7), pos_score(variants)]
    # External
    ext = load_external_predictions(EXTERNAL_DIR)
    if len(ext):
        preds.append(ext)
    all_preds = pd.concat(preds, ignore_index=True)
    metrics = evaluate_predictions(truth, all_preds)
    metrics_path = f"{RESULTS_DIR}/metrics.tsv"
    metrics.to_csv(metrics_path, sep='\t', index=False)
    write_markdown_report(metrics, f"{RESULTS_DIR}/report.md")
    write_manifest({'variants': DATA_VARIANTS, 'truth': TRUTH, 'external_dir': EXTERNAL_DIR, 'metrics': metrics_path},
                   f"{RESULTS_DIR}/manifest.json")
    print(metrics)

if __name__ == "__main__":
    main()
