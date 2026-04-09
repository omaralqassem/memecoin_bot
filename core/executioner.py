import base64
import httpx # Async HTTP is faster than requests
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from config.settings import settings

class Executioner:
    def __init__(self):
        self.keypair = Keypair.from_base58_string(settings.PRIVATE_KEY)
        self.quote_url = "https://quote-api.jup.ag/v6/quote"
        self.swap_url = "https://quote-api.jup.ag/v6/swap"

    async def get_quote(self, output_mint: str, amount_sol: float):
        amount_lamports = int(amount_sol * 1e9)
        params = {
            "inputMint": "So11111111111111111111111111111111111111112", # SOL
            "outputMint": output_mint,
            "amount": amount_lamports,
            "slippageBps": 1000, 
            "onlyDirectRoutes": "false"
        }
        async with httpx.AsyncClient() as client:
            res = await client.get(self.quote_url, params=params)
            return res.json()

    async def get_swap_transaction(self, quote_response):
        """Converts the quote into a serialized transaction"""
        payload = {
            "quoteResponse": quote_response,
            "userPublicKey": str(self.keypair.pubkey()),
            "wrapAndUnwrapSol": True,
            "prioritizationFeeLamports": settings.JITO_TIP_LAMPORT
        }
        async with httpx.AsyncClient() as client:
            res = await client.post(self.swap_url, json=payload)
            return res.json().get("swapTransaction")

    async def execute_trade(self, mint: str, amount: float):
        try:
            print(f"🎯 Attempting to buy {mint} for {amount} SOL...")
            
            quote = await self.get_quote(mint, amount)
            if "error" in quote:
                print(f"❌ Quote failed: {quote['error']}")
                return

            raw_tx_b64 = await self.get_swap_transaction(quote)
            if not raw_tx_b64:
                print("❌ Failed to build transaction")
                return

            raw_tx = base64.b64decode(raw_tx_b64)
            tx = VersionedTransaction.from_bytes(raw_tx)
            
           
            print(f"✅ Transaction signed for {mint}. Sending to blockchain...")
            
            return tx
        except Exception as e:
            print(f"⚠️ Execution Error: {e}")