#telegram_listener.py
import asyncio
from telethon import TelegramClient, events
from config.settings import settings
from core.social.sentiment_engine import SentimentEngine


class TelegramListener:
    def __init__(self):
        self.client = TelegramClient(
            "session",
            settings.TELEGRAM_API_ID,
            settings.TELEGRAM_API_HASH
        )

        self.engine = SentimentEngine()

    async def start(self):
        await self.client.start()
        print("📡 Telegram listener started")

        @self.client.on(events.NewMessage)
        async def handler(event):
            try:
                text = event.raw_text

                if not text:
                    return

                if "$" in text or "CA:" in text or "contract" in text.lower():

                    print(f"\n📢 TG: {text[:120]}")

                    self.engine.process(text)

                    self.print_trending()

            except Exception as e:
                print(f"⚠️ Telegram error: {e}")

        await self.client.run_until_disconnected()

    def print_trending(self):
        print("\n📊 TRENDING TOKENS:")

        for token in list(self.engine.mentions.keys()):
            score = self.engine.get_score(token)

            if score >= 2:
                print(f"🔥 {token}: {score}")