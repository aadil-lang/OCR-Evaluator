import json
from pathlib import Path

from src.evaluation.extractor import extract_fields
from src.evaluation.faithfulness import detect_unsupported_fields
from src.evaluation.metrics import (
    calculate_cer,
    calculate_wer,
    calculate_field_accuracy,
)
from src.evaluation.risk import assess_risk
from src.ocr.engine import OCREngine


class DocumentEvaluator:
    """Evaluate OCR output against a ground-truth document."""

    def __init__(self, ocr_engine: OCREngine):
        self.ocr_engine = ocr_engine

    def load_ground_truth(self, ground_truth_path: str) -> dict:
        """Load ground-truth JSON."""

        path = Path(ground_truth_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Ground-truth file not found: {path}"
            )

        with path.open("r", encoding="utf-8") as file:
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

        field_results = calculate_field_accuracy(
            expected_fields,
            predicted_fields,
        )

        faithfulness = detect_unsupported_fields(
            predicted_fields,
            predicted_text,
        )

        risk = assess_risk(
            field_results["fields"]
        )

        return {
            "document": Path(image_path).name,
            "cer": calculate_cer(
                reference_text,
                predicted_text,
            ),
            "wer": calculate_wer(
                reference_text,
                predicted_text,
            ),
            "field_accuracy": field_results["accuracy"],
            "status": risk["status"],
            "failed_fields": risk["failed_fields"],
            "fields": field_results["fields"],
            "faithfulness": faithfulness,
            "ocr_text": predicted_text,
        }
