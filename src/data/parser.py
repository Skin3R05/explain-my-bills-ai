import re
import pdfplumber


# ── PDF Parser ────────────────────────────────────────────────────────────────

def extract_charges_from_pdf(file) -> dict:
    """
    Extract utility charges from a PDF bill.

    Scans all pages (not just the first) for table rows containing a Euro
    amount and a known utility keyword.

    Returns:
        dict with keys 'water', 'electricity', 'gas', 'total' (float values)
    """
    charges = {
        "water": 0.0,
        "electricity": 0.0,
        "gas": 0.0,
        "total": 0.0
    }

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                for row in table:
                    if not row:
                        continue

                    # Normalise row content to a single lowercase string
                    row_text = " ".join(
                        str(cell) for cell in row if cell is not None
                    ).replace("\n", " ").lower()

                    # Match European-style amounts: 50.07€ or 81,36€ or € 12.50
                    cost_match = re.search(r"(\d{1,6}[.,]\d{2})\s*€|€\s*(\d{1,6}[.,]\d{2})", row_text)
                    if not cost_match:
                        continue

                    raw = cost_match.group(1) or cost_match.group(2)
                    val = float(raw.replace(",", "."))

                    if "water" in row_text:
                        charges["water"] = val
                    elif (
                        "electricity" in row_text
                        or any(x in row_text for x in ["vazio", "ponta", "cheias"])
                    ):
                        # Keep updating — last matching row is the section sub-total
                        charges["electricity"] = val
                    elif "gas" in row_text or "gás" in row_text:
                        charges["gas"] = val
                    elif "total" in row_text and "daily" not in row_text:
                        charges["total"] = val

    return charges


# ── Plain-text Parser ─────────────────────────────────────────────────────────

def extract_charges(text: str) -> dict:
    """
    Extract charges from a plain-text bill.

    Expected line format:  <name>: <value>
    Example:               electricity: 45.30

    Returns:
        dict mapping charge name (lowercase) → float value
    """
    charges = {}
    # Accepts both integer and decimal values
    matches = re.findall(r"([A-Za-z]+):\s*([0-9]+\.?[0-9]*)", text)
    for name, value in matches:
        charges[name.lower()] = float(value)
    return charges