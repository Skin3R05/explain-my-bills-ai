import streamlit as st

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

    st.subheader("Explained Bill")

    for name, value in charges.items():
        explanation = explain_charges(name)
        st.write(f"{name}: €{value} → {explanation}")