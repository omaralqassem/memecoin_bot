#token_detector.py
from typing import Dict, Any, Optional


class TokenDetector:
    def __init__(self):
        self.keywords = {
            "mint": "InitializeMint",
            "liquidity": ["AddLiquidity", "InitializePool"],
            "swap": "Swap"
        }

    def detect_event(self, logs: list) -> Optional[Dict[str, Any]]:

        event = {
            "type": None,
            "confidence": 0,
        }

        for log in logs:
            if self.keywords["mint"] in log:
                event["type"] = "NEW_TOKEN"
                event["confidence"] = 0.6

            for keyword in self.keywords["liquidity"]:
                if keyword in log:
                    event["type"] = "LIQUIDITY_ADDED"
                    event["confidence"] = 0.9

            if self.keywords["swap"] in log:
                event["type"] = "SWAP"
                event["confidence"] = 0.5

        if event["type"]:
            return event

        return None