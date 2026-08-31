from pathlib import Path

import pytest

from src.evaluation.evaluator import DocumentEvaluator
from src.ocr.engine import OCREngine


IMAGE_PATH = Path("data/documents/test_document.png")
GROUND_TRUTH_PATH = Path(
    "data/ground_truth/test_document.json"
)


CRITICAL_FIELDS = {
    "owner_name",
    "survey_number",
    "area",
    "registration_number",
}


@pytest.fixture
def evaluator():
    ocr_engine = OCREngine(language="eng")
    return DocumentEvaluator(ocr_engine)


def test_sample_files_exist():
    assert IMAGE_PATH.exists()
    assert GROUND_TRUTH_PATH.exists()


def test_evaluator_returns_result(evaluator):
    result = evaluator.evaluate(
        image_path=str(IMAGE_PATH),
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    assert isinstance(result, dict)


def test_evaluator_returns_expected_keys(evaluator):
    result = evaluator.evaluate(
        image_path=str(IMAGE_PATH),
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    expected_keys = {
        "document",
        "cer",
        "wer",
        "field_accuracy",
        "critical_field_accuracy",
        "confidence",
        "status",
        "failed_fields",
        "critical_fields",
        "critical_failed_fields",
        "fields",
        "faithfulness",
        "ocr_text",
    }

    assert expected_keys.issubset(result.keys())


def test_evaluator_metrics_are_valid(evaluator):
    result = evaluator.evaluate(
        image_path=str(IMAGE_PATH),
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    assert 0.0 <= result["cer"]
    assert 0.0 <= result["wer"]
    assert 0.0 <= result["field_accuracy"] <= 1.0
    assert 0.0 <= result["critical_field_accuracy"] <= 1.0
    assert 0.0 <= result["confidence"] <= 100.0


def test_evaluator_contains_all_fields(evaluator):
    result = evaluator.evaluate(
        image_path=str(IMAGE_PATH),
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    expected_fields = {
        "owner_name",
        "father_name",
        "survey_number",
        "area",
        "village",
        "tehsil",
        "district",
        "registration_number",
    }

    assert set(result["fields"].keys()) == expected_fields


def test_evaluator_contains_all_critical_fields(evaluator):
    result = evaluator.evaluate(
        image_path=str(IMAGE_PATH),
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    assert set(result["critical_fields"].keys()) == CRITICAL_FIELDS


def test_evaluator_critical_fields_have_expected_structure(evaluator):
    result = evaluator.evaluate(
        image_path=str(IMAGE_PATH),
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    for field in CRITICAL_FIELDS:
        field_result = result["critical_fields"][field]

        assert "expected" in field_result
        assert "actual" in field_result
        assert "match" in field_result

        assert isinstance(field_result["match"], bool)


def test_evaluator_critical_failed_fields_are_consistent(evaluator):
    result = evaluator.evaluate(
        image_path=str(IMAGE_PATH),
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    expected_failed_fields = {
        field
        for field, field_result in result["critical_fields"].items()
        if not field_result["match"]
    }

    assert set(result["critical_failed_fields"]) == expected_failed_fields


def test_evaluator_status_is_valid(evaluator):
    result = evaluator.evaluate(
        image_path=str(IMAGE_PATH),
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    assert result["status"] in {
        "PASS",
        "REVIEW",
        "FAIL",
    }


def test_evaluator_ocr_text_is_not_empty(evaluator):
    result = evaluator.evaluate(
        image_path=str(IMAGE_PATH),
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    assert result["ocr_text"].strip() != ""


def test_evaluator_contains_confidence(evaluator):
    result = evaluator.evaluate(
        image_path=str(IMAGE_PATH),
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    assert "confidence" in result
    assert result["confidence"] is not None
    assert 0 <= result["confidence"] <= 100