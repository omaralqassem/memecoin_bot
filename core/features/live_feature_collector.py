import asyncio
from core.database import Database
from core.ml.ml_model import MLModel
from core.rug_filter import RugFilter
from core.solana_client import SolanaClient
from config.settings import settings

class LiveFeatureCollector:
    def __init__(self):
        self.db = Database()
        self.solana_client = SolanaClient()
        self.rug_filter = RugFilter(self.solana_client)
        self.ml_model = MLModel()
        print("📡 Advisor Mode Active: Monitoring for Alpha Signals...")

    async def process_new_token(self, event: dict):
        mint = event.get("mint_address")
        if not mint: return

        audit = await self.rug_filter.analyze_token(mint)
        
        hype = self.db.get_hype_count(mint, window_sec=300)
        prob_safe = self.ml_model.predict({
            "rug_score": audit["score"],
            "hype_mentions": hype,
            "tx_count_1m": event.get("tx_count", 1)
        })

        is_signal = (prob_safe >= settings.ML_CONFIDENCE_THRESHOLD) and audit["safe"]

        if is_signal:
            print(f"⚠️ SIGNAL DETECTED: {mint} | Waiting {settings.HYPE_DELAY_SECONDS}s for re-audit...")
            await asyncio.sleep(settings.HYPE_DELAY_SECONDS)
            
            final_audit = await self.rug_filter.analyze_token(mint)
            if final_audit["safe"]:
                print(f"✅ SIGNAL VERIFIED: Sending to Dashboard!")
                self.db.update_token(mint, final_audit["score"], is_safe=True)
            else:
                print(f"🛑 SIGNAL CANCELLED: Token failed re-audit (Delayed Rug).")
        else:
            self.db.update_token(mint, audit["score"], is_safe=False)

    async def start(self, log_listener):
        log_listener.on_event = self.process_new_token
        await log_listener.start()