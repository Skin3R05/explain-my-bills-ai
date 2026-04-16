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

def explain_anomaly_reason(df, charge_name, value):
    # filter same charge history
    charge_df = df[df["charge_name"] == charge_name]

    if len(charge_df) < 3:
        return "Not enough historical data for comparison."

    avg = charge_df["value"].mean()

    if avg == 0:
        return "No baseline available."

    diff_percent = ((value - avg) / avg) * 100

    if abs(diff_percent) < 20:
        return "Value is close to your usual pattern."

    elif diff_percent > 0:
        return f"{charge_name} is {diff_percent:.1f}% higher than your average (€{avg:.2f})."

    else:
        return f"{charge_name} is {abs(diff_percent):.1f}% lower than your average (€{avg:.2f})."