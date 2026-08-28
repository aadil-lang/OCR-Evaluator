from pathlib import Path

from src.evaluation.batch_evaluator import BatchEvaluator
from src.ocr.engine import OCREngine


DOCUMENTS_DIR = Path("data/documents")
GROUND_TRUTH_DIR = Path("data/ground_truth")


def test_batch_evaluator_returns_results():
    evaluator = BatchEvaluator(
        OCREngine(language="eng")
    )

    results = evaluator.evaluate_directory(
        documents_directory=str(DOCUMENTS_DIR),
        ground_truth_directory=str(GROUND_TRUTH_DIR),
    )

    assert isinstance(results, list)
    assert len(results) >= 1


def test_batch_evaluator_processes_sample_document():
    evaluator = BatchEvaluator(
        OCREngine(language="eng")
    )

    results = evaluator.evaluate_directory(
        documents_directory=str(DOCUMENTS_DIR),
        ground_truth_directory=str(GROUND_TRUTH_DIR),
    )

    result = next(
        item
        for item in results
        if item["document"] == "test_document.png"
    )

    assert result["status"] in {
        "PASS",
        "REVIEW",
        "FAIL",
    }


def test_batch_evaluator_requires_document_directory():
    evaluator = BatchEvaluator(
        OCREngine(language="eng")
    )

    missing_directory = Path(
        "data/documents/does_not_exist"
    )

    try:
        evaluator.evaluate_directory(
            documents_directory=str(missing_directory),
            ground_truth_directory=str(GROUND_TRUTH_DIR),
        )
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass