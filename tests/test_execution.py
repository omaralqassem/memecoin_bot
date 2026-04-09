import asyncio
from core.execution.execution_engine import ExecutionEngine
from solders.keypair import Keypair

import json

def load_wallet(path="devnet.json"):
    with open(path, "r") as f:
        secret = json.load(f)
    return Keypair.from_bytes(bytes(secret))

async def test_swap():
    wallet = load_wallet()
    engine = ExecutionEngine(wallet)

    token_in = "So11111111111111111111111111111111111111112"
    token_out = "F6Zt96rQZ6cZ1bG8bnj6fQWc1YjF6t3g49fJcP29AmuG"
    
    print("🚀 Executing REAL devnet swap...")
    await engine.swap(token_in, token_out, 0.01)

    await engine.close()

asyncio.run(test_swap())