import pandas as pd


def explain_charge(name: str, value: float) -> str:
    """Return a human-readable label for a charge line item."""
    return f"{name.title()} charge recorded as €{value:.2f}."


def interpret_anomaly(anomaly: str) -> str:
    """Convert a model prediction string into a display label."""
    if anomaly == "Anomaly detected":
        return "🔴 Anomaly detected"
    if anomaly == "Not enough data for ML":
        return "⚪ Insufficient history"
    return "🟢 Normal pattern"


def explain_anomaly_reason(df: pd.DataFrame, charge_name: str, value: float) -> str:
    """
    Generate a plain-language explanation comparing `value` against
    the historical average for `charge_name`.
    """
    if df is None or df.empty:
        return "⚠️ No historical data available for comparison."

    if "charge" not in df.columns or "value" not in df.columns:
        return "⚠️ Invalid dataset format."

    charge_df = df[df["charge"] == charge_name]

    if len(charge_df) < 3:
        return "⚠️ Not enough historical data for comparison (need at least 3 records)."

    avg = charge_df["value"].mean()
    std = charge_df["value"].std()

    if avg == 0:
        return "⚠️ No baseline available — historical average is zero."

    diff_percent = ((value - avg) / avg) * 100

    # Spike: more than 2 standard deviations above mean
    if std > 0 and value > avg + 2 * std:
        return (
            f"🔴 Unusual spike detected for {charge_name.title()}. "
            f"Typical: €{avg:.2f}, current: €{value:.2f} "
            f"(+{diff_percent:.1f}% above average)."
        )

    if abs(diff_percent) <= 15:
        return f"🟢 {charge_name.title()} is consistent with your usual pattern (avg €{avg:.2f})."

    if 15 < diff_percent <= 40:
        return (
            f"🟡 {charge_name.title()} is moderately higher than usual "
            f"(+{diff_percent:.1f}% vs avg €{avg:.2f})."
        )

    if -40 <= diff_percent < -15:
        return (
            f"🟡 {charge_name.title()} is moderately lower than usual "
            f"({diff_percent:.1f}% vs avg €{avg:.2f})."
        )

    if diff_percent > 40:
        return (
            f"🔴 Significant increase for {charge_name.title()} "
            f"(+{diff_percent:.1f}% vs avg €{avg:.2f})."
        )

    # diff_percent < -40
    return (
        f"🔵 Significant decrease for {charge_name.title()} "
        f"({diff_percent:.1f}% vs avg €{avg:.2f})."
    )