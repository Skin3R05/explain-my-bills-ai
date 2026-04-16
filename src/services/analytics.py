import pandas as pd


def history_to_df(history, model=None):

    # =========================
    # EMPTY SAFETY
    # =========================
    if not history:
        return pd.DataFrame(columns=["timestamp", "charge", "value", "anomaly"])

    rows = []

    # =========================
    # FLATTEN HISTORY
    # =========================
    for item in history:
        timestamp = item["timestamp"]

        for name, value in item["charges"].items():
            rows.append({
                "timestamp": timestamp,
                "charge": name,
                "value": value
            })

    df = pd.DataFrame(rows)

    if df.empty:
        return pd.DataFrame(columns=["timestamp", "charge", "value", "anomaly"])

    # =========================
    # TYPE FIXES
    # =========================
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # =========================
    # DEFAULT ANOMALY
    # =========================
    df["anomaly"] = 1  # normal

    # =========================
    # ML ANOMALY DETECTION (SAFE)
    # =========================
    if model and hasattr(model, "model") and model.model is not None:

        for charge_type in df["charge"].unique():

            subset = df[df["charge"] == charge_type]

            # need enough data to be meaningful
            if len(subset) < 5:
                continue

            values = subset["value"].values.reshape(-1, 1)

            preds = model.model.fit_predict(values)

            df.loc[subset.index, "anomaly"] = preds

    return df