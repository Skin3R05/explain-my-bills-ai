def explain_charge(name, value):
    base = {
        "Energy Charge": "Cost based on electricity usage.",
        "Delivery Charge": "Infrastructure and delivery cost.",
        "Service Fee": "Operational maintenance fee.",
        "Tax": "Government tax on usage."
    }

    text = base.get(name, "Billing-related charge.")

    if value > 50:
        text += " High compared to normal."
    elif value < 10:
        text += " Low-cost component."

    return text


def interpret_anomaly(result):
    if "Anomaly" in result:
        return result + " → Needs attention."
    return result + " → Within expected range."