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
    assert summary["Noise"]["failed"] == 2
    assert summary["Noise"]["pass_rate"] == 1 / 3
    assert summary["Noise"]["max_passing_level"] == 25
    assert summary["Noise"]["first_failure"] == 40

def test_robustness_report_is_generated(tmp_path):
    from src.reporting.robustness_report import (
        RobustnessReportGenerator,
    )

    summary = {
        "Blur": {
            "tests": 3,
            "passed": 2,
            "failed": 1,
            "pass_rate": 2 / 3,
            "max_passing_level": 7,
            "first_failure": 15,
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
    assert "66.7%" in content
    assert "7" in content
    assert "15" in content