from pathlib import Path


class RobustnessReportGenerator:
    """Generate a human-readable Markdown robustness report."""

    def generate(
        self,
        robustness_summary: dict,
        output_path: str,
    ) -> None:
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
            "| Degradation | Tests | Passed | Failed | Pass Rate | Max Passing Level | First Failure |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]

        for degradation, data in robustness_summary.items():
            max_passing = (
                f"{data['max_passing_level']:g}"
                if data["max_passing_level"] is not None
                else "N/A"
            )

            first_failure = (
                f"{data['first_failure']:g}"
                if data["first_failure"] is not None
                else "N/A"
            )

            pass_rate = f"{data['pass_rate']:.1%}"

            lines.append(
                f"| {degradation} "
                f"| {data['tests']} "
                f"| {data['passed']} "
                f"| {data['failed']} "
                f"| {pass_rate} "
                f"| {max_passing} "
                f"| {first_failure} |"
            )

        lines.extend(
            [
                "",
                "## Interpretation",
                "",
                "The robustness evaluation measures how OCR performance changes "
                "under controlled image degradations.",
                "",
                "- **Max Passing Level** indicates the highest tested severity "
                "that still passed evaluation.",
                "- **First Failure** indicates the lowest tested severity "
                "that produced a non-PASS result.",
                "- A higher pass rate indicates greater robustness to that "
                "degradation type.",
                "",
            ]
        )

        output.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )