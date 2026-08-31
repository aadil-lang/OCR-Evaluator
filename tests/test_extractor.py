from src.evaluation.extractor import extract_fields


OCR_TEXT = """
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


def test_extracts_all_fields():
    fields = extract_fields(OCR_TEXT)

    assert fields["owner_name"] == "Daniel James Anderson"
    assert fields["father_name"] == "James Anderson"
    assert fields["survey_number"] == "128/3"
    assert fields["area"] == "0.2450 Hectare"
    assert fields["village"] == "Rampur"
    assert fields["tehsil"] == "Sadar"
    assert fields["district"] == "Varanasi"
    assert fields["registration_number"] == "REG-2026-00128"


def test_missing_field_returns_empty_string():
    text = """
    SALE DEED

    Owner Name: Daniel James Anderson
    Survey Number: 128/3
    """

    fields = extract_fields(text)

    assert fields["owner_name"] == "Daniel James Anderson"
    assert fields["survey_number"] == "128/3"
    assert fields["father_name"] == ""
    assert fields["area"] == ""
    assert fields["village"] == ""
    assert fields["tehsil"] == ""
    assert fields["district"] == ""
    assert fields["registration_number"] == ""


def test_extraction_is_case_insensitive():
    text = """
    owner name: Daniel James Anderson
    SURVEY NUMBER: 128/3
    """

    fields = extract_fields(text)

    assert fields["owner_name"] == "Daniel James Anderson"
    assert fields["survey_number"] == "128/3"


def test_extra_whitespace_is_trimmed():
    text = """
    Owner Name:    Daniel James Anderson
    Survey Number:     128/3
    """

    fields = extract_fields(text)

    assert fields["owner_name"] == "Daniel James Anderson"
    assert fields["survey_number"] == "128/3"