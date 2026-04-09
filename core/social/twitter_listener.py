#telegram_listener.py

import asyncio
import snscrape.modules.twitter as sntwitter
from typing import List


class TwitterListener:
    def __init__(self, query: str):
        self.query = query
        self.running = True

    async def fetch_mentions(self) -> List[dict]:
  
        tweets = []

        for tweet in sntwitter.TwitterSearchScraper(self.query).get_items():
            tweets.append({
                "content": tweet.content,
                "user": tweet.user.username,
                "date": tweet.date
            })

            if len(tweets) >= 20:  # limit for speed
                break

        return tweets

    async def stream(self):
        while self.running:
            try:
                tweets = await self.fetch_mentions()

                for t in tweets:
                    print(f"\n🐦 {t['user']}: {t['content'][:100]}")

                await asyncio.sleep(10)

            except Exception as e:
                print(f"⚠️ Twitter error: {e}")
                await asyncio.sleep(5)