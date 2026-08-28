from src.evaluation.faithfulness import (
    check_value_supported,
    detect_unsupported_fields,
)


SOURCE_TEXT = """
SALE DEED

Owner Name: Mohammed Aadil Khurshid
Father Name: Mohammed Khurshid
Survey Number: 128/3
Area: 0.2450 Hectare
Village: Rampur
Tehsil: Sadar
District: Varanasi
Registration Number: REG-2026-00128
"""


def test_exact_value_is_supported():
    result = check_value_supported(
        "Mohammed Aadil Khurshid",
        SOURCE_TEXT,
    )

    assert result["supported"] is True
    assert result["similarity"] == 1.0


def test_missing_value_is_not_supported():
    result = check_value_supported(
        "Residential",
        SOURCE_TEXT,
    )

    assert result["supported"] is False


def test_empty_value_is_not_supported():
    result = check_value_supported(
        "",
        SOURCE_TEXT,
    )

    assert result["supported"] is False
    assert result["similarity"] == 0.0


def test_detect_unsupported_fields():
    fields = {
        "owner_name": "Mohammed Aadil Khurshid",
        "survey_number": "128/3",
        "property_type": "Residential",
    }

    result = detect_unsupported_fields(
        fields,
        SOURCE_TEXT,
    )

    assert result["owner_name"]["supported"] is True
    assert result["survey_number"]["supported"] is True
    assert result["property_type"]["supported"] is False


def test_ocr_error_is_detected_as_unsupported():
    fields = {
        "survey_number": "128/8",
    }

    result = detect_unsupported_fields(
        fields,
        SOURCE_TEXT,
    )

    assert result["survey_number"]["supported"] is False