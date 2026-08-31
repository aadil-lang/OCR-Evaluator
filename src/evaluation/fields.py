"""Shared field schema for the 8 evaluated document fields.

This is the single source of truth for field keys, display labels,
risk severity, critical-field membership, and OCR extraction
patterns. All evaluation modules import from here instead of
redeclaring their own copies.
"""

import re


# Display labels as they appear in the documents.
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


# Risk severity per field. CRITICAL mismatches cause FAIL,
# HIGH mismatches cause REVIEW, NORMAL mismatches cause REVIEW
# as well but are lower-priority signals.
FIELD_SEVERITY = {
    "owner_name": "CRITICAL",
    "father_name": "HIGH",
    "survey_number": "CRITICAL",
    "area": "CRITICAL",
    "village": "HIGH",
    "tehsil": "HIGH",
    "district": "HIGH",
    "registration_number": "CRITICAL",
}


# Fields whose mismatch always fails the document, regardless
# of other signals.
CRITICAL_FIELDS = {
    "owner_name",
    "survey_number",
    "area",
    "registration_number",
}


# OCR confidence thresholds shared by risk assessment and
# confidence/correctness analysis.
LOW_CONFIDENCE_THRESHOLD = 60.0
HIGH_CONFIDENCE_THRESHOLD = 85.0


def build_field_patterns() -> dict:
    """Build OCR extraction patterns for all known fields.

    The pattern matches a field label followed by a colon and
    captures the value on the same line. It is used with
    re.IGNORECASE (no MULTILINE anchor) so a label may appear
    anywhere in the text.
    """

    return {
        field: rf"{re.escape(label)}\s*:\s*(.+)"
        for field, label in FIELD_LABELS.items()
    }


def anchored_field_pattern(field: str) -> str:
    """Build the anchored pattern for line-based source extraction.

    Used with re.IGNORECASE | re.MULTILINE to read a field's
    value from its own ``Label: value`` line in the OCR text.
    """

    label = FIELD_LABELS.get(field)

    if not label:
        return ""

    return rf"^\s*{re.escape(label)}\s*:\s*(.+?)\s*$"


# Precomputed extraction patterns for the extractor.
FIELD_PATTERNS = build_field_patterns()
