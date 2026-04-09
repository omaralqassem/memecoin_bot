import asyncio
from core.social.telegram_listener import TelegramListener

async def main():
    print("🚀 Starting Telegram Social Test...\n")
    
    listener = TelegramListener()
    
    try:
        await asyncio.wait_for(listener.start(), timeout=60)  
    except asyncio.TimeoutError:
        print("\n⏱️ Test finished after 60 seconds")

if __name__ == "__main__":
    asyncio.run(main())