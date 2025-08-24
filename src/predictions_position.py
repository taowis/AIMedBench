from __future__ import annotations
import numpy as np, pandas as pd

def score(variants: pd.DataFrame) -> pd.DataFrame:
    # Toy heuristic: normalized sine of position to simulate a non-trivial signal
    pos = variants['pos'].astype(int).to_numpy()
    s = (np.sin(pos / 1000.0) + 1) / 2.0  # 0..1
    return pd.DataFrame({'variant_id': variants['variant_id'].values,
                         'score': s,
                         'tool': 'pos_sine_baseline'})
