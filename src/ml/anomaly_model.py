import numpy as np
from sklearn.ensemble import IsolationForest


class AnomalyModel:
    def __init__(self):
        self.model = None

    def train(self, history: list) -> None:
        """Train the IsolationForest model on all charge values from history."""
        rows = []

        for item in history:
            for key, value in item["charges"].items():
                # Exclude synthetic 'total' key to avoid skewing the model
                if key != "total":
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

    def predict(self, value: float) -> str:
        """
        Predict whether a single charge value is an anomaly.
        Returns: 'Anomaly detected' | 'Normal' | 'Not enough data for ML'
        """
        if self.model is None:
            return "Not enough data for ML"

        result = self.model.predict([[value]])
        return "Anomaly detected" if result[0] == -1 else "Normal"