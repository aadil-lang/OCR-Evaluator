from pathlib import Path

from src.evaluation.evaluator import DocumentEvaluator


ERROR_STATUS = "ERROR"


def make_error_result(document_name: str, error: str) -> dict:
    """Build a per-document error record.

    A document that cannot be evaluated (missing ground truth,
    unreadable image, OCR failure) is reported as an ERROR result
    so the surrounding documents are still evaluated.
    """

    return {
        "document": document_name,
        "status": ERROR_STATUS,
        "error": error,
        "cer": None,
        "wer": None,
        "confidence": None,
        "field_accuracy": None,
        "fields": {},
        "critical_field_accuracy": None,
        "critical_fields": {},
        "critical_failed_fields": [],
        "failed_fields": [],
        "low_confidence_fields": [],
        "faithfulness": {},
        "ocr_text": "",
    }


class BatchEvaluator:
    """Evaluate multiple documents against matching ground-truth files."""

    def __init__(self, ocr_engine):
        self.document_evaluator = DocumentEvaluator(
            ocr_engine
        )

    def evaluate_directory(
        self,
        documents_directory: str,
        ground_truth_directory: str,
    ) -> list[dict]:
        """Evaluate all supported documents in a directory.

        Each document is scored only against its own
        ``<stem>.json`` ground-truth file. A document with a
        missing ground truth or a failed evaluation is recorded
        as an ERROR result; the batch continues with the
        remaining documents.
        """

        documents_path = Path(documents_directory)
        ground_truth_path = Path(ground_truth_directory)

        if not documents_path.exists():
            raise FileNotFoundError(
                f"Documents directory not found: "
                f"{documents_path}"
            )

        if not ground_truth_path.exists():
            raise FileNotFoundError(
                f"Ground-truth directory not found: "
                f"{ground_truth_path}"
            )

        results = []

        image_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".tif",
            ".tiff",
            ".bmp",
        }

        image_paths = sorted(
            path
            for path in documents_path.iterdir()
            if path.is_file()
            and path.suffix.lower() in image_extensions
        )

        for image_path in image_paths:
            ground_truth_file = (
                ground_truth_path
                / f"{image_path.stem}.json"
            )

            if not ground_truth_file.exists():
                results.append(
                    make_error_result(
                        image_path.name,
                        "Ground-truth file not found: "
                        f"{ground_truth_file.name}",
                    )
                )

                continue

            try:
                result = self.document_evaluator.evaluate(
                    image_path=str(image_path),
                    ground_truth_path=str(
                        ground_truth_file
                    ),
                )
            except Exception as exc:
                results.append(
                    make_error_result(
                        image_path.name,
                        str(exc),
                    )
                )

                continue

            results.append(result)

        return results
