import asyncio
from core.rug_filter import RugFilter
from core.solana_client import SolanaClient


async def main():
    client = SolanaClient()
    rug_filter = RugFilter(client)

    print("🔍 Testing Rug Filter...\n")

    mint = "So11111111111111111111111111111111111111112"

    result = await rug_filter.analyze_token(mint)

    print("Result:")
    print(f"Safe: {result['safe']}")
    print(f"Score: {result['score']}")

    print("\nReasons:")
    for r in result["reasons"]:
        print(f"- {r}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())