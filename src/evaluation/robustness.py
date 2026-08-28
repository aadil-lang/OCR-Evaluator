from collections import defaultdict
from pathlib import Path


DEGRADATION_TYPES = {
    "blur": "Blur",
    "contrast": "Contrast",
    "jpeg": "JPEG",
    "noise": "Noise",
    "rotation": "Rotation",
}


CONTRAST_SEVERITY = {
    "low": 1.0,
    "medium": 2.0,
    "high": 3.0,
    "extreme": 4.0,
}


def parse_degradation(document_name: str) -> tuple[str, float]:
    """Extract degradation type and severity from a document filename."""

    stem = Path(document_name).stem

    for prefix, label in DEGRADATION_TYPES.items():
        if stem.startswith(f"{prefix}_"):
            value = stem[len(prefix) + 1:]

            if prefix == "contrast":
                severity = CONTRAST_SEVERITY.get(
                    value.lower(),
                    0.0,
                )
            else:
                try:
                    severity = float(value)
                except ValueError:
                    severity = 0.0

            return label, severity

    return "Unknown", 0.0


def calculate_pass_rate(results: list[dict]) -> float:
    """Calculate percentage of documents that passed."""

    if not results:
        return 0.0

    passed = sum(
        result["status"] == "PASS"
        for result in results
    )

    return passed / len(results)


def build_robustness_summary(results: list[dict]) -> dict:
    """Build robustness summary grouped by degradation type."""

    grouped = defaultdict(list)

    for result in results:
        degradation, severity = parse_degradation(
            result["document"]
        )

        grouped[degradation].append(
            {
                "severity": severity,
                "result": result,
            }
        )

    summary = {}

    for degradation, cases in grouped.items():
        cases.sort(key=lambda item: item["severity"])

        passing_cases = [
            case
            for case in cases
            if case["result"]["status"] == "PASS"
        ]

        failing_cases = [
            case
            for case in cases
            if case["result"]["status"] != "PASS"
        ]

        max_passing_level = (
            max(
                case["severity"]
                for case in passing_cases
            )
            if passing_cases
            else None
        )

        first_failure = (
            min(
                case["severity"]
                for case in failing_cases
            )
            if failing_cases
            else None
        )

        summary[degradation] = {
            "tests": len(cases),
            "passed": len(passing_cases),
            "failed": len(failing_cases),
            "pass_rate": calculate_pass_rate(
                [case["result"] for case in cases]
            ),
            "max_passing_level": max_passing_level,
            "first_failure": first_failure,
        }

    return summary