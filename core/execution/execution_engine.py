#execution_engine.py
import asyncio
import base64
import requests
from solana.rpc.async_api import AsyncClient
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from solana.rpc.types import TxOpts

JUPITER_QUOTE_API = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_API = "https://quote-api.jup.ag/v6/swap"


class ExecutionEngine:
    def __init__(self, wallet: Keypair, rpc_url="https://api.devnet.solana.com"):
        self.wallet = wallet
        self.client = AsyncClient(rpc_url)

    async def get_swap_transaction(self, route: dict, slippage_bps=50):
        payload = {
            "route": route,
            "userPublicKey": str(self.wallet.pubkey()),
            "wrapUnwrapSOL": True,
            "asLegacyTransaction": False,
            "slippageBps": slippage_bps
        }

        resp = requests.post(JUPITER_SWAP_API, json=payload, timeout=10)
        data = resp.json()

        if "swapTransaction" in data:
            return data["swapTransaction"]

        print("Swap API error:", data)
        return None

    async def execute_swap(self, swap_tx_b64: str):
        swap_tx_bytes = base64.b64decode(swap_tx_b64)
        txn = VersionedTransaction.deserialize(swap_tx_bytes)

        resp = await self.client.send_transaction(
            txn,
            self.wallet,
            opts=TxOpts(skip_preflight=True)
        )

        signature = resp.value
        print("Transaction signature:", signature)

        await self.client.confirm_transaction(signature)
        print("Transaction confirmed")

    async def swap(self, token_in: str, token_out: str, amount: float, slippage_bps=50):
        amount_lamports = int(amount * 1e9)  # SOL = 9 decimals

        quote_url = (
            f"{JUPITER_QUOTE_API}"
            f"?inputMint={token_in}"
            f"&outputMint={token_out}"
            f"&amount={amount_lamports}"
            f"&slippageBps={slippage_bps}"
        )

        print("DEBUG QUOTE URL:", quote_url)

        try:
            resp = requests.get(quote_url, timeout=10)
            data = resp.json()
        except Exception as e:
            print("Quote request failed:", e)
            return

        if "data" not in data or len(data["data"]) == 0:
            print("No route found")
            return

        best_route = data["data"][0]

        swap_tx_b64 = await self.get_swap_transaction(best_route, slippage_bps)
        if not swap_tx_b64:
            print("Failed to get swap transaction")
            return

        await self.execute_swap(swap_tx_b64)

    async def close(self):
        await self.client.close()


async def main():
    wallet = Keypair()  
    engine = ExecutionEngine(wallet)

    token_in = "So11111111111111111111111111111111111111112"  # SOL
    token_out = "Es9vMFrzaCERmJfrh2y1k4EYBLETymFcpnSUsctNk6he"  # USDT (better liquidity)

    amount = 0.01

    print("🚀 Executing devnet swap...")
    await engine.swap(token_in, token_out, amount)

    await engine.close()


if __name__ == "__main__":
    asyncio.run(main())