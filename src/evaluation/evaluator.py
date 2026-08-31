import json
from pathlib import Path

from src.evaluation.confidence import (
    calculate_all_field_confidence_details,
)
from src.evaluation.critical_fields import (
    calculate_critical_field_accuracy,
)
from src.evaluation.extractor import extract_fields
from src.evaluation.faithfulness import (
    detect_unsupported_fields,
    extract_source_field_value,
)
from src.evaluation.fields import FIELD_LABELS
from src.evaluation.metrics import (
    calculate_cer,
    calculate_wer,
    calculate_field_accuracy,
)
from src.evaluation.risk import assess_risk
from src.ocr.engine import OCREngine


__all__ = [
    "FIELD_LABELS",
    "extract_raw_field_value",
    "DocumentEvaluator",
]


def extract_raw_field_value(
    field: str,
    text: str,
) -> str:
    """Extract the raw OCR value associated with a field label."""

    return extract_source_field_value(
        field,
        text,
    )


class DocumentEvaluator:
    """Evaluate OCR output against a ground-truth document."""

    def __init__(self, ocr_engine: OCREngine):
        self.ocr_engine = ocr_engine

    def load_ground_truth(
        self,
        ground_truth_path: str,
    ) -> dict:
        """Load ground-truth JSON."""

        path = Path(ground_truth_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Ground-truth file not found: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def evaluate(
        self,
        image_path: str,
        ground_truth_path: str,
    ) -> dict:
        """Run OCR and calculate evaluation metrics."""

        ground_truth = self.load_ground_truth(
            ground_truth_path
        )

        ocr_result = self.ocr_engine.extract(
            image_path
        )

        predicted_text = ocr_result["text"]
        reference_text = ground_truth["transcription"]

        predicted_fields = extract_fields(
            predicted_text
        )

        expected_fields = ground_truth["fields"]

        # Calculate accuracy for all structured fields.
        field_results = calculate_field_accuracy(
            expected_fields,
            predicted_fields,
        )

        # Calculate accuracy specifically for critical fields.
        critical_field_results = (
            calculate_critical_field_accuracy(
                expected_fields,
                predicted_fields,
            )
        )

        # Calculate detailed OCR confidence for each extracted
        # field. The plain confidence map is derived from the
        # same details, so the matching loop runs once.
        field_confidence_details = (
            calculate_all_field_confidence_details(
                predicted_fields,
                ocr_result["words"],
            )
        )

        # Attach confidence and OCR matching metadata
        # to each evaluated field.
        for field, result in field_results["fields"].items():
            details = field_confidence_details.get(
                field,
                {},
            )

            result["confidence"] = details.get("confidence")

            result["raw_ocr_value"] = (
                extract_raw_field_value(
                    field,
                    predicted_text,
                )
            )

            result["normalization_applied"] = (
                details.get(
                    "normalization_applied",
                    False,
                )
            )

            result["matched_words"] = (
                details.get("matched_words", [])
            )

        # Check whether extracted values are supported
        # by their corresponding OCR source fields.
        faithfulness = detect_unsupported_fields(
            predicted_fields,
            predicted_text,
        )

        # Determine document-level risk.
        risk = assess_risk(
            field_results["fields"]
        )

        return {
            "document": Path(image_path).name,

            # Text-level quality
            "cer": calculate_cer(
                reference_text,
                predicted_text,
            ),
            "wer": calculate_wer(
                reference_text,
                predicted_text,
            ),

            # Document-level OCR confidence
            "confidence": ocr_result["confidence"],

            # Structured field quality
            "field_accuracy": field_results["accuracy"],
            "fields": field_results["fields"],

            # Critical-field quality
            "critical_field_accuracy": (
                critical_field_results["accuracy"]
            ),
            "critical_fields": (
                critical_field_results["fields"]
            ),
            "critical_failed_fields": (
                critical_field_results["failed_fields"]
            ),

            # Risk / trust signals
            "status": risk["status"],
            "failed_fields": risk["failed_fields"],
            "low_confidence_fields": (
                risk["low_confidence_fields"]
            ),
            "faithfulness": faithfulness,

            # Raw OCR output
            "ocr_text": predicted_text,
        }
