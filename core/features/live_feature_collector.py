#live_feature_collector.py
import asyncio
from core.database import Database
from core.ml.ml_model import MLModel
from core.log_listener import SolanaLogListener

class LiveFeatureCollector:
    def __init__(self):
        self.db = Database()
        self.ml_model = MLModel()
        self.log_listener = SolanaLogListener(event_callback=self.process_new_token)

    async def start(self):
        print("🚀 Starting Bot with SQL Memory...")
        await self.log_listener.start()

    async def process_new_token(self, event: dict):
        mint = event.get("mint_address")
        rug_data = event.get("rug_results", {"score": 0, "safe": False})
        
        hype_count = self.db.get_hype_count(mint)
        
        fv = {
            "token_age_seconds": 0,
            "tx_count_last_min": event.get("tx_count", 1),
            "rug_score": rug_data["score"],
            "hype_mentions_last_5min": hype_count
        }

        # 3. Predict
        prob_safe = self.ml_model.predict(fv)
        
        # 4. Save to DB for Streamlit to see
        self.db.update_token(
            mint=mint,
            rug_score=rug_data["score"],
            is_safe=(prob_safe > 0.7),
            tx_count=fv["tx_count_last_min"]
        )
        
        print(f"DEBUG: Token {mint} processed. Safe Prob: {prob_safe:.2f}")