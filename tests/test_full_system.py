import asyncio
import sys
from core.solana_client import SolanaClient
from core.features.token_state import TokenState
from core.features.feature_engine import FeatureEngine
from core.parsers.transaction_parser import extract_mint_and_wallet
from core.features.live_feature_collector import LiveFeatureCollector
from types import SimpleNamespace

async def test_solana_client():
    print("\n=== Testing SolanaClient ===")
    client = SolanaClient()
    try:
        height = await client.get_block_height()
        print("✅ Block height:", height)
    except Exception as e:
        print("❌ SolanaClient failed:", e)
    await client.close()

def test_token_state_and_features():
    print("\n=== Testing TokenState & FeatureEngine ===")
    token = TokenState("FAKE_TOKEN")
    fe = FeatureEngine()

    token.add_transaction("wallet1")
    token.add_transaction("wallet2")
    token.add_mention()
    token.add_mention()
    fe.process_social("FAKE_TOKEN")

    print("TX count last 1m:", token.get_tx_count_1m())
    print("Unique wallets last 1m:", token.get_unique_wallets_1m())
    print("Mentions last 5m:", token.get_mentions_5m())
    print("Token age seconds:", token.get_age())

    fv = fe.build_feature_vector(
        token="FAKE_TOKEN",
        onchain_data={"age_seconds": token.get_age(), "tx_last_min": token.get_tx_count_1m()},
        rug_data={"score": 10, "safe": True}
    )
    print("✅ Feature Vector:", fv)

def test_transaction_parser():
    print("\n=== Testing Transaction Parser ===")

    class MockTx:
        def __init__(self):
            instr = SimpleNamespace(
                program_id="Tokenkeg",
                parsed={"type": "initializeMint", "info": {"mint": "FAKE_MINT"}}
            )
            self.transaction = SimpleNamespace(
                transaction=SimpleNamespace(
                    message=SimpleNamespace(
                        instructions=[instr],
                        account_keys=[SimpleNamespace(pubkey="FAKE_WALLET")]
                    )
                )
            )

    tx = MockTx()
    mint, wallet = extract_mint_and_wallet(tx)
    if mint == "FAKE_MINT" and wallet == "FAKE_WALLET":
        print(f"✅ Mint: {mint}, Wallet: {wallet}")
    else:
        print("❌ Parser failed")

async def test_live_feature_collector():
    print("\n=== Testing LiveFeatureCollector Dry Run ===")
    collector = LiveFeatureCollector()
    await collector.process_new_token({
        "mint_address": "FAKE_TOKEN",
        "rug_score": 0,
        "safe": True,
        "reasons": []
    })
    print("✅ LiveFeatureCollector dry run complete")

async def main():
    test_token_state_and_features()
    test_transaction_parser()
    await test_solana_client()
    await test_live_feature_collector()
    print("\n🎯 All Phase 6 tests complete. Ready for Phase 7!")

if __name__ == "__main__":
    asyncio.run(main())