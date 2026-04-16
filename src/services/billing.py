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
    # filter same charge history (correct column)
    charge_df = df[df["charge"] == charge_name]

    if df is None or df.empty:
        return "No historical data available for comparison."

    if charge_df.empty or len(charge_df) < 3:
        return "⚠️ Not enough historical data for reliable comparison."

    avg = charge_df["value"].mean()
    std = charge_df["value"].std()

    if avg == 0:
        return "⚠️ No baseline available for comparison."

    diff_percent = ((value - avg) / avg) * 100

    # 🔥 NEW: spike detection using variability (IMPORTANT FIX)
    if std > 0 and value > avg + 2 * std:
        return (
            f"🔴 Unusual spike detected. "
            f"Typical: €{avg:.2f}, now: €{value:.2f}."
        )

    # normal range
    if abs(diff_percent) <= 15:
        return f"🟢 Value is consistent with your usual pattern (avg €{avg:.2f})."

    # moderate anomaly
    elif 15 < diff_percent <= 40:
        return f"🟡 Higher than usual by {diff_percent:.1f}% (avg €{avg:.2f})."

    elif -40 <= diff_percent < -15:
        return f"🟡 Lower than usual by {abs(diff_percent):.1f}% (avg €{avg:.2f})."

    # strong anomaly
    elif diff_percent > 40:
        return f"🔴 Significantly higher than average (+{diff_percent:.1f}%) → avg €{avg:.2f}."

    else:
        return f"🔵 Significantly lower than average ({abs(diff_percent):.1f}%) → avg €{avg:.2f}."