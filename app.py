import streamlit as st

from src.services.analytics import history_to_df
import pandas as pd
from src.data.storage import load_history, save_history
from src.data.parser import extract_charges
from src.ml.anomaly_model import AnomalyModel
from src.services.billing import explain_charge, interpret_anomaly

st.title("Explain My Bill AI")

uploaded_file = st.file_uploader("Upload bill (.txt)", type=["txt"])

model = AnomalyModel()

history = load_history()
model.train(history)

if uploaded_file:

    content = uploaded_file.read().decode("utf-8")
    st.write("### Raw Bill")
    st.write(content)

    charges = extract_charges(content)

    st.write("### Insights")

    for name, value in charges.items():

        explanation = explain_charge(name, value)
        anomaly = model.predict(value)
        final = interpret_anomaly(anomaly)

        st.write(f"""
        **{name}: €{value}**

        {explanation}

        {final}
        """)

    save_history(charges)

    st.success("Saved to history!")

# History
st.write("## Last 5 Records")

for item in reversed(history[-5:]):
    st.write(item)
    st.write("---")

# Analytics
st.write("## Analytics Dashboard")

history = load_history()

if len(history) > 0:

    df = history_to_df(history, model)

    if not df.empty:
        df["date"] = df["timestamp"].dt.date

        # Aggregate total per day
        daily = df.groupby("date").agg({
            "value": "sum",
            "anomaly": "min"  # if any anomaly exists that day → mark it
        }).reset_index()

        st.write("### Spending Over Time (Anomalies Highlighted)")

        # Split normal vs anomaly
        normal = daily[daily["anomaly"] == 1]
        anomaly = daily[daily["anomaly"] == -1]

        st.line_chart(normal.set_index("date")["value"])

        if not anomaly.empty:
            st.write("Anomalies detected on these dates:")
            st.dataframe(anomaly)

else:
    st.write("No data available yet.")