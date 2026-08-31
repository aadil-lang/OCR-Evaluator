import re

from src.evaluation.fields import FIELD_PATTERNS
from src.evaluation.normalization import clean_value


__all__ = [
    "FIELD_PATTERNS",
    "clean_ocr_value",
    "extract_fields",
]


# Kept for backward compatibility with existing callers.
clean_ocr_value = clean_value


def extract_fields(text: str) -> dict:
    """Extract structured fields from OCR text."""

    fields = {}

    for field, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            value = match.group(1).strip()
            fields[field] = clean_ocr_value(value)
        else:
            fields[field] = ""

    return fields
