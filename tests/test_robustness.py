from src.evaluation.robustness import (
    parse_degradation,
    build_robustness_summary,
)


def test_parse_blur():
    degradation, severity = parse_degradation(
        "blur_15.png"
    )

    assert degradation == "Blur"
    assert severity == 15


def test_parse_noise():
    degradation, severity = parse_degradation(
        "noise_40.png"
    )

    assert degradation == "Noise"
    assert severity == 40


def test_parse_rotation():
    degradation, severity = parse_degradation(
        "rotation_10.png"
    )

    assert degradation == "Rotation"
    assert severity == 10


def test_unknown_degradation():
    degradation, severity = parse_degradation(
        "test_document.png"
    )

    assert degradation == "Unknown"
    assert severity == 0.0


def test_robustness_summary_handles_review():
    results = [
        {
            "document": "noise_25.png",
            "status": "PASS",
        },
        {
            "document": "noise_40.png",
            "status": "REVIEW",
        },
        {
            "document": "noise_60.png",
            "status": "FAIL",
        },
    ]

    summary = build_robustness_summary(results)

    assert summary["Noise"]["tests"] == 3
    assert summary["Noise"]["passed"] == 1
    assert summary["Noise"]["failed"] == 1
    assert summary["Noise"]["review"] == 1
    assert summary["Noise"]["pass_rate"] == 1 / 3
    assert summary["Noise"]["max_passing_level"] == 25
    assert summary["Noise"]["first_failure"] == 60


def test_robustness_report_is_generated(tmp_path):
    from src.reporting.robustness_report import (
        RobustnessReportGenerator,
    )

    summary = {
        "Blur": {
            "tests": 3,
            "passed": 1,
            "review": 1,
            "failed": 1,
            "accurate": 2,
            "inaccurate": 1,
            "pass_rate": 1 / 3,
            "max_accurate_level": 7,
            "first_accuracy_failure": 15,
        }
    }

    output = tmp_path / "robustness_report.md"

    generator = RobustnessReportGenerator()

    generator.generate(
        summary,
        str(output),
    )

    assert output.exists()

    content = output.read_text(
        encoding="utf-8"
    )

    assert "# OCR Robustness Evaluation Report" in content
    assert "| Blur |" in content
    assert "| 3 | 1 | 1 | 1 |" in content
    assert "| 2 | 1 | 7 | 15 |" in content
    assert "PASS" in content
    assert "REVIEW" in content
    assert "FAIL" in content
    assert "Accurate" in content
    assert "Inaccurate" in content
    assert "Max Accurate Level" in content
    assert "First Accuracy Failure" in content


def test_explicit_robustness_metadata():
    from src.evaluation.robustness import (
        get_robustness_metadata,
    )

    result = {
        "document": "random_image_abc.png",
        "status": "PASS",
        "robustness": {
            "type": "blur",
            "severity": 3,
        },
    }

    degradation, severity = get_robustness_metadata(result)

    assert degradation == "Blur"
    assert severity == 3.0


def test_baseline_document_has_no_robustness_metadata():
    from src.evaluation.robustness import (
        get_degradation_metadata,
    )

    result = {
        "document": "test_document.png",
        "status": "PASS",
    }

    assert get_degradation_metadata(result) is None


def test_correct_review_is_counted_as_accuracy():
    from src.evaluation.robustness import is_accuracy_pass

    result = {
        "field_accuracy": 1.0,
        "critical_field_accuracy": 1.0,
        "failed_fields": [],
        "critical_failed_fields": [],
        "status": "REVIEW",
    }

    assert is_accuracy_pass(result) is True


def test_failed_result_is_not_accuracy_pass():
    from src.evaluation.robustness import is_accuracy_pass

    result = {
        "field_accuracy": 0.5,
        "critical_field_accuracy": 0.5,
        "failed_fields": ["owner_name"],
        "critical_failed_fields": ["owner_name"],
        "status": "FAIL",
    }

    assert is_accuracy_pass(result) is False


def test_summary_separates_review_from_failure():
    from src.evaluation.robustness import build_robustness_summary

    results = [
        {
            "document": "blur_3.png",
            "status": "REVIEW",
            "field_accuracy": 1.0,
            "critical_field_accuracy": 1.0,
            "failed_fields": [],
            "critical_failed_fields": [],
            "robustness": {
                "degradation": "Blur",
                "severity": 3,
            },
        },
        {
            "document": "blur_15.png",
            "status": "FAIL",
            "field_accuracy": 0.5,
            "critical_field_accuracy": 0.5,
            "failed_fields": ["owner_name"],
            "critical_failed_fields": ["owner_name"],
            "robustness": {
                "degradation": "Blur",
                "severity": 15,
            },
        },
    ]

    summary = build_robustness_summary(results)

    assert summary["Blur"]["tests"] == 2
    assert summary["Blur"]["passed"] == 0
    assert summary["Blur"]["review"] == 1
    assert summary["Blur"]["failed"] == 1
    assert summary["Blur"]["accurate"] == 1
    assert summary["Blur"]["inaccurate"] == 1
    assert summary["Blur"]["max_accurate_level"] == 3
    assert summary["Blur"]["first_accuracy_failure"] == 15
