import json
import os
from datetime import datetime

DATA_PATH = "data/history.json"


def load_history():
    if not os.path.exists(DATA_PATH):
        return []

    with open(DATA_PATH, "r") as f:
        return json.load(f)


def save_history(charges: dict):
    history = load_history()

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "charges": charges
    }

    history.append(entry)

    os.makedirs("data", exist_ok=True)

    with open(DATA_PATH, "w") as f:
        json.dump(history, f, indent=4)