from src.evaluation.faithfulness import (
    check_field_supported,
)


SOURCE_TEXT = """
SALE DEED

Owner Name: Daniel James Anderson
Father Name: James Anderson
Survey Number: 128/3
Area: 0.2450 Hectare
Village: Rampur
Tehsil: Sadar
District: Varanasi
Registration Number: REG-2026-00128
"""


def test_correct_field_value_is_supported():
    result = check_field_supported(
        "survey_number",
        "128/3",
        SOURCE_TEXT,
    )

    assert result["supported"] is True
    assert result["source_value"] == "128/3"


def test_wrong_field_value_is_unsupported():
    result = check_field_supported(
        "survey_number",
        "128/8",
        SOURCE_TEXT,
    )

    assert result["supported"] is False
    assert result["source_value"] == "128/3"


def test_correct_owner_name_is_supported():
    result = check_field_supported(
        "owner_name",
        "Daniel James Anderson",
        SOURCE_TEXT,
    )

    assert result["supported"] is True


def test_unknown_field_is_unsupported():
    result = check_field_supported(
        "property_type",
        "Residential",
        SOURCE_TEXT,
    )

    assert result["supported"] is False
    assert result["source_value"] == ""