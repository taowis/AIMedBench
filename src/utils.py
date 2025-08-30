from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Dict, Any


def load_variants_table(path: str | Path) -> pd.DataFrame:
    """
    Load a variant table from TSV with expected columns:
        chrom, pos, ref, alt
    - Accepts headers like '#chrom' or 'CHROM'.
    - Normalizes column names to lowercase without leading '#'.
    - Ensures 'pos' is integer-like, coerced to string for stable IDs.
    - Adds a 'variant_id' column in the format: chrom:pos:ref:alt
    """
    df = pd.read_csv(path, sep="\t", dtype=str, comment="#")

    # Normalize column names: strip whitespace, leading '#', lowercase
    norm_map: Dict[str, str] = {c: c.strip().lstrip("#").lower() for c in df.columns}
    df.rename(columns=norm_map, inplace=True)

    required = {"chrom", "pos", "ref", "alt"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Ensure canonical types
    df["chrom"] = df["chrom"].astype(str)
    # keep pos numeric for sorting but store as string for ID building
    df["pos"] = df["pos"].astype(int).astype(str)
    df["ref"] = df["ref"].astype(str)
    df["alt"] = df["alt"].astype(str)

    # Construct variant_id
    df["variant_id"] = df["chrom"] + ":" + df["pos"] + ":" + df["ref"] + ":" + df["alt"]

    return df


def save_table(df: pd.DataFrame, path: str | Path, sep: str = "\t", index: bool = False) -> None:
    """
    Save a DataFrame to disk as TSV/CSV with UTF-8 encoding.
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, sep=sep, index=index, encoding="utf-8")


def preview_table(df: pd.DataFrame, n: int = 5) -> str:
    """
    Return a small string preview of a DataFrame (head and shape).
    """
    head = df.head(n).to_string(index=False)
    return f"DataFrame shape={df.shape}\n{head}"
