#solana_client.py

import asyncio
from typing import Optional, List, Any
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed, Confirmed
from solders.pubkey import Pubkey
from solders.signature import Signature
from config.settings import settings

class SolanaClient:
    def __init__(self):
        self.client = AsyncClient(settings.SOLANA_RPC_URL, commitment=Processed)

    async def get_block_height(self) -> int:
        resp = await self.client.get_block_height()
        return resp.value

    async def get_balance(self, wallet_address: str) -> float:
        pubkey = Pubkey.from_string(wallet_address)
        resp = await self.client.get_balance(pubkey)
        return resp.value / 1e9  # Convert Lamports to SOL

    async def get_transaction(self, signature_str: str):
        """Fetches parsed transaction details for mint/wallet extraction"""
        sig = Signature.from_string(signature_str)
        resp = await self.client.get_transaction(
            sig, 
            encoding="jsonParsed", 
            max_supported_transaction_version=0
        )
        return resp.value

    async def get_token_supply(self, mint_address: str) -> float:
        try:
            pubkey = Pubkey.from_string(mint_address)
            resp = await self.client.get_token_supply(pubkey)
            if resp.value:
                # amount is a string in the RPC response to avoid precision loss
                return float(resp.value.amount) / (10 ** resp.value.decimals)
            return 0.0
        except Exception as e:
            print(f"⚠️ Error fetching supply for {mint_address}: {e}")
            return 0.0

    async def get_largest_accounts(self, mint_address: str) -> List[Any]:
        try:
            pubkey = Pubkey.from_string(mint_address)
            resp = await self.client.get_token_largest_accounts(pubkey)
            return resp.value if resp.value else []
        except Exception as e:
            print(f"⚠️ Error fetching holders for {mint_address}: {e}")
            return []

    async def get_account_info(self, address: str):
        try:
            pubkey = Pubkey.from_string(address)
            resp = await self.client.get_account_info_json_parsed(pubkey)
            return resp.value
        except Exception as e:
            print(f"⚠️ Error fetching account info: {e}")
            return None

    async def get_recent_blockhash(self):
        resp = await self.client.get_latest_blockhash()
        return resp.value.blockhash

    async def close(self):
        await self.client.close()