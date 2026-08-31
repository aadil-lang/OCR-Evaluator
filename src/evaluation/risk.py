from src.evaluation.fields import (
    FIELD_SEVERITY,
    LOW_CONFIDENCE_THRESHOLD,
)


__all__ = [
    "FIELD_SEVERITY",
    "LOW_CONFIDENCE_THRESHOLD",
    "assess_risk",
]


def assess_risk(field_results: dict) -> dict:
    """Determine document risk from field-level evaluation results.

    Risk rules:

    1. A field mismatch creates a FIELD_MISMATCH risk.
    2. A CRITICAL field mismatch causes FAIL.
    3. A HIGH field mismatch causes REVIEW.
    4. A field with low OCR confidence causes REVIEW.
    5. CRITICAL field mismatch always takes priority over
       low-confidence warnings.
    6. Missing confidence (None) does not create a risk.
    """

    failed_fields = []
    low_confidence_fields = []

    for field, result in field_results.items():
        match = result.get("match", False)
        confidence = result.get("confidence")

        severity = FIELD_SEVERITY.get(
            field,
            "NORMAL",
        )

        # --------------------------------------------------
        # Field mismatch
        # --------------------------------------------------
        if not match:
            failed_fields.append(
                {
                    "field": field,
                    "severity": severity,
                    "reason": "FIELD_MISMATCH",
                }
            )

        # --------------------------------------------------
        # Low OCR confidence
        # --------------------------------------------------
        if (
            confidence is not None
            and confidence < LOW_CONFIDENCE_THRESHOLD
        ):
            low_confidence_fields.append(
                {
                    "field": field,
                    "confidence": confidence,
                    "threshold": LOW_CONFIDENCE_THRESHOLD,
                    "severity": severity,
                    "reason": "LOW_CONFIDENCE",
                }
            )

    # ------------------------------------------------------
    # Determine overall status
    # ------------------------------------------------------

    # Any critical field mismatch means the document fails.
    if any(
        item["severity"] == "CRITICAL"
        for item in failed_fields
    ):
        status = "FAIL"

    # Any field mismatch or low-confidence result requires
    # human review when there is no critical failure.
    elif failed_fields or low_confidence_fields:
        status = "REVIEW"

    else:
        status = "PASS"

    return {
        "status": status,
        "failed_fields": failed_fields,
        "low_confidence_fields": low_confidence_fields,
    }
