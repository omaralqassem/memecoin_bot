#rug_filter.py
import asyncio
from typing import Dict, Any, List
from solders.pubkey import Pubkey

class RugFilter:
    def __init__(self, solana_client):
        self.client = solana_client
        self.BURN_ADDRESSES = [
            "11111111111111111111111111111111", 
            "dead000000000000000000000000000000000000",
            "Burned0000000000000000000000000000000000"
        ]

    async def analyze_token(self, mint_address: str) -> Dict[str, Any]:
   
        score = 100
        reasons = []

        try:
            account_info_task = self.client.get_account_info(mint_address)
            supply_task = self.client.get_token_supply(mint_address)
            holders_task = self.client.get_largest_accounts(mint_address)

            account_info, total_supply, holders = await asyncio.gather(
                account_info_task, supply_task, holders_task
            )

            if not account_info:
                return {"safe": False, "score": 0, "reasons": ["Token data not found"]}

            parsed_data = account_info.data.get('parsed', {}).get('info', {})
            
            if parsed_data.get("mintAuthority"):
                score -= 50
                reasons.append("Mint Authority Enabled (Risk of unlimited supply)")
            
            if parsed_data.get("freezeAuthority"):
                score -= 40
                reasons.append("Freeze Authority Enabled (Risk of Honeypot)")

            if total_supply > 0 and holders:

                danger_holdings = 0
                for holder in holders[:10]: 
                    holder_address = holder.address
                    if str(holder_address) not in self.BURN_ADDRESSES:
                        percent = (float(holder.amount) / (10**9)) / total_supply * 100
                        if percent > 15:
                            score -= 20
                            reasons.append(f"Top Holder concentration: {percent:.1f}%")

 
            if total_supply == 0:
                score -= 100
                reasons.append("Total supply is 0 or unreadable")

        except Exception as e:
            print(f"⚠️ RugFilter Analysis Error: {e}")
            return {"safe": False, "score": 0, "reasons": [f"Audit failed: {str(e)}"]}

        is_safe = score >= 60
        return {
            "safe": is_safe,
            "score": max(0, score),
            "reasons": reasons
        }