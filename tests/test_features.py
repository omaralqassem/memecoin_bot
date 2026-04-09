import asyncio
from core.features.feature_engine import FeatureEngine

async def main():
    fe = FeatureEngine()

    fe.process_social("$DOGEAI")
    fe.process_social("$DOGEAI")
    fe.process_social("$DOGEAI", is_contract=True)

    onchain_data = {"age_seconds": 120, "tx_last_min": 5}
    rug_data = {"score": -10}

    fv = fe.build_feature_vector("$DOGEAI", onchain_data, rug_data)

    print("\n📊 Feature Vector:")
    for k, v in fv.items():
        print(f"{k}: {v}")

    # Convert to DataFrame
    df = fe.to_dataframe([fv])
    print("\n📊 DataFrame:")
    print(df)

if __name__ == "__main__":
    asyncio.run(main())