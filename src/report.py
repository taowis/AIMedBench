from __future__ import annotations
import json, pandas as pd
from pathlib import Path

def write_manifest(paths_dict, out_path: str):
    Path(out_path).write_text(json.dumps(paths_dict, indent=2))

def write_markdown_report(metrics_df: pd.DataFrame, out_path: str):
    lines = ["# Benchmark Report (demo)", ""]
    # Research metrics section
    lines.append("## Research Metrics (discrimination & scalability)")
    lines.append("")
    if not metrics_df.empty:
        lines.append(metrics_df[['tool','auroc','auprc']].to_markdown(index=False))
    else:
        lines.append("_No research metrics computed_")
    lines.append("")
    # Clinical metrics section
    lines.append("## Clinical Metrics (calibration & safety)")
    lines.append("")
    if not metrics_df.empty:
        if 'brier' in metrics_df.columns:
            lines.append(metrics_df[['tool','brier','n']].to_markdown(index=False))
        else:
            lines.append("_No clinical metrics computed_")
    else:
        lines.append("_No clinical metrics computed_")
    Path(out_path).write_text("\n".join(lines))
