import json
from pathlib import Path

from src.evaluation.robustness import build_robustness_summary


class ReportGenerator:
    """Generate evaluation reports from document results."""

    def generate(
        self,
        results: list[dict],
        output_path: str,
    ) -> dict:
        """Generate and save a JSON evaluation report."""

        output = Path(output_path)

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        summary = self._build_summary(results)
        robustness = build_robustness_summary(results)

        report = {
            "summary": summary,
            "robustness": robustness,
            "documents": results,
        }

        with output.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False,
            )

        return report

    def _build_summary(
        self,
        results: list[dict],
    ) -> dict:
        """Build aggregate evaluation statistics."""

        total_documents = len(results)

        passed = sum(
            1
            for result in results
            if result["status"] == "PASS"
        )

        review = sum(
            1
            for result in results
            if result["status"] == "REVIEW"
        )

        failed = sum(
            1
            for result in results
            if result["status"] == "FAIL"
        )

        if total_documents:
            average_cer = round(
                sum(
                    result["cer"]
                    for result in results
                ) / total_documents,
                4,
            )

            average_wer = round(
                sum(
                    result["wer"]
                    for result in results
                ) / total_documents,
                4,
            )

            average_field_accuracy = round(
                sum(
                    result["field_accuracy"]
                    for result in results
                ) / total_documents,
                4,
            )
        else:
            average_cer = 0.0
            average_wer = 0.0
            average_field_accuracy = 0.0

        return {
            "total_documents": total_documents,
            "passed": passed,
            "review": review,
            "failed": failed,
            "average_cer": average_cer,
            "average_wer": average_wer,
            "average_field_accuracy": (
                average_field_accuracy
            ),
        }