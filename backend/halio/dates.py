"""Human-readable Indonesian dates for answers."""

MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


def human_date(iso: str) -> str:
    """'2026-11-05T09:12:00+07:00' -> '5 Nov 2026'; anything unparseable is returned as is."""
    try:
        y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
        return f"{d} {MONTHS[m - 1]} {y}"
    except (ValueError, IndexError):
        return iso
