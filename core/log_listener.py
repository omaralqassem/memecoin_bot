import asyncio
import json
import websockets
from typing import Dict, Any

from config.settings import settings
from core.token_detector import TokenDetector
from core.solana_client import SolanaClient
from core.parsers.transaction_parser import extract_mint_and_wallet

class SolanaLogListener:
    def __init__(self, event_callback=None):
        # Convert HTTPS RPC to WSS
        self.rpc_ws_url = settings.SOLANA_RPC_URL.replace("https", "wss")
        self.detector = TokenDetector()
        self.solana_client = SolanaClient()
        
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
            "params": ["all", {"commitment": "processed"}]
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
                        continue

                    mint_address, _ = extract_mint_and_wallet(tx)
                    if not mint_address:
                        continue

                    if self.event_callback:
                        structured_event = {
                            "mint_address": mint_address,
                            "signature": signature,
                            "tx_count": 1 # Initial state
                        }
                        asyncio.create_task(self.event_callback(structured_event))
                        print(f"🎯 New Token detected: {mint_address[:8]}... Sent for audit.")

            except Exception as e:
                print(f"⚠️ Listener Processing error: {e}")
            finally:
                self.queue.task_done()

    async def start(self):
        await asyncio.gather(
            self.connect(),
            self.process_events()
        )

    async def stop(self):
        self.running = False
        await self.solana_client.close()