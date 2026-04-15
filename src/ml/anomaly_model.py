import numpy as np
from sklearn.ensemble import IsolationForest


class AnomalyModel:
    def __init__(self):
        self.model = None

    def train(self, history):
        rows = []

        for item in history:
            for _, value in item["charges"].items():
                rows.append([value])

        if len(rows) < 5:
            self.model = None
            return

        data = np.array(rows)

        self.model = IsolationForest(
            contamination=0.1,
            random_state=42
        )

        self.model.fit(data)

    def predict(self, value):
        if self.model is None:
            return "Not enough data for ML"

        result = self.model.predict([[value]])

        return "Anomaly detected" if result[0] == -1 else "Normal"