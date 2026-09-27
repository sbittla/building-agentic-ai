"""Interlude (testing): a small module to practise tests on."""

def apply_discount(amount: float, percent: float) -> float:
    """Reduce amount by percent (0-100). Rejects impossible percentages."""
    if not 0 <= percent <= 100:
        raise ValueError(f"percent must be between 0 and 100, got {percent}")
    return round(amount * (1 - percent / 100), 2)

def parse_price(text: str) -> float:
    """'$1,299.50' -> 1299.5"""
    cleaned = text.replace("$", "").replace(",", "").strip()
    return float(cleaned)

def save_receipt(path, lines: list[str]) -> int:
    """Write receipt lines to a file; return how many were written."""
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return len(lines)
