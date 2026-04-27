from enum import StrEnum


class ThreadType(StrEnum):
    """Thread profile types with their calculation formulas."""
    ISO_METRIC = "ISO Metric"
    UNIFIED = "Unified"
    WHITWORTH = "Whitworth"
    ACME = "ACME"
