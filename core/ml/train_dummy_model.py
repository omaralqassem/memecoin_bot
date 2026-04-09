
#train_dummy_model.py
import pandas as pd
from core.ml.ml_model import MLModel

# Create a dummy dataset
data = [
    {"token_age_seconds": 100, "tx_count_last_min": 5, "rug_score": 10, "hype_mentions_last_5min": 2, "hype_contract_mentions": 1, "target": 1},
    {"token_age_seconds": 50, "tx_count_last_min": 0, "rug_score": -20, "hype_mentions_last_5min": 0, "hype_contract_mentions": 0, "target": 0},
    {"token_age_seconds": 200, "tx_count_last_min": 10, "rug_score": 5, "hype_mentions_last_5min": 3, "hype_contract_mentions": 0, "target": 1},
    {"token_age_seconds": 10, "tx_count_last_min": 1, "rug_score": -10, "hype_mentions_last_5min": 1, "hype_contract_mentions": 0, "target": 0},
]

df = pd.DataFrame(data)

model = MLModel()
model.train(df)