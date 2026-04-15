def extract_charges(text: str):
    charges = {}

    for line in text.split("\n"):
        if ":" in line:
            name, value = line.split(":", 1)

            try:
                charges[name.strip()] = float(value.strip())
            except:
                continue

    return charges