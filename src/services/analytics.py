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

    if model and model.model is not None:
        df["anomaly"] = df["value"].apply(
            lambda x: model.model.predict([[x]])[0]
        )
    else:
        df["anomaly"] = 1 # default normal

    return df