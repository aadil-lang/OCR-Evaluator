from src.evaluation.fields import (
    HIGH_CONFIDENCE_THRESHOLD,
    LOW_CONFIDENCE_THRESHOLD,
)


__all__ = [
    "HIGH_CONFIDENCE_THRESHOLD",
    "LOW_CONFIDENCE_THRESHOLD",
    "analyze_confidence_correctness",
    "analyze_results",
]


def analyze_confidence_correctness(result: dict) -> dict:
    """
    Analyze whether OCR confidence is consistent with
    the evaluated document outcome.
    """

    confidence = result.get("confidence")
    status = result.get("status")

    if confidence is None:
        return {
            "category": "UNAVAILABLE",
            "confidence": None,
            "status": status,
            "message": "OCR confidence is unavailable.",
        }

    if status == "FAIL" and confidence >= HIGH_CONFIDENCE_THRESHOLD:
        return {
            "category": "HIGH_CONFIDENCE_FAILURE",
            "confidence": confidence,
            "status": status,
            "message": (
                "OCR reported high confidence despite "
                "the document failing evaluation."
            ),
        }

    if status == "PASS" and confidence < LOW_CONFIDENCE_THRESHOLD:
        return {
            "category": "LOW_CONFIDENCE_PASS",
            "confidence": confidence,
            "status": status,
            "message": (
                "OCR reported low confidence despite "
                "the document passing evaluation."
            ),
        }

    return {
        "category": "ALIGNED",
        "confidence": confidence,
        "status": status,
        "message": (
            "OCR confidence is reasonably aligned "
            "with the evaluation outcome."
        ),
    }


def analyze_results(results: list[dict]) -> dict:
    """Analyze confidence/correctness alignment across documents.

    Documents recorded as ERROR are skipped: they have no OCR
    confidence or evaluated outcome to analyze.
    """

    analysis = {
        "total_documents": len(results),
        "high_confidence_failures": 0,
        "low_confidence_passes": 0,
        "aligned": 0,
        "unavailable": 0,
        "documents": [],
    }

    for result in results:
        if result.get("status") == "ERROR":
            continue

        confidence_analysis = analyze_confidence_correctness(
            result
        )

        category = confidence_analysis["category"]

        if category == "HIGH_CONFIDENCE_FAILURE":
            analysis["high_confidence_failures"] += 1

        elif category == "LOW_CONFIDENCE_PASS":
            analysis["low_confidence_passes"] += 1

        elif category == "ALIGNED":
            analysis["aligned"] += 1

        elif category == "UNAVAILABLE":
            analysis["unavailable"] += 1

        analysis["documents"].append(
            {
                "document": result["document"],
                **confidence_analysis,
            }
        )

    return analysis
