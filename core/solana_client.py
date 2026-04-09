#solana_client.py

import asyncio
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from config.settings import settings
from solders.signature import Signature

class SolanaClient:
    def __init__(self):
        self.client = AsyncClient(settings.SOLANA_RPC_URL)

    async def get_block_height(self) -> int:
        resp = await self.client.get_block_height()
        return resp.value
    async def get_transaction(self, signature: str):
        sig = Signature.from_string(signature)
        resp = await self.client.get_transaction(sig, encoding="jsonParsed")
        return resp.value
    async def get_balance(self, wallet_address: str) -> float:
        pubkey = Pubkey.from_string(wallet_address)
        resp = await self.client.get_balance(pubkey)
        return resp.value / 1e9  

    async def get_recent_blockhash(self):
        resp = await self.client.get_latest_blockhash()
        return resp.value.blockhash

    async def close(self):
        await self.client.close()