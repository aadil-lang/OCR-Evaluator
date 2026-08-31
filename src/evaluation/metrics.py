from src.evaluation.normalization import (
    normalize_for_match,
    normalize_text,
)

from jiwer import cer, wer


__all__ = [
    "normalize_text",
    "calculate_cer",
    "calculate_wer",
    "exact_match",
    "calculate_field_accuracy",
]


def calculate_cer(reference: str, hypothesis: str) -> float:
    """Calculate Character Error Rate."""

    reference = normalize_text(reference)
    hypothesis = normalize_text(hypothesis)

    return cer(reference, hypothesis)


def calculate_wer(reference: str, hypothesis: str) -> float:
    """Calculate Word Error Rate."""

    reference = normalize_text(reference)
    hypothesis = normalize_text(hypothesis)

    return wer(reference, hypothesis)


def exact_match(reference: str, hypothesis: str) -> bool:
    """Check whether two field values match after normalization.

    Uses the dash-space-aware normalizer so that
    ``REG - 2026 - 00128`` and ``REG-2026-00128`` compare as
    equal; CER/WER keep the spacing-preserving
    ``normalize_text``.
    """

    return normalize_for_match(reference) == normalize_for_match(hypothesis)


def calculate_field_accuracy(
    ground_truth: dict,
    prediction: dict
) -> dict:
    """Calculate exact-match accuracy for structured fields."""

    results = {}

    for field, expected in ground_truth.items():
        actual = prediction.get(field, "")

        results[field] = {
            "expected": expected,
            "actual": actual,
            "match": exact_match(expected, actual)
        }

    total = len(results)
    correct = sum(
        result["match"]
        for result in results.values()
    )

    accuracy = correct / total if total else 0.0

    return {
        "fields": results,
        "accuracy": accuracy
    }
