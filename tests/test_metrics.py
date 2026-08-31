from src.evaluation.metrics import (
    calculate_cer,
    calculate_wer,
    exact_match,
    calculate_field_accuracy,
)


def test_identical_text_has_zero_cer_and_wer():
    reference = "Survey Number: 128/3"

    assert calculate_cer(reference, reference) == 0.0
    assert calculate_wer(reference, reference) == 0.0


def test_character_error_is_detected():
    reference = "Survey Number: 128/3"
    hypothesis = "Survey Number: 128/8"

    assert calculate_cer(reference, hypothesis) > 0.0


def test_word_error_is_detected():
    reference = "Owner Name: Daniel James Anderson"
    hypothesis = "Owner Name: James Anderson"

    assert calculate_wer(reference, hypothesis) > 0.0


def test_exact_match_normalizes_case_and_whitespace():
    assert exact_match(
        "Daniel James Anderson",
        "  DANIEL   JAMES   ANDERSON  ",
    )


def test_field_accuracy():
    ground_truth = {
        "owner_name": "Daniel James Anderson",
        "survey_number": "128/3",
    }

    prediction = {
        "owner_name": "Daniel James Anderson",
        "survey_number": "128/8",
    }

    result = calculate_field_accuracy(
        ground_truth,
        prediction,
    )

    assert result["accuracy"] == 0.5
    assert result["fields"]["owner_name"]["match"] is True
    assert result["fields"]["survey_number"]["match"] is False

def test_exact_match_normalizes_unicode_em_dash():
    assert exact_match(
        "REG-2026-00128",
        "REG—2026-—00128",
    )