import json

import pytest

from src.evaluation.manifest import RobustnessManifest


def create_manifest(tmp_path, data):
    path = tmp_path / "manifest.json"

    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    return path


def test_manifest_loads_valid_file(tmp_path):
    path = create_manifest(
        tmp_path,
        {
            "experiment": "OCR robustness evaluation",
            "version": "1.0",
            "ground_truth": "test_document.json",
            "tests": [],
        },
    )

    manifest = RobustnessManifest(str(path))

    assert manifest.experiment == "OCR robustness evaluation"
    assert manifest.version == "1.0"
    assert manifest.ground_truth == "test_document.json"
    assert manifest.tests == []


def test_manifest_reads_baseline(tmp_path):
    path = create_manifest(
        tmp_path,
        {
            "experiment": "OCR robustness evaluation",
            "version": "1.0",
            "ground_truth": "test_document.json",
            "baseline": "test_document.png",
            "tests": [],
        },
    )

    manifest = RobustnessManifest(str(path))

    assert manifest.baseline == "test_document.png"


def test_manifest_baseline_is_optional(tmp_path):
    path = create_manifest(
        tmp_path,
        {
            "experiment": "OCR robustness evaluation",
            "version": "1.0",
            "ground_truth": "test_document.json",
            "tests": [],
        },
    )

    manifest = RobustnessManifest(str(path))

    assert manifest.baseline is None


def test_manifest_rejects_missing_required_field(tmp_path):
    path = create_manifest(
        tmp_path,
        {
            "experiment": "OCR robustness evaluation",
            "version": "1.0",
            "tests": [],
        },
    )

    with pytest.raises(ValueError):
        RobustnessManifest(str(path))


def test_manifest_rejects_non_list_tests(tmp_path):
    path = create_manifest(
        tmp_path,
        {
            "experiment": "OCR robustness evaluation",
            "version": "1.0",
            "ground_truth": "test_document.json",
            "tests": {},
        },
    )

    with pytest.raises(ValueError):
        RobustnessManifest(str(path))

def test_manifest_reads_test_metadata(tmp_path):
    path = create_manifest(
        tmp_path,
        {
            "experiment": "OCR robustness evaluation",
            "version": "1.0",
            "ground_truth": "test_document.json",
            "tests": [
                {
                    "document": "blur_7.png",
                    "degradation": "Blur",
                    "severity": 7,
                }
            ],
        },
    )

    manifest = RobustnessManifest(str(path))

    test = manifest.get_test("blur_7.png")

    assert test is not None
    assert test["degradation"] == "Blur"
    assert test["severity"] == 7


def test_manifest_returns_none_for_unknown_document(tmp_path):
    path = create_manifest(
        tmp_path,
        {
            "experiment": "OCR robustness evaluation",
            "version": "1.0",
            "ground_truth": "test_document.json",
            "tests": [],
        },
    )

    manifest = RobustnessManifest(str(path))

    assert manifest.get_test("missing.png") is None


def test_manifest_rejects_test_missing_document(tmp_path):
    path = create_manifest(
        tmp_path,
        {
            "experiment": "OCR robustness evaluation",
            "version": "1.0",
            "ground_truth": "test_document.json",
            "tests": [
                {
                    "degradation": "Blur",
                    "severity": 7,
                }
            ],
        },
    )

    with pytest.raises(ValueError):
        RobustnessManifest(str(path))


def test_manifest_rejects_test_missing_degradation(tmp_path):
    path = create_manifest(
        tmp_path,
        {
            "experiment": "OCR robustness evaluation",
            "version": "1.0",
            "ground_truth": "test_document.json",
            "tests": [
                {
                    "document": "blur_7.png",
                    "severity": 7,
                }
            ],
        },
    )

    with pytest.raises(ValueError):
        RobustnessManifest(str(path))


def test_manifest_rejects_test_missing_severity(tmp_path):
    path = create_manifest(
        tmp_path,
        {
            "experiment": "OCR robustness evaluation",
            "version": "1.0",
            "ground_truth": "test_document.json",
            "tests": [
                {
                    "document": "blur_7.png",
                    "degradation": "Blur",
                }
            ],
        },
    )

    with pytest.raises(ValueError):
        RobustnessManifest(str(path))


def test_manifest_rejects_invalid_test_entry(tmp_path):
    path = create_manifest(
        tmp_path,
        {
            "experiment": "OCR robustness evaluation",
            "version": "1.0",
            "ground_truth": "test_document.json",
            "tests": [
                "blur_7.png"
            ],
        },
    )

    with pytest.raises(ValueError):
        RobustnessManifest(str(path))