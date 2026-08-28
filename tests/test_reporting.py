import json
from pathlib import Path

from src.reporting.report_generator import ReportGenerator


def sample_results():
    return [
        {
            "document": "document_1.png",
            "cer": 0.10,
            "wer": 0.20,
            "field_accuracy": 0.875,
            "status": "PASS",
        },
        {
            "document": "document_2.png",
            "cer": 0.30,
            "wer": 0.40,
            "field_accuracy": 0.625,
            "status": "FAIL",
        },
        {
            "document": "document_3.png",
            "cer": 0.20,
            "wer": 0.30,
            "field_accuracy": 0.750,
            "status": "REVIEW",
        },
    ]


def test_report_contains_summary(tmp_path):
    generator = ReportGenerator()

    output_path = tmp_path / "report.json"

    report = generator.generate(
        sample_results(),
        str(output_path),
    )

    assert "summary" in report
    assert "documents" in report


def test_report_summary_counts_statuses(tmp_path):
    generator = ReportGenerator()

    output_path = tmp_path / "report.json"

    report = generator.generate(
        sample_results(),
        str(output_path),
    )

    summary = report["summary"]

    assert summary["total_documents"] == 3
    assert summary["passed"] == 1
    assert summary["review"] == 1
    assert summary["failed"] == 1


def test_report_calculates_averages(tmp_path):
    generator = ReportGenerator()

    output_path = tmp_path / "report.json"

    report = generator.generate(
        sample_results(),
        str(output_path),
    )

    summary = report["summary"]

    assert summary["average_cer"] == 0.20
    assert summary["average_wer"] == 0.30
    assert summary["average_field_accuracy"] == 0.75


def test_report_is_written_to_disk(tmp_path):
    generator = ReportGenerator()

    output_path = tmp_path / "report.json"

    generator.generate(
        sample_results(),
        str(output_path),
    )

    assert output_path.exists()


def test_report_is_valid_json(tmp_path):
    generator = ReportGenerator()

    output_path = tmp_path / "report.json"

    generator.generate(
        sample_results(),
        str(output_path),
    )

    with output_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        report = json.load(file)

    assert report["summary"]["total_documents"] == 3
    assert len(report["documents"]) == 3