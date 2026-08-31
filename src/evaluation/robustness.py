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
    """Parse legacy degradation metadata from a filename."""

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


def get_robustness_metadata(
    result: dict,
) -> tuple[str, float] | None:
    """Read explicit robustness metadata."""

    metadata = result.get("robustness")

    if not metadata:
        return None

    degradation_type = (
        metadata.get("degradation")
        or metadata.get("type")
    )

    if not degradation_type:
        return None

    label = DEGRADATION_TYPES.get(
        str(degradation_type).lower(),
        str(degradation_type).title(),
    )

    severity = metadata.get("severity")

    if severity is None:
        severity = 0.0

    if isinstance(severity, str):
        numeric_severity = CONTRAST_SEVERITY.get(
            severity.lower()
        )

        if numeric_severity is not None:
            severity = numeric_severity
        else:
            try:
                severity = float(severity)
            except ValueError:
                severity = 0.0
    else:
        try:
            severity = float(severity)
        except (TypeError, ValueError):
            severity = 0.0

    return label, severity


def get_degradation_metadata(
    result: dict,
) -> tuple[str, float] | None:
    """Resolve robustness metadata.

    Explicit metadata is authoritative. Legacy filename parsing is
    used only when explicit metadata is absent.
    """

    explicit_metadata = get_robustness_metadata(result)

    if explicit_metadata is not None:
        return explicit_metadata

    document_name = result.get("document", "")

    degradation, severity = parse_degradation(
        document_name
    )

    if degradation == "Unknown":
        return None

    return degradation, severity


def calculate_pass_rate(results: list[dict]) -> float:
    """Calculate the percentage of documents with PASS status."""

    if not results:
        return 0.0

    passed = sum(
        result["status"] == "PASS"
        for result in results
    )

    return passed / len(results)


def is_accuracy_pass(result: dict) -> bool:
    """Determine whether OCR extraction is actually correct."""

    return (
        result.get("field_accuracy", 0.0) == 1.0
        and result.get("critical_field_accuracy", 0.0) == 1.0
        and not result.get("failed_fields")
        and not result.get("critical_failed_fields")
    )


def build_robustness_summary(results: list[dict]) -> dict:
    """Build a risk-aware robustness summary."""

    grouped = defaultdict(list)

    for result in results:
        # Documents that could not be evaluated carry no
        # metrics and are excluded from the degradation curves.
        if result.get("status") == "ERROR":
            continue

        metadata = get_degradation_metadata(result)

        if metadata is None:
            continue

        degradation, severity = metadata

        grouped[degradation].append(
            {
                "severity": severity,
                "result": result,
            }
        )

    summary = {}

    for degradation, cases in grouped.items():
        cases.sort(
            key=lambda item: item["severity"]
        )

        case_results = [
            case["result"]
            for case in cases
        ]

        passed_cases = [
            case
            for case in cases
            if case["result"]["status"] == "PASS"
        ]

        review_cases = [
            case
            for case in cases
            if case["result"]["status"] == "REVIEW"
        ]

        failed_cases = [
            case
            for case in cases
            if case["result"]["status"] == "FAIL"
        ]

        accurate_cases = [
            case
            for case in cases
            if is_accuracy_pass(case["result"])
        ]

        inaccurate_cases = [
            case
            for case in cases
            if not is_accuracy_pass(case["result"])
        ]

        max_passing_level = (
            max(
                case["severity"]
                for case in passed_cases
            )
            if passed_cases
            else None
        )

        first_failure = (
            min(
                case["severity"]
                for case in failed_cases
            )
            if failed_cases
            else None
        )

        max_accurate_level = (
            max(
                case["severity"]
                for case in accurate_cases
            )
            if accurate_cases
            else None
        )

        first_accuracy_failure = (
            min(
                case["severity"]
                for case in inaccurate_cases
            )
            if inaccurate_cases
            else None
        )

        # ---------------------------------------------------------
        # Aggregate quality metrics
        # ---------------------------------------------------------

        average_cer = (
            sum(
                result.get("cer", 0.0)
                for result in case_results
            )
            / len(case_results)
            if case_results
            else 0.0
        )

        average_wer = (
            sum(
                result.get("wer", 0.0)
                for result in case_results
            )
            / len(case_results)
            if case_results
            else 0.0
        )

        average_field_accuracy = (
            sum(
                result.get("field_accuracy", 0.0)
                for result in case_results
            )
            / len(case_results)
            if case_results
            else 0.0
        )

        average_critical_field_accuracy = (
            sum(
                result.get(
                    "critical_field_accuracy",
                    0.0,
                )
                for result in case_results
            )
            / len(case_results)
            if case_results
            else 0.0
        )

        available_confidences = [
            result["confidence"]
            for result in case_results
            if result.get("confidence") is not None
        ]

        average_confidence = (
            sum(available_confidences)
            / len(available_confidences)
            if available_confidences
            else None
        )

        # ---------------------------------------------------------
        # Per-severity measurements
        # ---------------------------------------------------------

        severity_results = []

        for case in cases:
            result = case["result"]

            severity_results.append(
                {
                    "severity": case["severity"],
                    "cer": result.get("cer", 0.0),
                    "wer": result.get("wer", 0.0),
                    "field_accuracy": result.get(
                        "field_accuracy",
                        0.0,
                    ),
                    "critical_field_accuracy": result.get(
                        "critical_field_accuracy",
                        0.0,
                    ),
                    "confidence": result.get(
                        "confidence"
                    ),
                    "status": result.get("status"),
                    "accurate": is_accuracy_pass(result),
                }
            )

        summary[degradation] = {
            "tests": len(cases),

            # Operational outcome
            "passed": len(passed_cases),
            "review": len(review_cases),
            "failed": len(failed_cases),
            "pass_rate": calculate_pass_rate(
                case_results
            ),

            # OCR correctness
            "accurate": len(accurate_cases),
            "inaccurate": len(inaccurate_cases),
            "accuracy_rate": (
                len(accurate_cases) / len(cases)
                if cases
                else 0.0
            ),

            # Aggregate quality
            "average_cer": average_cer,
            "average_wer": average_wer,
            "average_field_accuracy": (
                average_field_accuracy
            ),
            "average_critical_field_accuracy": (
                average_critical_field_accuracy
            ),
            "average_confidence": average_confidence,

            # Thresholds
            "max_passing_level": max_passing_level,
            "first_failure": first_failure,
            "max_accurate_level": max_accurate_level,
            "first_accuracy_failure": first_accuracy_failure,

            # Detailed degradation curve
            "severity_results": severity_results,
        }

    return summary