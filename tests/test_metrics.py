import pandas as pd
from src.evaluate import evaluate_predictions

def test_metrics_computation():
    truth = pd.DataFrame({'variant_id':['v1','v2','v3','v4'], 'label':[0,0,1,1]})
    preds = pd.DataFrame({'variant_id':['v1','v2','v3','v4'], 'score':[0.1,0.2,0.8,0.9], 'tool':'x'})
    m = evaluate_predictions(truth, preds)
    assert m['auroc'].iloc[0] > 0.9
