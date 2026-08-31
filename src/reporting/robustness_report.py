from pathlib import Path


class RobustnessReportGenerator:
    """Generate a human-readable Markdown robustness report."""

    def generate(
        self,
        robustness_summary: dict,
        output_path: str,
    ) -> None:
        """Generate and write the robustness report."""

        output = Path(output_path)

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        lines = [
            "# OCR Robustness Evaluation Report",
            "",
            "## Robustness Summary",
            "",
            (
                "| Degradation | Tests | PASS | REVIEW | FAIL | "
                "Accurate | Inaccurate | Max Accurate Level | "
                "First Accuracy Failure |"
            ),
            (
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|"
            ),
        ]

        for degradation, data in robustness_summary.items():
            max_accurate = (
                f"{data['max_accurate_level']:g}"
                if data["max_accurate_level"] is not None
                else "N/A"
            )

            first_accuracy_failure = (
                f"{data['first_accuracy_failure']:g}"
                if data["first_accuracy_failure"] is not None
                else "N/A"
            )

            lines.append(
                f"| {degradation} "
                f"| {data['tests']} "
                f"| {data['passed']} "
                f"| {data['review']} "
                f"| {data['failed']} "
                f"| {data['accurate']} "
                f"| {data['inaccurate']} "
                f"| {max_accurate} "
                f"| {first_accuracy_failure} |"
            )

        lines.extend(
            [
                "",
                "## Interpretation",
                "",
                (
                    "The robustness evaluation measures how OCR "
                    "performance changes under controlled image "
                    "degradations."
                ),
                "",
                (
                    "- **PASS** indicates that the document passed "
                    "the automated evaluation."
                ),
                (
                    "- **REVIEW** indicates that the extracted "
                    "information is accurate but the result requires "
                    "human review because of confidence or risk rules."
                ),
                (
                    "- **FAIL** indicates that the evaluation detected "
                    "an actual extraction or critical-field failure."
                ),
                (
                    "- **Accurate** indicates that all evaluated fields "
                    "match the ground truth."
                ),
                (
                    "- **Inaccurate** indicates that one or more "
                    "evaluated fields do not match the ground truth."
                ),
                (
                    "- **Max Accurate Level** indicates the highest "
                    "tested severity where extraction remained accurate."
                ),
                (
                    "- **First Accuracy Failure** indicates the lowest "
                    "tested severity where extraction became inaccurate."
                ),
                "",
                (
                    "Operational status and extraction accuracy are "
                    "reported separately because a REVIEW result can "
                    "still contain completely accurate OCR output."
                ),
            ]
        )

        output.write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )