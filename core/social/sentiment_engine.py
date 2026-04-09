import time
from core.database import Database

class SentimentEngine:
    def __init__(self, db: Database):
        self.db = db

    def process(self, text: str):
        tokens = self.extract_tokens(text)
        for token in tokens:
            self.db.add_hype_mention(token)

    def extract_tokens(self, text: str):
        words = text.replace("\n", " ").split(" ")
        found = []
        for w in words:
            if w.startswith("$"):
                found.append(w.upper())
            elif len(w) > 30:
                found.append(w)
        return found