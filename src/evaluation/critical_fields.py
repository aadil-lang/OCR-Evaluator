from src.evaluation.fields import CRITICAL_FIELDS
from src.evaluation.metrics import exact_match


__all__ = [
    "CRITICAL_FIELDS",
    "calculate_critical_field_accuracy",
]


def calculate_critical_field_accuracy(
    expected_fields: dict,
    predicted_fields: dict,
) -> dict:
    """Calculate accuracy specifically for legally important fields.

    Critical-field comparison uses the same normalization policy
    as the general field evaluator so that equivalent OCR
    representations are evaluated consistently.
    """

    results = {}

    for field in CRITICAL_FIELDS:
        expected = expected_fields.get(field)
        actual = predicted_fields.get(field)

        results[field] = {
            "expected": expected,
            "actual": actual,
            "match": (
                expected is not None
                and actual is not None
                and exact_match(expected, actual)
            ),
        }

    total = len(results)

    correct = sum(
        1
        for result in results.values()
        if result["match"]
    )

    accuracy = (
        correct / total
        if total
        else 0.0
    )

    failed = [
        field
        for field, result in results.items()
        if not result["match"]
    ]

    return {
        "accuracy": accuracy,
        "fields": results,
        "failed_fields": failed,
    }
