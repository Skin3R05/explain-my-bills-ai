import pandas as pd


def history_to_df(history):
    rows = []

    for item in history:
        timestamp = item["timestamp"]

        for name, value in item["charges"].items():
            rows.append({
                "timestamp": timestamp,
                "charge": name,
                "value": value
            })

    return pd.DataFrame(rows)