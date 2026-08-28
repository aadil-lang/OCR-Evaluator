from pathlib import Path

from src.evaluation.evaluator import DocumentEvaluator
from src.evaluation.robustness import build_robustness_summary


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
        """Evaluate all supported documents in a directory."""

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
            # First try an exact filename match.
            ground_truth_file = (
                ground_truth_path
                / f"{image_path.stem}.json"
            )

            # Degraded variants use the original document's
            # ground truth.
            if not ground_truth_file.exists():
                ground_truth_file = (
                    ground_truth_path
                    / "test_document.json"
                )

            if not ground_truth_file.exists():
                raise FileNotFoundError(
                    f"Ground-truth file not found for "
                    f"{image_path.name}"
                )

            result = self.document_evaluator.evaluate(
                image_path=str(image_path),
                ground_truth_path=str(
                    ground_truth_file
                ),
            )

            results.append(result)

        return results