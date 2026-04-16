import pandas as pd
import numpy as np


def history_to_df(history: list, model=None) -> pd.DataFrame:
    """
    Convert structured bill history into a flat DataFrame.
    Optionally annotates each row with anomaly predictions.

    Returns columns: timestamp, charge, value, anomaly
    """
    EMPTY = pd.DataFrame(columns=["timestamp", "charge", "value", "anomaly"])

    if not history:
        return EMPTY

    rows = []
    for item in history:
        timestamp = item["timestamp"]
        for name, value in item["charges"].items():
            if name != "total":
                rows.append({
                    "timestamp": timestamp,
                    "charge": name,
                    "value": value
                })

    if not rows:
        return EMPTY

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["anomaly"] = 1  # default = normal

    # get inner model
    inner = getattr(model, "model", None)

    # ✅ FIX: proper check for IsolationForest readiness
    if inner is None or not hasattr(inner, "offset_"):
        return df

    for charge_type in df["charge"].unique():
        subset = df[df["charge"] == charge_type]

        if len(subset) < 5:
            continue

        values = subset["value"].values.reshape(-1, 1)

        try:
            preds = inner.predict(values)
            df.loc[subset.index, "anomaly"] = preds
        except Exception:
            continue

    return df