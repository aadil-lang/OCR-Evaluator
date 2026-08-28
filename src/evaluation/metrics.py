import re
from jiwer import wer, cer


def normalize_text(text: str) -> str:
    """Normalize OCR and ground-truth text before comparison."""

    text = text.lower()

    # Normalize common dash variants and OCR encoding artifacts.
    text = text.replace("—", "-")
    text = text.replace("–", "-")
    text = text.replace("â€”", "-")
    text = text.replace("â€“", "-")

    # Collapse repeated dash separators introduced by OCR.
    text = re.sub(r"-{2,}", "-", text)

    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    return text

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
    """Check whether two field values match after normalization."""

    return normalize_text(reference) == normalize_text(hypothesis)


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
