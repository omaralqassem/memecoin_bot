# tests/test_phase7_live_ml.py
import asyncio
from core.features.live_feature_collector import LiveFeatureCollector
from core.ml.ml_model import MLModel

async def test_phase7_live_ml():
    print("=== Phase 7: Live ML + Feature Collector Test ===")

    # Initialize collector
    collector = LiveFeatureCollector()
    collector.ml_model = MLModel()  # ensure ML model is loaded

    # Load the dummy ML model
    collector.ml_model.load()

    # Simulate multiple new token events
    fake_tokens = [
        {"mint_address": "FAKE_TOKEN_1", "rug_score": 5, "safe": True, "reasons": []},
        {"mint_address": "FAKE_TOKEN_2", "rug_score": 25, "safe": False, "reasons": ["Low liquidity"]},
        {"mint_address": "FAKE_TOKEN_3", "rug_score": 10, "safe": True, "reasons": []},
        {"mint_address": "TEST_TOKEN_123", "rug_score": 15, "safe": True, "reasons": []},
    ]

    for token_event in fake_tokens:
        print(f"\n🆕 Simulating token: {token_event['mint_address']}")
        await collector.process_new_token(token_event)

        # ML prediction
        fv = collector.fe.build_feature_vector(
            token=token_event["mint_address"],
            onchain_data={"age_seconds": 0, "tx_last_min": 0},
            rug_data={"score": token_event["rug_score"], "safe": token_event["safe"], "reasons": token_event["reasons"]}
        )
        prob_safe = collector.ml_model.predict(fv)
        print(f"🤖 ML Prediction: Probability token is safe: {prob_safe:.2f}")

        if prob_safe > 0.7:
            print(f"✅ Token {token_event['mint_address']} likely safe")
        elif prob_safe < 0.3:
            print(f"❌ Token {token_event['mint_address']} likely rug")
        else:
            print(f"⚠️ Token {token_event['mint_address']} is uncertain, use caution")

async def main():
    await test_phase7_live_ml()

if __name__ == "__main__":
    asyncio.run(main())