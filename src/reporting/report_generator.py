import json
from pathlib import Path

from src.evaluation.robustness import build_robustness_summary
from src.evaluation.confidence_analysis import analyze_results


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
        confidence_analysis = analyze_results(results)

        report = {
            "summary": summary,
            "robustness": robustness,
            "confidence_analysis": confidence_analysis,
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
        """Build aggregate evaluation statistics.

        Documents recorded as ERROR (missing ground truth or a
        failed evaluation) are counted separately and excluded
        from the average metrics.
        """

        total_documents = len(results)

        evaluated = [
            result
            for result in results
            if result.get("status") != "ERROR"
        ]

        passed = sum(
            1
            for result in evaluated
            if result["status"] == "PASS"
        )

        review = sum(
            1
            for result in evaluated
            if result["status"] == "REVIEW"
        )

        failed = sum(
            1
            for result in evaluated
            if result["status"] == "FAIL"
        )

        errors = total_documents - len(evaluated)

        if evaluated:
            average_cer = round(
                sum(
                    result["cer"]
                    for result in evaluated
                ) / len(evaluated),
                4,
            )

            average_wer = round(
                sum(
                    result["wer"]
                    for result in evaluated
                ) / len(evaluated),
                4,
            )

            average_field_accuracy = round(
                sum(
                    result["field_accuracy"]
                    for result in evaluated
                ) / len(evaluated),
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
            "errors": errors,
            "average_cer": average_cer,
            "average_wer": average_wer,
            "average_field_accuracy": (
                average_field_accuracy
            ),
        }