import re
from difflib import SequenceMatcher


FIELD_LABELS = {
    "owner_name": "Owner Name",
    "father_name": "Father Name",
    "survey_number": "Survey Number",
    "area": "Area",
    "village": "Village",
    "tehsil": "Tehsil",
    "district": "District",
    "registration_number": "Registration Number",
}


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def check_value_supported(
    value: str,
    source_text: str,
    threshold: float = 0.85,
) -> dict:
    """Check whether an extracted value is supported by source text."""

    normalized_value = normalize_text(value)
    normalized_source = normalize_text(source_text)

    if not normalized_value:
        return {
            "supported": False,
            "similarity": 0.0,
        }

    if normalized_value in normalized_source:
        return {
            "supported": True,
            "similarity": 1.0,
        }

    similarity = SequenceMatcher(
        None,
        normalized_value,
        normalized_source,
    ).ratio()

    return {
        "supported": similarity >= threshold,
        "similarity": similarity,
    }


def _extract_source_field_value(
    field: str,
    source_text: str,
) -> str:
    """Extract the value associated with a known field label."""

    label = FIELD_LABELS.get(field)

    if not label:
        return ""

    pattern = rf"^\s*{re.escape(label)}\s*:\s*(.+?)\s*$"

    match = re.search(
        pattern,
        source_text,
        re.IGNORECASE | re.MULTILINE,
    )

    if not match:
        return ""

    return match.group(1).strip()


def check_field_supported(
    field: str,
    value: str,
    source_text: str,
    threshold: float = 0.85,
) -> dict:
    """Check whether a field value is supported by its own source field."""

    source_value = _extract_source_field_value(
        field,
        source_text,
    )

    if not source_value or not value:
        return {
            "supported": False,
            "similarity": 0.0,
            "source_value": source_value,
        }

    normalized_value = normalize_text(value)
    normalized_source_value = normalize_text(source_value)

    if normalized_value == normalized_source_value:
        return {
            "supported": True,
            "similarity": 1.0,
            "source_value": source_value,
        }

    similarity = SequenceMatcher(
        None,
        normalized_value,
        normalized_source_value,
    ).ratio()

    return {
        "supported": similarity >= threshold,
        "similarity": similarity,
        "source_value": source_value,
    }


def detect_unsupported_fields(
    extracted_fields: dict,
    source_text: str,
) -> dict:
    """Detect extracted values that are not supported by their source fields."""

    results = {}

    for field, value in extracted_fields.items():
        results[field] = check_field_supported(
            field,
            value,
            source_text,
        )

    return results