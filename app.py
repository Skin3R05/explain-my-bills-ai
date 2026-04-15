from sklearn.ensemble import IsolationForest
import streamlit as st
import numpy as np

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

    st.subheader("AI Insights (ML Anomaly Detection)")

    for name, value in charges.items():
        explanation = explain_charges(name)
        anomaly = detect_anomaly_ml(value)

        st.write(f"""
        **{name}**: €{value}
        → {explanation}
        → {anomaly}
        """)