import re

INCOME_KEYWORDS = [
    "gaji", "salary", "bonus", "income", "masuk"
]

def parse_amount(text: str) -> int:
    """
    Support:
    25000
    25k
    1jt
    1 juta
    """
    text = text.lower().replace(".", "").strip()

    match = re.search(r"(\d+(?:\.\d+)?)\s*(k|rb|jt|juta)?", text)
    if not match:
        raise ValueError("No amount found")

    value = float(match.group(1))
    unit = match.group(2)

    if unit in ("k", "rb"):
        value *= 1_000
    elif unit in ("jt", "juta"):
        value *= 1_000_000

    return int(value)


def parse_transaction(text: str) -> dict:
    amount = parse_amount(text)

    # remove amount part from text
    title = re.sub(r"\d+(?:\.\d+)?\s*(k|rb|jt|juta)?", "", text, flags=re.I)
    title = title.strip()

    if not title:
        raise ValueError("Empty title")

    tx_type = "expense"
    for kw in INCOME_KEYWORDS:
        if kw in title.lower():
            tx_type = "income"
            break

    return {
        "title": title,
        "amount": amount,
        "type": tx_type
    }
