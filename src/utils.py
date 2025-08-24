from __future__ import annotations
import pandas as pd
from dataclasses import dataclass
from typing import Iterable

def make_variant_id(chrom: str, pos: int, ref: str, alt: str) -> str:
    return f"{chrom}:{pos}:{ref}:{alt}"

def load_variants_table(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep='\t', comment='#')
    if df.columns[0].startswith('#'):
        df.columns = [c.lstrip('#') for c in df.columns]
    required = {'chrom','pos','ref','alt'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    df['variant_id'] = df.apply(lambda r: make_variant_id(str(r['chrom']), int(r['pos']), str(r['ref']), str(r['alt'])), axis=1)
    return df[['variant_id','chrom','pos','ref','alt']]
