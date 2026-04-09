import asyncio
from core.solana_client import SolanaClient


async def test():
    client = SolanaClient()

    print("🔌 Testing Solana connection...")

    block_height = await client.get_block_height()
    print(f"✅ Block Height: {block_height}")

    wallet = "GxTxeLnf9ttazaNYVJrNfxpW2ghB3qXgSvbyF3LXzyFd"

    balance = await client.get_balance(wallet)
    print(f"💰 Wallet Balance: {balance} SOL")

    await client.close()


if __name__ == "__main__":
    asyncio.run(test())