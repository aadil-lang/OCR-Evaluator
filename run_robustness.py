import argparse
import json
from pathlib import Path

from src.evaluation.robustness import build_robustness_summary
from src.evaluation.robustness_runner import RobustnessRunner
from src.ocr.engine import OCREngine
from src.reporting.robustness_report import RobustnessReportGenerator


def parse_arguments():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Run OCR robustness evaluation from a manifest."
    )

    parser.add_argument(
        "--manifest",
        required=True,
        help="Path to the robustness experiment manifest.",
    )

    parser.add_argument(
        "--images",
        required=True,
        help="Directory containing robustness test images.",
    )

    parser.add_argument(
        "--ground-truth",
        required=True,
        help="Directory containing ground-truth JSON files.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path where the JSON robustness report will be written.",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    print("=" * 60)
    print("OCR ROBUSTNESS EVALUATION")
    print("=" * 60)

    ocr_engine = OCREngine(
        language="eng"
    )

    runner = RobustnessRunner(
        ocr_engine
    )

    results = runner.run(
        manifest_path=args.manifest,
        images_directory=args.images,
        ground_truth_directory=args.ground_truth,
    )

    summary = build_robustness_summary(
        results
    )

    output_path = Path(args.output)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = {
        "experiment": "OCR robustness evaluation",
        "manifest": str(args.manifest),
        "tests": len(results),
        "robustness": summary,
        "results": results,
    }

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
        )

    markdown_path = output_path.with_suffix(
        ".md"
    )

    RobustnessReportGenerator().generate(
        robustness_summary=summary,
        output_path=str(markdown_path),
    )

    print()
    print(f"Tests: {len(results)}")
    print()

    for degradation, data in summary.items():
        max_accurate = data["max_accurate_level"]
        first_accuracy_failure = data[
            "first_accuracy_failure"
        ]

        max_accurate_text = (
            f"{max_accurate:g}"
            if max_accurate is not None
            else "None"
        )

        first_accuracy_failure_text = (
            f"{first_accuracy_failure:g}"
            if first_accuracy_failure is not None
            else "None"
        )

        print(
            f"{degradation}: "
            f"{data['tests']} tests | "
            f"OCR accuracy: {data['accuracy_rate']:.1%} | "
            f"PASS: {data['passed']} | "
            f"REVIEW: {data['review']} | "
            f"FAIL: {data['failed']} | "
            f"Max accurate: {max_accurate_text} | "
            f"First accuracy failure: "
            f"{first_accuracy_failure_text}"
        )

    print()
    print(
        "Note: OCR accuracy and operational status are "
        "reported separately."
    )
    print()

    print(f"JSON report: {output_path}")
    print(f"Markdown report: {markdown_path}")

    print("=" * 60)


if __name__ == "__main__":
    main()