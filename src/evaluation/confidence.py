from typing import Optional

from src.evaluation.normalization import normalize_token


__all__ = [
    "normalize_token",
    "calculate_field_confidence",
    "calculate_field_confidence_details",
    "calculate_all_field_confidences",
    "calculate_all_field_confidence_details",
]


def calculate_field_confidence(
    field_value: str,
    words: list[dict],
) -> Optional[float]:
    """Calculate average OCR confidence for a field value."""

    details = calculate_field_confidence_details(
        field_value,
        words,
    )

    return details["confidence"]


def calculate_field_confidence_details(
    field_value: str,
    words: list[dict],
) -> dict:
    """
    Calculate OCR confidence and matching details for a field.

    The raw OCR confidence is preserved. Normalization is reported
    separately rather than artificially increasing the confidence.
    """

    if not field_value:
        return {
            "confidence": None,
            "matched_words": [],
            "normalization_applied": False,
        }

    field_words = field_value.split()

    matched_words = []
    normalization_applied = False

    for field_word in field_words:
        normalized_field_word = normalize_token(
            field_word
        )

        for word in words:
            raw_ocr_word = word["text"]
            normalized_ocr_word = normalize_token(
                raw_ocr_word
            )

            if normalized_ocr_word == normalized_field_word:
                matched_words.append(
                    {
                        "field_word": field_word,
                        "raw_ocr_word": raw_ocr_word,
                        "confidence": word["confidence"],
                    }
                )

                if raw_ocr_word != field_word:
                    normalization_applied = True

                break

    confidences = [
        item["confidence"]
        for item in matched_words
    ]

    confidence = (
        sum(confidences) / len(confidences)
        if confidences
        else None
    )

    return {
        "confidence": confidence,
        "matched_words": matched_words,
        "normalization_applied": normalization_applied,
    }


def calculate_all_field_confidences(
    fields: dict,
    words: list[dict],
) -> dict:
    """Calculate OCR confidence for every extracted field."""

    return {
        field: calculate_field_confidence(
            value,
            words,
        )
        for field, value in fields.items()
    }


def calculate_all_field_confidence_details(
    fields: dict,
    words: list[dict],
) -> dict:
    """Calculate detailed OCR confidence information for every field."""

    return {
        field: calculate_field_confidence_details(
            value,
            words,
        )
        for field, value in fields.items()
    }
