import asyncio
from core.features.live_feature_collector import LiveFeatureCollector

async def main():
    collector = LiveFeatureCollector()
    await collector.start()  # runs indefinitely, Ctrl+C to stop

if __name__ == "__main__":
    asyncio.run(main())