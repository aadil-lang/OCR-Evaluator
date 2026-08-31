from src.evaluation.critical_fields import (
    calculate_critical_field_accuracy,
)


GROUND_TRUTH = {
    "owner_name": "Daniel James Anderson",
    "father_name": "James Anderson",
    "survey_number": "128/3",
    "area": "0.2450 Hectare",
    "village": "Rampur",
    "tehsil": "Sadar",
    "district": "Varanasi",
    "registration_number": "REG-2026-00128",
}


def test_all_critical_fields_match():
    predicted = GROUND_TRUTH.copy()

    result = calculate_critical_field_accuracy(
        GROUND_TRUTH,
        predicted,
    )

    assert result["accuracy"] == 1.0
    assert result["failed_fields"] == []


def test_critical_field_failure_is_detected():
    predicted = GROUND_TRUTH.copy()
    predicted["survey_number"] = "128/8"

    result = calculate_critical_field_accuracy(
        GROUND_TRUTH,
        predicted,
    )

    assert result["accuracy"] == 0.75
    assert "survey_number" in result["failed_fields"]


def test_missing_critical_field_is_failure():
    predicted = GROUND_TRUTH.copy()
    del predicted["owner_name"]

    result = calculate_critical_field_accuracy(
        GROUND_TRUTH,
        predicted,
    )

    assert result["accuracy"] == 0.75
    assert "owner_name" in result["failed_fields"]


def test_non_critical_field_does_not_affect_critical_accuracy():
    predicted = GROUND_TRUTH.copy()
    predicted["village"] = "Lucknow"

    result = calculate_critical_field_accuracy(
        GROUND_TRUTH,
        predicted,
    )

    assert result["accuracy"] == 1.0
    assert result["failed_fields"] == []