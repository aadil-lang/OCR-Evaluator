from src.evaluation.faithfulness import check_value_supported


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


def test_completely_unrelated_value_is_unsupported():
    result = check_value_supported(
        "Mumbai",
        SOURCE_TEXT,
    )

    assert result["supported"] is False


def test_wrong_survey_number_is_unsupported():
    result = check_value_supported(
        "128/8",
        SOURCE_TEXT,
    )

    assert result["supported"] is False


def test_similar_but_wrong_owner_name_is_unsupported():
    result = check_value_supported(
        "Daniel James Andersons",
        SOURCE_TEXT,
    )

    assert result["supported"] is False


def test_value_with_different_case_is_supported():
    result = check_value_supported(
        "DANIEL JAMES ANDERSON",
        SOURCE_TEXT,
    )

    assert result["supported"] is True