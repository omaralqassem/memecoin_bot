import asyncio
from core.log_listener import SolanaLogListener
from core.features.live_feature_collector import LiveFeatureCollector

async def main():
    print("--- 🚀 SOLANA ALPHA ADVISOR STARTING ---")
    
    collector = LiveFeatureCollector()
    

    listener = SolanaLogListener(event_callback=collector.process_new_token)
    
    print("🔌 Connecting to WebSocket... Watching for New Pairs.")
    try:
        await listener.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down safely...")

if __name__ == "__main__":
    asyncio.run(main())