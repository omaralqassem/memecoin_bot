import asyncio
from core.social.twitter_listener import TwitterListener
from core.social.sentiment_engine import SentimentEngine


async def main():
    twitter = TwitterListener("memecoin OR solana")
    engine = SentimentEngine()

    while True:
        tweets = await twitter.fetch_mentions()

        for t in tweets:
            engine.process(t["content"])

        print("\n📊 Trending Tokens:")

        for token in list(engine.mentions.keys()):
            score = engine.get_score(token)
            if score > 2:
                print(f"{token}: {score}")

        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())