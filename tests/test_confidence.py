from src.evaluation.confidence import (
    calculate_field_confidence,
    calculate_all_field_confidences,
)


def test_field_confidence():
    words = [
        {"text": "Daniel", "confidence": 90.0},
        {"text": "James", "confidence": 80.0},
        {"text": "Anderson", "confidence": 100.0},
    ]

    confidence = calculate_field_confidence(
        "Daniel James Anderson",
        words,
    )

    assert confidence == 90.0


def test_missing_field_has_no_confidence():
    words = [
        {"text": "Daniel", "confidence": 90.0},
    ]

    confidence = calculate_field_confidence(
        "Unknown Person",
        words,
    )

    assert confidence is None


def test_all_field_confidences():
    words = [
        {"text": "Daniel", "confidence": 90.0},
        {"text": "128/3", "confidence": 80.0},
    ]

    fields = {
        "owner_name": "Daniel",
        "survey_number": "128/3",
    }

    result = calculate_all_field_confidences(
        fields,
        words,
    )

    assert result["owner_name"] == 90.0
    assert result["survey_number"] == 80.0
from src.evaluation.confidence_analysis import (
    analyze_confidence_correctness,
    analyze_results,
)


def test_high_confidence_failure_is_detected():
    result = {
        "document": "rotation_10.png",
        "confidence": 91.0,
        "status": "FAIL",
    }

    analysis = analyze_confidence_correctness(result)

    assert analysis["category"] == "HIGH_CONFIDENCE_FAILURE"


def test_low_confidence_pass_is_detected():
    result = {
        "document": "noise_25.png",
        "confidence": 55.0,
        "status": "PASS",
    }

    analysis = analyze_confidence_correctness(result)

    assert analysis["category"] == "LOW_CONFIDENCE_PASS"


def test_aligned_result_is_detected():
    result = {
        "document": "test_document.png",
        "confidence": 92.0,
        "status": "PASS",
    }

    analysis = analyze_confidence_correctness(result)

    assert analysis["category"] == "ALIGNED"


def test_missing_confidence_is_handled():
    result = {
        "document": "empty.png",
        "confidence": None,
        "status": "FAIL",
    }

    analysis = analyze_confidence_correctness(result)

    assert analysis["category"] == "UNAVAILABLE"


def test_analyze_results_counts_categories():
    results = [
        {
            "document": "a.png",
            "confidence": 92.0,
            "status": "FAIL",
        },
        {
            "document": "b.png",
            "confidence": 50.0,
            "status": "PASS",
        },
        {
            "document": "c.png",
            "confidence": 90.0,
            "status": "PASS",
        },
    ]

    analysis = analyze_results(results)

    assert analysis["total_documents"] == 3
    assert analysis["high_confidence_failures"] == 1
    assert analysis["low_confidence_passes"] == 1
    assert analysis["aligned"] == 1
def test_dash_variants_are_normalized_for_matching():
    words = [
        {
            "text": "REG\u20142026-\u201400128",
            "confidence": 32.0,
        },
    ]

    confidence = calculate_field_confidence(
        "REG-2026-00128",
        words,
    )

    assert confidence == 32.0


def test_punctuation_is_normalized_for_matching():
    words = [
        {"text": "Varanasi,", "confidence": 96.0},
    ]

    confidence = calculate_field_confidence(
        "Varanasi",
        words,
    )

    assert confidence == 96.0
