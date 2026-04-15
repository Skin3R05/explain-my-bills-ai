import streamlit as st
import numpy as np

def get_previous_average(charge_name):
    fake_history = {
        "Energy Charge": 40,
        "Delivery Charge": 10,
        "Service Fee": 5,
        "Tax": 6
    }
    return fake_history.get(charge_name, 0)

def detect_anomaly(name, current_value):
    previous_avg = get_previous_average(name)

    if previous_avg == 0:
        return "No reference data"

    change = ((current_value - previous_avg) / previous_avg) * 100

    if change > 20:
        return f"High increase (+{change:.1f}%)"
    elif change < -20:
        return f"Unusually low ({change:1f}%)"
    else:
        return f"Normal ({change:.1f}%)"

def explain_charges(name):
    explanations = {
        "Energy Charge": "Cost of electricity you used.",
        "Delivery Charge": "Cost of delivering electricity to your home.",
        "Service Fee": "Fixed service/maintenance fee.",
        "Tax": "Government tax applied to your bill.",
        "Total": "Total amount you need to pay."
    }

    return explanations.get(name, "No explanations available.")

def extract_charges(text):
    charges = {}

    lines = text.split("\n")

    for line in lines:
        if ":" in line:
            parts = line.split(":")

            name = parts[0].strip()
            value = parts[1].strip()

            try:
                charges[name] = float(value)
            except:
                pass

    return charges

st.title("Explain My Bill AI")
st.write("Upload your bill file below")

uploaded_file = st.file_uploader("Upload your bill (.txt)", type=["txt"])

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")

    st.subheader("Raw Bill Content")
    st.write(content)

    charges = extract_charges(content)

    st.subheader("AI Insights (Anomaly Detection)")

    for name, value in charges.items():
        explanation = explain_charges(name)
        anomaly = detect_anomaly(name, value)

        st.write(f"""
        **{name}**: €{value}
        → {explanation}
        → {anomaly}
        """)