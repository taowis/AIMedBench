from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, UTC
from glob import glob
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

# Local utils: expects load_variants_table(path) that returns a DataFrame
# with columns: chrom, pos, ref, alt, and a computed variant_id
from utils import load_variants_table  # noqa: F401


# ---------------------------
# IO helpers
# ---------------------------

DATA_DIR = Path("data")
RESULTS_DIR = Path("results")
PRED_DIR = RESULTS_DIR / "predictions"

DATA_VARIANTS = DATA_DIR / "simulated_variants.tsv"
DATA_TRUTH = DATA_DIR / "truth_labels.tsv"

OUT_METRICS = RESULTS_DIR / "metrics.tsv"
OUT_REPORT = RESULTS_DIR / "report.md"
OUT_MANIFEST = RESULTS_DIR / "manifest.json"


def ensure_dirs() -> None:
    RESULTS_DIR.mkdir(exist_ok=True, parents=True)
    (RESULTS_DIR / "predictions").mkdir(exist_ok=True, parents=True)


def load_truth_labels(path: Path) -> pd.DataFrame:
    """
    Load truth labels as a DataFrame with columns: variant_id,label (0/1 int).
    """
    df = pd.read_csv(path, dtype={"variant_id": str, "label": int})
    # basic sanity
    if not {"variant_id", "label"}.issubset(df.columns):
        raise ValueError("truth_labels.tsv must have columns: variant_id,label")
    df["label"] = df["label"].astype(int)
    return df[["variant_id", "label"]]


def load_prediction_files(pred_dir: Path) -> List[Path]:
    """
    Return list of .tsv files inside results/predictions.
    """
    files = [Path(p) for p in glob(str(pred_dir / "*.tsv"))]
    return sorted(files)


def read_predictions(paths: List[Path]) -> pd.DataFrame:
    """
    Read and concat prediction TSVs with columns: variant_id,score,tool.
    """
    frames = []
    for p in paths:
        df = pd.read_csv(p, dtype={"variant_id": str, "score": float, "tool": str})
        required = {"variant_id", "score", "tool"}
        if not required.issubset(df.columns):
            raise ValueError(f"{p} must have columns: variant_id,score,tool")
        frames.append(df[["variant_id", "score", "tool"]])
    if frames:
        return pd.concat(frames, ignore_index=True)
    else:
        return pd.DataFrame(columns=["variant_id", "score", "tool"])


# ---------------------------
# Baseline predictors
# ---------------------------

def make_random_baseline(variant_ids: pd.Series, seed: int = 42) -> pd.DataFrame:
    rng = np.random.RandomState(seed)
    scores = rng.rand(len(variant_ids))
    return pd.DataFrame({"variant_id": variant_ids, "score": scores, "tool": "random_baseline"})


def make_pos_sine_baseline(variant_ids: pd.Series) -> pd.DataFrame:
    """
    Deterministic 'toy' baseline: score = scaled sine of position index.
    Only uses ordering (acts like a weak positional prior).
    """
    x = np.arange(len(variant_ids))
    s = (np.sin(x / 17.0) + 1.0) / 2.0  # in [0,1]
    return pd.DataFrame({"variant_id": variant_ids, "score": s, "tool": "pos_sine_baseline"})


# ---------------------------
# Metrics & bootstrap CIs
# ---------------------------

@dataclass
class MetricRow:
    tool: str
    n: int
    auroc: float
    auprc: float
    brier: float
    auroc_ci_low: Optional[float] = None
    auroc_ci_high: Optional[float] = None
    auprc_ci_low: Optional[float] = None
    auprc_ci_high: Optional[float] = None


def _safe_auc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    # AUROC requires both classes present
    y = np.asarray(y_true)
    if len(np.unique(y)) < 2:
        return float("nan")
    return roc_auc_score(y_true, y_score)


def _safe_auprc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    # AUPRC is defined even with class imbalance; will still work for 1 class but is not informative
    return average_precision_score(y_true, y_score)


def bootstrap_ci(
    y_true: np.ndarray,
    y_score: np.ndarray,
    scorer: Callable[[np.ndarray, np.ndarray], float],
    n_boot: int = 1000,
    seed: int = 42,
    ci: float = 0.95,
) -> (float, float):
    rng = np.random.RandomState(seed)
    n = len(y_true)
    idx = np.arange(n)
    vals: List[float] = []
    for _ in range(n_boot):
        b = rng.choice(idx, size=n, replace=True)
        val = scorer(y_true[b], y_score[b])
        if not (isinstance(val, float) or isinstance(val, np.floating)):
            # some scorers might return arrays; reduce to float if needed
            val = float(val)
        vals.append(val)
    alpha = (1.0 - ci) * 100.0 / 2.0
    lo, hi = np.percentile(vals, [alpha, 100 - alpha])
    return float(lo), float(hi)


def evaluate_tools(truth: pd.DataFrame, preds: pd.DataFrame, do_bootstrap: bool = True) -> pd.DataFrame:
    """
    truth: DataFrame with [variant_id, label]
    preds: DataFrame with [variant_id, score, tool]
    """
    # Align
    merged = preds.merge(truth, on="variant_id", how="inner")
    rows: List[MetricRow] = []

    for tool, sub in merged.groupby("tool", sort=True):
        y = sub["label"].to_numpy(dtype=int)
        s = sub["score"].to_numpy(dtype=float)

        # Brier score requires probability-like scores in [0,1]
        brier = float(np.mean((s - y) ** 2))

        auroc = _safe_auc(y, s)
        auprc = _safe_auprc(y, s)

        auroc_ci_low = auroc_ci_high = auprc_ci_low = auprc_ci_high = None
        if do_bootstrap and len(sub) >= 50 and np.isfinite(auroc):  # small sets give unstable CIs
            auroc_ci_low, auroc_ci_high = bootstrap_ci(y, s, _safe_auc)
            auprc_ci_low, auprc_ci_high = bootstrap_ci(y, s, _safe_auprc)

        rows.append(
            MetricRow(
                tool=tool,
                n=len(sub),
                auroc=float(auroc) if np.isfinite(auroc) else float("nan"),
                auprc=float(auprc),
                brier=brier,
                auroc_ci_low=auroc_ci_low,
                auroc_ci_high=auroc_ci_high,
                auprc_ci_low=auprc_ci_low,
                auprc_ci_high=auprc_ci_high,
            )
        )

    # Sort: best AUROC first, then AUPRC
    out = pd.DataFrame([r.__dict__ for r in rows])
    if not out.empty:
        out.sort_values(by=["auroc", "auprc"], ascending=[False, False], inplace=True, ignore_index=True)
    return out


# ---------------------------
# Reporting
# ---------------------------

def write_manifest(manifest_path: Path, metrics_df: pd.DataFrame, extras: Dict) -> None:
    meta = {
        "generated_at": datetime.now(UTC).isoformat(),
        "n_tools": int(metrics_df.shape[0]),
        "columns": list(metrics_df.columns),
    }
    meta.update(extras or {})
    manifest_path.write_text(json.dumps(meta, indent=2))


def write_report(report_path: Path, metrics_df: pd.DataFrame, n_variants: int) -> None:
    lines: List[str] = []
    lines.append("# AIMedBench Report\n")
    lines.append(f"- Total variants evaluated: **{n_variants}**\n")
    lines.append(f"- Tools compared: **{metrics_df.shape[0]}**\n")
    lines.append("\n## Metrics\n")
    # Markdown table
    cols = ["tool", "n", "auroc", "auprc", "brier", "auroc_ci_low", "auroc_ci_high", "auprc_ci_low", "auprc_ci_high"]
    present = [c for c in cols if c in metrics_df.columns]
    table = metrics_df[present].copy()

    # Format floats for readability
    for c in present:
        if c in {"tool"}:
            continue
        if table[c].dtype.kind in "fc":
            table[c] = table[c].map(lambda x: f"{x:.6f}" if pd.notnull(x) else "")

    # Convert to markdown
    lines.append(table.to_markdown(index=False))
    lines.append("\n")

    # Narrative summary
    if not metrics_df.empty:
        best = metrics_df.iloc[0]
        summary = f"**Top-ranked tool:** {best['tool']} (n={int(best['n'])}). "
        if not math.isnan(best["auroc"]):
            summary += f"AUROC={best['auroc']:.3f}"
            if "auroc_ci_low" in metrics_df.columns and pd.notnull(best.get("auroc_ci_low", np.nan)):
                summary += f" (95% CI {best['auroc_ci_low']:.3f}–{best['auroc_ci_high']:.3f})"
            summary += "; "
        summary += f"AUPRC={best['auprc']:.3f}"
        if "auprc_ci_low" in metrics_df.columns and pd.notnull(best.get("auprc_ci_low", np.nan)):
            summary += f" (95% CI {best['auprc_ci_low']:.3f}–{best['auprc_ci_high']:.3f})"
        summary += f"; Brier={best['brier']:.3f}."
        lines.append("## Summary\n")
        lines.append(summary + "\n")

    report_path.write_text("\n".join(lines))


# ---------------------------
# Main
# ---------------------------

def main() -> None:
    ensure_dirs()

    # Load variants (adds .variant_id)
    variants = load_variants_table(str(DATA_VARIANTS))
    if "variant_id" not in variants.columns:
        # If your utils doesn't construct it, do it here just in case
        variants["pos"] = variants["pos"].astype(str)
        variants["variant_id"] = variants["chrom"].astype(str) + ":" + variants["pos"] + ":" + variants["ref"] + ":" + variants["alt"]

    # Load truth labels
    truth = load_truth_labels(DATA_TRUTH)

    # Read real predictions if present
    pred_files = load_prediction_files(PRED_DIR)
    preds = read_predictions(pred_files)

    # If none present, build baselines
    if preds.empty:
        vb = variants["variant_id"]
        baseline_frames = [
            make_random_baseline(vb, seed=42),
            make_pos_sine_baseline(vb),
        ]
        preds = pd.concat(baseline_frames, ignore_index=True)

    # Drop predictions for variants without labels
    preds = preds.merge(truth[["variant_id"]], on="variant_id", how="inner")

    # Evaluate
    metrics_df = evaluate_tools(truth, preds, do_bootstrap=True)

    # Write outputs
    metrics_df.to_csv(OUT_METRICS, sep="\t", index=False)
    write_report(OUT_REPORT, metrics_df, n_variants=int(truth.shape[0]))

    manifest_extras = {
        "n_variants_total": int(truth.shape[0]),
        "prediction_files": [str(p) for p in pred_files],
        "has_real_predictions": bool(len(pred_files) > 0),
    }
    write_manifest(OUT_MANIFEST, metrics_df, manifest_extras)

    # Console preview
    with pd.option_context("display.max_columns", None, "display.width", 140):
        print(metrics_df)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Make Snakemake error surfaces obvious
        print(f"[AIMedBench] Fatal error: {e}", file=sys.stderr)
        raise
