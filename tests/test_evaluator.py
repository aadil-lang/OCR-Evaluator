from pathlib import Path

import pytest

from src.evaluation.evaluator import DocumentEvaluator
from src.ocr.engine import OCREngine


IMAGE_PATH = Path("data/documents/test_document.png")
GROUND_TRUTH_PATH = Path(
    "data/ground_truth/test_document.json"
)


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
        "status",
        "failed_fields",
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
