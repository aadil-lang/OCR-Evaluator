import json

import pytest

from src.evaluation.robustness_runner import (
    RobustnessRunner,
)


class FakeEvaluator:
    def evaluate(
        self,
        image_path: str,
        ground_truth_path: str,
    ) -> dict:
        return {
            "document": image_path.split("\\")[-1],
            "cer": 0.0,
            "wer": 0.0,
            "field_accuracy": 1.0,
            "status": "PASS",
        }


def create_manifest(tmp_path):
    manifest_path = tmp_path / "manifest.json"

    manifest = {
        "experiment": "OCR robustness evaluation",
        "version": "1.0",
        "ground_truth": "test_document.json",
        "baseline": "test_document.png",
        "tests": [
            {
                "document": "renamed_image.png",
                "degradation": "Blur",
                "severity": 15,
                "ground_truth": "test_document.json",
                "baseline": "test_document.png",
            }
        ],
    }

    manifest_path.write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    return manifest_path


def test_runner_uses_manifest_metadata(
    tmp_path,
):
    images = tmp_path / "images"
    ground_truth = tmp_path / "ground_truth"

    images.mkdir()
    ground_truth.mkdir()

    (images / "renamed_image.png").write_bytes(
        b"fake image"
    )

    (ground_truth / "test_document.json").write_text(
        "{}",
        encoding="utf-8",
    )

    manifest_path = create_manifest(tmp_path)

    runner = RobustnessRunner.__new__(
        RobustnessRunner
    )

    runner.document_evaluator = FakeEvaluator()

    results = runner.run(
        str(manifest_path),
        str(images),
        str(ground_truth),
    )

    assert len(results) == 1

    robustness = results[0]["robustness"]

    assert robustness["degradation"] == "Blur"
    assert robustness["severity"] == 15
    assert robustness["baseline"] == "test_document.png"


def test_runner_does_not_depend_on_filename(
    tmp_path,
):
    images = tmp_path / "images"
    ground_truth = tmp_path / "ground_truth"

    images.mkdir()
    ground_truth.mkdir()

    # Deliberately unrelated filename.
    (
        images / "completely_unrelated_name.png"
    ).write_bytes(b"fake image")

    (ground_truth / "test_document.json").write_text(
        "{}",
        encoding="utf-8",
    )

    manifest_path = tmp_path / "manifest.json"

    manifest = {
        "experiment": "OCR robustness evaluation",
        "version": "1.0",
        "ground_truth": "test_document.json",
        "tests": [
            {
                "document": "completely_unrelated_name.png",
                "degradation": "Blur",
                "severity": 15,
            }
        ],
    }

    manifest_path.write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    runner = RobustnessRunner.__new__(
        RobustnessRunner
    )

    runner.document_evaluator = FakeEvaluator()

    results = runner.run(
        str(manifest_path),
        str(images),
        str(ground_truth),
    )

    assert results[0]["robustness"]["degradation"] == "Blur"
    assert results[0]["robustness"]["severity"] == 15


def test_runner_requires_image(
    tmp_path,
):
    images = tmp_path / "images"
    ground_truth = tmp_path / "ground_truth"

    images.mkdir()
    ground_truth.mkdir()

    (ground_truth / "test_document.json").write_text(
        "{}",
        encoding="utf-8",
    )

    manifest_path = create_manifest(tmp_path)

    runner = RobustnessRunner.__new__(
        RobustnessRunner
    )

    runner.document_evaluator = FakeEvaluator()

    with pytest.raises(FileNotFoundError):
        runner.run(
            str(manifest_path),
            str(images),
            str(ground_truth),
        )