from pathlib import Path

from src.evaluation.evaluator import DocumentEvaluator
from src.evaluation.manifest import RobustnessManifest


class RobustnessRunner:
    """Run an OCR robustness experiment from a manifest."""

    def __init__(self, ocr_engine):
        self.document_evaluator = DocumentEvaluator(
            ocr_engine
        )

    def run(
        self,
        manifest_path: str,
        images_directory: str,
        ground_truth_directory: str,
    ) -> list[dict]:
        """Evaluate every test defined in a robustness manifest."""

        manifest = RobustnessManifest(manifest_path)

        images_path = Path(images_directory)
        ground_truth_path = Path(ground_truth_directory)

        if not images_path.exists():
            raise FileNotFoundError(
                f"Robustness images directory not found: "
                f"{images_path}"
            )

        if not ground_truth_path.exists():
            raise FileNotFoundError(
                f"Ground-truth directory not found: "
                f"{ground_truth_path}"
            )

        results = []

        for test in manifest.tests:
            document = test["document"]

            image_path = images_path / document

            if not image_path.exists():
                raise FileNotFoundError(
                    f"Robustness image not found: "
                    f"{image_path}"
                )

            ground_truth_file = (
                test.get("ground_truth")
                or manifest.ground_truth
            )

            ground_truth_path_for_test = (
                ground_truth_path
                / ground_truth_file
            )

            if not ground_truth_path_for_test.exists():
                raise FileNotFoundError(
                    f"Ground-truth file not found: "
                    f"{ground_truth_path_for_test}"
                )

            result = self.document_evaluator.evaluate(
                image_path=str(image_path),
                ground_truth_path=str(
                    ground_truth_path_for_test
                ),
            )

            # Metadata comes from the manifest,
            # not from the filename.
            result["robustness"] = {
                "degradation": test["degradation"],
                "severity": test["severity"],
                "baseline": test.get(
                    "baseline",
                    manifest.baseline,
                ),
            }

            results.append(result)

        return results