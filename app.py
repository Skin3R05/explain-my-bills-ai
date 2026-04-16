import streamlit as st

from src.services.billing import explain_anomaly_reason
from src.data.database import load_df
from src.data.database import init_db, save_charges, load_history
from src.services.analytics import history_to_df
import pandas as pd
from src.data.parser import extract_charges
from src.ml.anomaly_model import AnomalyModel
from src.services.billing import explain_charge, interpret_anomaly

init_db()

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Explain My Bill AI",
    layout="wide",
    page_icon="💡"
)

st.title("💡 Explain My Bill AI")
st.caption("AI-powered bill insights, anomaly detection & spending intelligence")

# ================= UPLOAD =================
uploaded_file = st.file_uploader("📄 Upload your bill (.txt)", type=["txt"])

model = AnomalyModel()

history = load_history()
model.train(history)

# ================= UTIL: ANOMALY BADGE =================
def anomaly_badge(val):
    if val == -1:
        return "🔴 Anomaly"
    return "🟢 Normal"

# ================= MAIN =================
if uploaded_file:

    content = uploaded_file.read().decode("utf-8")

    st.subheader("📜 Raw Bill")
    st.code(content)

    charges = extract_charges(content)

    st.subheader("📊 AI Insights Dashboard")

    df_all = load_df()

    total_bill = sum(charges.values())

    for name, value in charges.items():

        explanation = explain_charge(name, value)
        anomaly = model.predict(value)
        final = interpret_anomaly(anomaly)
        reason = explain_anomaly_reason(df_all, name, value)

        percent = (value / total_bill) * 100 if total_bill else 0

        with st.expander(f"🧾 {name} — €{value} ({percent:.1f}%)"):

            col1, col2 = st.columns([1, 2])

            with col1:
                st.metric("Amount", f"€{value}")
                st.progress(min(percent / 100, 1.0))

                st.markdown(f"### {anomaly_badge(anomaly)}")

            with col2:
                st.markdown("#### 🧠 Explanation")
                st.write(explanation)

                st.markdown("#### 🚨 Status")
                st.write(final)

                st.markdown("#### 💡 AI Reasoning")
                st.info(reason)

# ================= HISTORY =================
st.markdown("---")
st.subheader("🕘 Recent Billing History")

for item in reversed(history[-5:]):
    st.json(item)
    st.markdown("---")

# ================= ANALYTICS =================
st.markdown("---")
st.subheader("📈 Spending Analytics Dashboard")

history = load_history()

if len(history) > 0:

    df = history_to_df(history, model)

    if not df.empty:

        df["date"] = df["timestamp"].dt.date

        daily = df.groupby("date").agg({
            "value": "sum",
            "anomaly": "min"
        }).reset_index()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 Daily Spending Trend")
            st.line_chart(daily.set_index("date")["value"])

        with col2:
            st.markdown("### ⚠️ Anomaly Overview")
            anomalies = daily[daily["anomaly"] == -1]

            if not anomalies.empty:
                st.dataframe(anomalies)
            else:
                st.success("No anomalies detected 🎉")

else:
    st.info("No data available yet. Upload a bill to start 🚀")