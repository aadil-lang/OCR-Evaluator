"""Regression tests for the shared field schema.

The 8 document fields are defined once in
``src/evaluation/fields.py``. These tests guard against the
old failure mode where each module redeclared its own copy
and the copies drifted apart.
"""

import re

from src.evaluation import fields
from src.evaluation.critical_fields import (
    CRITICAL_FIELDS as CRITICAL_FIELDS_CONSUMER,
)
from src.evaluation.extractor import (
    FIELD_PATTERNS as EXTRACTOR_PATTERNS,
)
from src.evaluation.evaluator import (
    FIELD_LABELS as EVALUATOR_LABELS,
)
from src.evaluation.risk import (
    FIELD_SEVERITY as RISK_SEVERITY,
    LOW_CONFIDENCE_THRESHOLD as RISK_THRESHOLD,
)
from src.evaluation.confidence_analysis import (
    LOW_CONFIDENCE_THRESHOLD as ANALYSIS_THRESHOLD,
)


EXPECTED_FIELDS = {
    "owner_name",
    "father_name",
    "survey_number",
    "area",
    "village",
    "tehsil",
    "district",
    "registration_number",
}


def test_schema_covers_all_document_fields():
    assert set(fields.FIELD_LABELS) == EXPECTED_FIELDS
    assert set(fields.FIELD_SEVERITY) == EXPECTED_FIELDS
    assert set(fields.FIELD_PATTERNS) == EXPECTED_FIELDS


def test_severities_are_valid():
    allowed = {"CRITICAL", "HIGH", "NORMAL"}

    for severity in fields.FIELD_SEVERITY.values():
        assert severity in allowed


def test_critical_fields_are_critical_severity():
    assert fields.CRITICAL_FIELDS <= set(fields.FIELD_SEVERITY)

    for field in fields.CRITICAL_FIELDS:
        assert (
            fields.FIELD_SEVERITY[field] == "CRITICAL"
        )


def test_consumer_modules_share_the_same_schema_objects():
    """Consumers must import the schema, not redeclare it.

    If a module redeclares its own dict, identity breaks and
    the copies can drift apart silently.
    """

    assert fields.FIELD_LABELS is EVALUATOR_LABELS
    assert fields.FIELD_SEVERITY is RISK_SEVERITY
    assert fields.FIELD_PATTERNS is EXTRACTOR_PATTERNS
    assert fields.CRITICAL_FIELDS is CRITICAL_FIELDS_CONSUMER


def test_confidence_thresholds_are_shared():
    assert (
        fields.LOW_CONFIDENCE_THRESHOLD is RISK_THRESHOLD
    )
    assert (
        fields.LOW_CONFIDENCE_THRESHOLD is ANALYSIS_THRESHOLD
    )
    assert fields.LOW_CONFIDENCE_THRESHOLD == 60.0
    assert fields.HIGH_CONFIDENCE_THRESHOLD == 85.0


def test_extractor_patterns_match_labels():
    """Patterns must be derived from the labels so the two
    cannot disagree."""

    sample_text = "\n".join(
        f"{label}: sample-value"
        for label in fields.FIELD_LABELS.values()
    )

    for field, pattern in fields.FIELD_PATTERNS.items():
        match = re.search(
            pattern,
            sample_text,
            re.IGNORECASE,
        )

        assert match is not None, field
        assert match.group(1).strip() == "sample-value"


def test_anchored_pattern_requires_label_line():
    pattern = fields.anchored_field_pattern("owner_name")

    assert re.search(
        pattern,
        "Owner Name: Someone",
        re.IGNORECASE | re.MULTILINE,
    )

    assert not re.search(
        pattern,
        "some Owner Name: value",
        re.IGNORECASE | re.MULTILINE,
    )


def test_anchored_pattern_unknown_field():
    assert fields.anchored_field_pattern("nope") == ""
