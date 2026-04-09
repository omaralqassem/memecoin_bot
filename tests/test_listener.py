import asyncio
from core.log_listener import SolanaLogListener


async def main():
    listener = SolanaLogListener()

    try:
        await listener.start()
    except KeyboardInterrupt:
        print("\n🛑 Stopping listener...")
        await listener.stop()


if __name__ == "__main__":
    asyncio.run(main())