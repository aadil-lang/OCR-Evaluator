import re


FIELD_PATTERNS = {
    "owner_name": r"Owner Name\s*:\s*(.+)",
    "father_name": r"Father Name\s*:\s*(.+)",
    "survey_number": r"Survey Number\s*:\s*(.+)",
    "area": r"Area\s*:\s*(.+)",
    "village": r"Village\s*:\s*(.+)",
    "tehsil": r"Tehsil\s*:\s*(.+)",
    "district": r"District\s*:\s*(.+)",
    "registration_number": r"Registration Number\s*:\s*(.+)",
}


def extract_fields(text: str) -> dict:
    """Extract structured fields from OCR text."""

    fields = {}

    for field, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            fields[field] = match.group(1).strip()
        else:
            fields[field] = ""

    return fields
