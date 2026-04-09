#ml_model.py
import os
import joblib
import pandas as pd
from xgboost import XGBClassifier

class MLModel:
    def __init__(self, model_path="models/xgb_model.pkl"):
        self.model_path = model_path
        self.model = None

    def train(self, df: pd.DataFrame):
        X = df.drop(columns=["target"])
        y = df["target"]

        self.model = XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.1,
            eval_metric="logloss"
        )
        self.model.fit(X, y)

        # Ensure the folder exists
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"Model trained and saved to {self.model_path}")

    def load(self):
        self.model = joblib.load(self.model_path)
        print(f"Model loaded from {self.model_path}")

    def predict(self, feature_vector: dict):
        if self.model is None:
            self.load()
        df = pd.DataFrame([feature_vector])
        if "token" in df.columns:
            df = df.drop(columns=["token"])
        prob = self.model.predict_proba(df)[0][1]
        return prob