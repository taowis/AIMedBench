from __future__ import annotations
import pandas as pd
from pathlib import Path

def load_external_predictions(folder: str) -> pd.DataFrame:
    p = Path(folder)
    if not p.exists():
        return pd.DataFrame(columns=['variant_id','score','tool'])
    dfs = []
    for f in p.glob('*.tsv'):
        dfs.append(pd.read_csv(f, sep='\t'))
    for f in p.glob('*.csv'):
        dfs.append(pd.read_csv(f))
    if not dfs:
        return pd.DataFrame(columns=['variant_id','score','tool'])
    df = pd.concat(dfs, ignore_index=True)
    needed = {'variant_id','score','tool'}
    if missing := (needed - set(df.columns)):
        raise ValueError(f"External prediction missing columns: {missing}")
    return df[sorted(needed)]
