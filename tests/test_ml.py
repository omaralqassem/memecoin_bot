import asyncio
from core.features.live_feature_collector import LiveFeatureCollector

async def test_ml_phase():
    collector = LiveFeatureCollector()

    fake_event = {
        "mint_address": "TEST_TOKEN_123",
        "rug_score": 10,
        "safe": True,
        "reasons": []
    }

    await collector.process_new_token(fake_event)

asyncio.run(test_ml_phase())