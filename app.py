import json
import os
from datetime import datetime
from sklearn.ensemble import IsolationForest
import streamlit as st
import numpy as np

# Load history
def load_history():
    if os.path.exists("history.json"):
        with open("history.json", "r") as f:
            return json.load(f)
    return []

# Save history
def save_history(entry):
    history = load_history()
    history.append(entry)

    with open("history.json", "w") as f:
        json.dump(history, f, indent=4)

def train_model():
    # normal bill patterns (example data)
    data = np.array([
        [40], [42], [38], [41], [39],
        [10], [11], [9], [10.5],
        [5], [5.5], [4.8], [6],
        [6], [6.2], [5.8]
    ])

    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(data)

    return model

def get_previous_average(charge_name):
    fake_history = {
        "Energy Charge": 40,
        "Delivery Charge": 10,
        "Service Fee": 5,
        "Tax": 6
    }
    return fake_history.get(charge_name, 0)

model = train_model()

def detect_anomaly_ml(value):
    prediction = model.predict([[value]])

    if prediction[0] == -1:
        return "Unusual value detected (ML anomaly)"
    else:
        return "Normal pattern (ML)"

def explain_charges(name, value):
    base_meanings = {
        "Energy Charge": "This represents the cost based on your electricity usage.",
        "Delivery Charge": "This covers the infrastructure and delivery of electricity to your home.",
        "Service Fee": "This is a fixed operational and maintenance fee.",
        "Tax": "This is a government-imposed tax on your total usage.",
        "Total": "This is the final amount you need to pay."
    }

    explanation = base_meanings.get(name, "This is a billing-related charge from your provider.")

    if value > 50:
        explanation += " It is relatively high compared to typical values."
    elif value < 10:
        explanation += " It is a low-cost component of your bill."

    return explanation

def interpret_anomaly(name, value, result):
    if result == "Unusual value detected (ML anomaly)":
        return f"{result} → This charge deviates from normal patterns and may require attention."
    else:
        return f"{result} → This value is within expected billing range."

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

    st.subheader("AI Insights (Smart Engine)")

    for name, value in charges.items():
        explanation = explain_charges(name, value)
        anomaly = detect_anomaly_ml(value)
        final_anomaly = interpret_anomaly(name, value, anomaly)

        st.write(f"""
        **{name}**: €{value}
        → {explanation}
        → {final_anomaly}
        """)

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "charges": charges
    }

    save_history(entry)

    st.subheader("Bill History")

    history = load_history()

    if len(history) == 0:
        st.write("No history yet.")
    else:
        for item in reversed(history[-5:]):
            st.write(f"{item['timestamp']}")
            st.write(item["charges"])
            st.write("---")