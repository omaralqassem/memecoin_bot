#log_listener.py
import asyncio
import json
import websockets
from typing import Dict, Any

from config.settings import settings
from core.features.feature_engine import FeatureEngine
from core.token_detector import TokenDetector
from core.rug_filter import RugFilter
from core.solana_client import SolanaClient
from core.features.token_state_manager import TokenStateManager
from core.parsers.transaction_parser import extract_mint_and_wallet


class SolanaLogListener:
    def __init__(self, event_callback=None):
        self.rpc_ws_url = settings.SOLANA_RPC_URL.replace("https", "wss")
        self.fe = FeatureEngine()
        self.detector = TokenDetector()
        self.solana_client = SolanaClient()
        self.rug_filter = RugFilter(self.solana_client)

        self.state_manager = TokenStateManager()

        self.queue: asyncio.Queue = asyncio.Queue(maxsize=10000)
        self.running = True

        self.event_callback = event_callback

    async def connect(self):
        while self.running:
            try:
                async with websockets.connect(
                    self.rpc_ws_url,
                    ping_interval=20,
                    close_timeout=5
                ) as ws:
                    print("🔌 Connected to Solana WebSocket")

                    await self.subscribe(ws)
                    await self.receive_loop(ws)

            except Exception as e:
                print(f"⚠️ Connection error: {e}")
                print("🔄 Reconnecting in 2 seconds...")
                await asyncio.sleep(2)

    async def subscribe(self, ws):
        msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "logsSubscribe",
            "params": [
                "all",
                {"commitment": "processed"}
            ]
        }
        await ws.send(json.dumps(msg))

    async def receive_loop(self, ws):
        while self.running:
            message = await ws.recv()
            data = json.loads(message)

            if data.get("method") == "logsNotification":
                logs_data = data["params"]["result"]["value"]
                await self.enqueue_event(logs_data)

    async def enqueue_event(self, logs_data: Dict[str, Any]):
        try:
            self.queue.put_nowait(logs_data)
        except asyncio.QueueFull:
            print("⚠️ Queue full — dropping event")

    async def process_events(self):
        while self.running:
            logs_data = await self.queue.get()
            try:
                signature = logs_data.get("signature")
                log_messages = logs_data.get("logs", [])
                event = self.detector.detect_event(log_messages)

                if event and event["type"] == "LIQUIDITY_ADDED":
                    tx = await self.solana_client.get_transaction(signature)
                    if not tx:
                        self.queue.task_done()
                        continue

                    # Extract mint + wallet first
                    mint_address, wallet = extract_mint_and_wallet(tx)
                    if not mint_address or not wallet:
                        self.queue.task_done()
                        continue

                    # Token state
                    state = self.state_manager.get_or_create(mint_address)
                    state.add_transaction(wallet)
                    state.add_liquidity_event()

                    # Skip tiny liquidity pools if needed
                    if len(state.wallets) < 2:
                        self.queue.task_done()
                        continue

                    # Rug filter
                    rug = await self.rug_filter.analyze_token(mint_address)

                    # Hype & feature vector
                    mentions, contract_mentions = self.fe.get_hype_score(mint_address)
                    fv = self.fe.build_feature_vector(
                        token=mint_address,
                        onchain_data={
                            "age_seconds": state.get_age(),
                            "tx_last_min": state.get_tx_count_1m()
                        },
                        rug_data={
                            "score": rug["score"],
                            "safe": rug["safe"],
                            "reasons": rug.get("reasons", [])
                        }
                    )

                    # Print feature vector
                    print("\n📊 Live Feature Vector:")
                    for k, v in fv.items():
                        print(f"{k}: {v}")

                    # Structured event
                    structured_event = {
                        "type": event["type"],
                        "confidence": event["confidence"],
                        "signature": signature,
                        "mint_address": mint_address,
                        "safe": rug["safe"],
                        "rug_score": rug["score"],
                        "reasons": rug.get("reasons", []),
                    }

                    if self.event_callback:
                        asyncio.create_task(self.event_callback(structured_event))

                    self.handle_event(structured_event)

                    # Print live stats
                    print("\n📊 LIVE FEATURES:")
                    print(f"token: {mint_address}")
                    print(f"tx_count_last_min: {state.get_tx_count_1m()}")
                    print(f"unique_wallets_last_min: {state.get_unique_wallets_1m()}")
                    print(f"hype_mentions_last_5min: {state.get_mentions_5m()}")
                    print(f"token_age_seconds: {state.get_age()}")

            except Exception as e:
                print(f"⚠️ Processing error: {e}")
            finally:
                self.queue.task_done()

    def handle_event(self, event: Dict[str, Any]):
        print("\n🔥 EVENT DETECTED")
        print(f"   Type: {event['type']}")
        print(f"   Confidence: {event['confidence']}")
        print(f"   Safe: {event['safe']}")
        print(f"   Rug Score: {event['rug_score']}")
        print(f"   Tx: {event['signature']}")
        if event["reasons"]:
            print("   ⚠️ Reasons:")
            for r in event["reasons"]:
                print(f"      - {r}")

    async def start(self):
        await asyncio.gather(
            self.connect(),
            self.process_events()
        )

    async def stop(self):
        self.running = False
        await self.solana_client.close()