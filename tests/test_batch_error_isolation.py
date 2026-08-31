"""Regression tests for batch error isolation.

A batch must continue past documents that cannot be evaluated:
missing ground truth and OCR failures become ERROR results
instead of aborting the run or silently falling back to another
document's ground truth.
"""

import base64
import json
from pathlib import Path

from src.evaluation.batch_evaluator import (
    BatchEvaluator,
    make_error_result,
)


# A minimal valid 1x1 PNG container. The fake engine ignores
# pixel content, so any image-shaped file is acceptable input.
PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
    "AAAADUlEQVR42mNk+M9QDwADgQF/fbyF3QAAAABJRU5"
    "ErkJggg=="
)


GROUND_TRUTH_FIELDS = {
    "owner_name": "A",
    "father_name": "B",
    "survey_number": "1",
    "area": "2",
    "village": "C",
    "tehsil": "D",
    "district": "E",
    "registration_number": "R-1",
}


MATCHING_TEXT = (
    "Owner Name: A\n"
    "Father Name: B\n"
    "Survey Number: 1\n"
    "Area: 2\n"
    "Village: C\n"
    "Tehsil: D\n"
    "District: E\n"
    "Registration Number: R-1"
)


class GoodEngine:
    """Returns matching text for every image it can open."""

    def extract(self, image_path):
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        words = [
            {"text": word, "confidence": 95.0}
            for line in MATCHING_TEXT.splitlines()
            for word in line.split()
        ]

        return {
            "document": image_path.name,
            "text": MATCHING_TEXT,
            "confidence": 95.0,
            "words": words,
        }


class CorruptImageEngine:
    """Fails OCR for a specific image, works for the rest."""

    def __init__(self, failing_name):
        self.failing_name = failing_name
        self.good_engine = GoodEngine()

    def extract(self, image_path):
        image_path = Path(image_path)

        if image_path.name == self.failing_name:
            raise RuntimeError(
                "Simulated OCR failure for "
                f"{image_path.name}"
            )

        return self.good_engine.extract(image_path)


def setup_dataset(tmp_path, ground_truth_stems):
    """Create documents and their ground-truth files."""

    documents = tmp_path / "documents"
    ground_truth = tmp_path / "ground_truth"

    documents.mkdir()
    ground_truth.mkdir()

    for stem in ground_truth_stems:
        image = documents / f"{stem}.png"
        image.write_bytes(PNG_BYTES)

        gt_file = ground_truth / f"{stem}.json"
        gt_file.write_text(
            json.dumps(
                {
                    "transcription": MATCHING_TEXT,
                    "fields": GROUND_TRUTH_FIELDS,
                }
            ),
            encoding="utf-8",
        )

    return documents, ground_truth


def test_missing_ground_truth_is_error_not_fallback(tmp_path):
    """Regression: a document must never be scored against
    another document's ground truth (test_document.json)."""

    documents, ground_truth = setup_dataset(
        tmp_path,
        ["good"],
    )

    # Add an image with no matching ground-truth file.
    (documents / "orphan.png").write_bytes(PNG_BYTES)

    results = BatchEvaluator(GoodEngine()).evaluate_directory(
        documents_directory=str(documents),
        ground_truth_directory=str(ground_truth),
    )

    by_document = {
        result["document"]: result
        for result in results
    }

    assert by_document["good.png"]["status"] == "PASS"

    orphan = by_document["orphan.png"]
    assert orphan["status"] == "ERROR"
    assert "Ground-truth file not found" in orphan["error"]

    # The batch continued instead of aborting.
    assert len(results) == 2


def test_corrupt_image_is_error_and_batch_continues(tmp_path):
    """Regression: one unreadable image must not abort the batch."""

    documents, ground_truth = setup_dataset(
        tmp_path,
        ["good", "broken"],
    )

    results = BatchEvaluator(
        CorruptImageEngine("broken.png")
    ).evaluate_directory(
        documents_directory=str(documents),
        ground_truth_directory=str(ground_truth),
    )

    by_document = {
        result["document"]: result
        for result in results
    }

    assert by_document["good.png"]["status"] == "PASS"

    broken = by_document["broken.png"]
    assert broken["status"] == "ERROR"
    assert "Simulated OCR failure" in broken["error"]


def test_error_result_shape(tmp_path):
    """ERROR results must be safe for report aggregation."""

    result = make_error_result(
        "x.png",
        "something failed",
    )

    # Status is an operational value, not a metric.
    assert result["status"] == "ERROR"
    assert result["error"] == "something failed"

    # Metric fields exist with null values so aggregators can
    # rely on the key being present.
    for key in (
        "cer",
        "wer",
        "confidence",
        "field_accuracy",
        "critical_field_accuracy",
    ):
        assert result[key] is None

    # Risk lists exist and are empty.
    assert result["failed_fields"] == []
    assert result["low_confidence_fields"] == []
