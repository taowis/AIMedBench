from __future__ import annotations
import json, pandas as pd
from pathlib import Path

def write_manifest(paths_dict, out_path: str):
    Path(out_path).write_text(json.dumps(paths_dict, indent=2))

def write_markdown_report(metrics_df: pd.DataFrame, out_path: str):
    lines = ["# Benchmark Report (demo)", "", metrics_df.to_markdown(index=False)]
    Path(out_path).write_text("\n".join(lines))
