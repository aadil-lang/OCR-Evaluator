"""Regression tests for the FastAPI evaluation endpoint.

These tests use a fake OCR engine so they run without Tesseract
and verify the API contract the frontend depends on.
"""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from src.api import create_app


MATCHING_TEXT = (
    "Owner Name: Daniel James Anderson\n"
    "Father Name: James Anderson\n"
    "Survey Number: 128/3\n"
    "Area: 0.2450 Hectare\n"
    "Village: Rampur\n"
    "Tehsil: Sadar\n"
    "District: Varanasi\n"
    "Registration Number: REG-2026-00128"
)


MISMATCHING_TEXT = (
    "Owner Name: Daniel James Anderson\n"
    "Father Name: James Anderson\n"
    "Survey Number: 999/9\n"
    "Area: 0.2450 Hectare\n"
    "Village: Rampur\n"
    "Tehsil: Sadar\n"
    "District: Varanasi\n"
    "Registration Number: REG-2026-00128"
)


GROUND_TRUTH = {
    "transcription": MATCHING_TEXT,
    "fields": {
        "owner_name": "Daniel James Anderson",
        "father_name": "James Anderson",
        "survey_number": "128/3",
        "area": "0.2450 Hectare",
        "village": "Rampur",
        "tehsil": "Sadar",
        "district": "Varanasi",
        "registration_number": "REG-2026-00128",
    },
}


class FakeEngine:
    """Stand-in for OCREngine with a fixed extraction result."""

    def __init__(self, text):
        self.text = text

    def extract(self, image_path):
        words = [
            {"text": word, "confidence": 95.0}
            for line in self.text.splitlines()
            for word in line.split()
        ]

        return {
            "document": Path(image_path).name,
            "text": self.text,
            "confidence": 95.0,
            "words": words,
        }


def make_client(text, ground_truth_path):
    app = create_app(
        ocr_engine=FakeEngine(text),
        default_ground_truth=ground_truth_path,
        cors_origins=["http://localhost:5173"],
    )
    return TestClient(app)


def write_ground_truth(path, ground_truth=None):
    path.write_text(
        json.dumps(ground_truth or GROUND_TRUTH),
        encoding="utf-8",
    )


def risk_field_names(entries):
    """Mirror of the frontend's field-name extraction."""

    return [
        entry["field"] if isinstance(entry, dict) else entry
        for entry in entries
        if entry
    ]


def test_pass_response_has_no_risk_items(tmp_path):
    gt_path = tmp_path / "gt.json"
    write_ground_truth(gt_path)
    client = make_client(MATCHING_TEXT, gt_path)

    response = client.post(
        "/evaluate",
        files={"file": ("document.png", b"png-bytes", "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "PASS"
    assert payload["risk"]["status"] == "PASS"
    assert payload["risk"]["failed_fields"] == []
    assert payload["risk"]["low_confidence_fields"] == []
    assert set(payload["fields"].keys()) == set(GROUND_TRUTH["fields"])


def test_fail_response_risk_schema_matches_frontend(tmp_path):
    """Regression: the frontend crashes when risk items are not
    extractable as field names (it called .replaceAll on dicts)."""

    gt_path = tmp_path / "gt.json"
    write_ground_truth(gt_path)
    client = make_client(MISMATCHING_TEXT, gt_path)

    response = client.post(
        "/evaluate",
        files={"file": ("document.png", b"png-bytes", "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()

    # A critical-field mismatch must fail the document.
    assert payload["status"] == "FAIL"
    assert payload["risk"]["status"] == "FAIL"

    failed = payload["risk"]["failed_fields"]
    assert len(failed) == 1

    # The frontend requires each entry to yield a field name.
    names = risk_field_names(failed)
    assert "survey_number" in names

    # The dict shape itself is the documented contract.
    entry = failed[0]
    assert isinstance(entry, dict)
    assert entry["field"] == "survey_number"
    assert entry["severity"] == "CRITICAL"
    assert entry["reason"] == "FIELD_MISMATCH"


def test_reject_non_image_upload(tmp_path):
    gt_path = tmp_path / "gt.json"
    write_ground_truth(gt_path)
    client = make_client(MATCHING_TEXT, gt_path)

    response = client.post(
        "/evaluate",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert "PNG and JPEG" in response.json()["detail"]


def test_missing_ground_truth_returns_404(tmp_path):
    client = make_client(
        MATCHING_TEXT,
        tmp_path / "does_not_exist.json",
    )

    response = client.post(
        "/evaluate",
        files={"file": ("document.png", b"png-bytes", "image/png")},
    )

    assert response.status_code == 404
    assert "Ground-truth file not found" in response.json()["detail"]


def test_no_usable_filename_returns_400(tmp_path):
    """A present-but-blank filename must be rejected with a clean
    400 rather than crashing or using a default name."""

    gt_path = tmp_path / "gt.json"
    write_ground_truth(gt_path)
    client = make_client(MATCHING_TEXT, gt_path)

    response = client.post(
        "/evaluate",
        files={"file": ("   ", b"png-bytes", "image/png")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "No file provided."


def test_empty_filename_is_rejected_as_client_error(tmp_path):
    """A truly empty filename cannot be parsed as a file upload, so
    the framework rejects it before the handler. It must be a client
    error (4xx), never a server error (5xx)."""

    gt_path = tmp_path / "gt.json"
    write_ground_truth(gt_path)
    client = make_client(MATCHING_TEXT, gt_path)

    response = client.post(
        "/evaluate",
        files={"file": ("", b"png-bytes", "image/png")},
    )

    assert 400 <= response.status_code < 500


def test_traversal_filename_stays_in_temp_dir(tmp_path):
    """A client-controlled filename must not escape the temp dir."""

    gt_path = tmp_path / "gt.json"
    write_ground_truth(gt_path)
    client = make_client(MATCHING_TEXT, gt_path)

    response = client.post(
        "/evaluate",
        files={
            "file": (
                "../../evil.png",
                b"png-bytes",
                "image/png",
            ),
        },
    )

    # The upload is stored under a generated name; the request
    # itself succeeds (or fails evaluation) but never writes the
    # client-chosen path.
    assert response.status_code in {200, 500}

    escaped = tmp_path / "evil.png"
    assert not escaped.exists()
    assert not (tmp_path.parent / "evil.png").exists()
