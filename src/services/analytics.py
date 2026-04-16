import pandas as pd


def history_to_df(history, model=None):
    rows = []

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
        return df

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # 🔥 Per-charge anomaly detection
    df["anomaly"] = 1  # default normal

    if model and model.model is not None:

        for charge_type in df["charge"].unique():

            subset = df[df["charge"] == charge_type]

            values = subset["value"].values.reshape(-1, 1)

            if len(values) >= 5:  # need enough data

                model.model.fit(values)  # train per charge

                preds = model.model.predict(values)

                df.loc[subset.index, "anomaly"] = preds

    return df