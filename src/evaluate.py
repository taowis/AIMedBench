from __future__ import annotations
import pandas as pd, numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, precision_recall_curve, roc_curve
from dataclasses import dataclass
from typing import Dict, Tuple

def _safe_auc(y_true, y_score):
    y = np.array(y_true); s = np.array(y_score)
    if len(np.unique(y)) < 2:
        return float('nan')
    return roc_auc_score(y, s)

def _safe_auprc(y_true, y_score):
    y = np.array(y_true); s = np.array(y_score)
    if len(np.unique(y)) < 2:
        return float('nan')
    return average_precision_score(y, s)

def evaluate_predictions(truth: pd.DataFrame, preds: pd.DataFrame) -> pd.DataFrame:
    # truth: variant_id,label ; preds: variant_id,score,tool
    merged = preds.merge(truth, on='variant_id', how='inner')
    out_rows = []
    for tool, g in merged.groupby('tool'):
        auroc = _safe_auc(g['label'], g['score'])
        auprc = _safe_auprc(g['label'], g['score'])
        try:
            brier = brier_score_loss(g['label'], g['score'])
        except Exception:
            brier = float('nan')
        out_rows.append({'tool': tool, 'n': len(g), 'auroc': auroc, 'auprc': auprc, 'brier': brier})
    return pd.DataFrame(out_rows).sort_values('auprc', ascending=False)

def reliability_bins(y_true, y_score, n_bins: int = 10):
    y = np.array(y_true); s = np.array(y_score)
    bins = np.linspace(0,1,n_bins+1)
    idx = np.digitize(s, bins) - 1
    rows = []
    for b in range(n_bins):
        mask = idx==b
        if mask.sum()==0:
            rows.append({'bin': b, 'mean_score': np.nan, 'empirical_pos': np.nan, 'n': 0})
            continue
        rows.append({'bin': b, 'mean_score': float(s[mask].mean()), 'empirical_pos': float(y[mask].mean()), 'n': int(mask.sum())})
    return pd.DataFrame(rows)
