from __future__ import annotations
import numpy as np, pandas as pd

def score(variants: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    scores = rng.random(len(variants))
    return pd.DataFrame({'variant_id': variants['variant_id'].values,
                         'score': scores,
                         'tool': 'random_baseline'})
