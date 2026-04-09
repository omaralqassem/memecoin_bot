#feature_engine.py

import pandas as pd
import time
from typing import Dict, Any
from collections import defaultdict

class FeatureEngine:
    def __init__(self):
        self.hype_mentions = defaultdict(list)
        self.hype_contract_mentions = defaultdict(list)


    def process_social(self, token: str, is_contract=False):
        now = time.time()
        if is_contract:
            self.hype_contract_mentions[token].append(now)
        else:
            self.hype_mentions[token].append(now)

    def get_hype_score(self, token: str, window_seconds=300):
        now = time.time()
        mentions = [t for t in self.hype_mentions[token] if now - t <= window_seconds]
        contracts = [t for t in self.hype_contract_mentions[token] if now - t <= window_seconds]
        return len(mentions), len(contracts)

  
    def build_feature_vector(self, token: str, onchain_data: Dict[str, Any], rug_data: Dict[str, Any]):
        mentions, contract_mentions = self.get_hype_score(token)

        feature_vector = {
            "token": token,
            "token_age_seconds": onchain_data.get("age_seconds", 0),
            "tx_count_last_min": onchain_data.get("tx_last_min", 0),
            "rug_score": rug_data.get("score", 0),
            "hype_mentions_last_5min": mentions,
            "hype_contract_mentions": contract_mentions
        }

        return feature_vector

    def to_dataframe(self, feature_vectors: list):
        return pd.DataFrame(feature_vectors)