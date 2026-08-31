import argparse
from pathlib import Path

from src.evaluation.batch_evaluator import BatchEvaluator
from src.ocr.engine import OCREngine
from src.reporting.report_generator import ReportGenerator
from src.reporting.robustness_report import (
    RobustnessReportGenerator,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate OCR performance on a document dataset."
    )

    parser.add_argument(
        "--documents",
        required=True,
        help="Directory containing input document images.",
    )

    parser.add_argument(
        "--ground-truth",
        required=True,
        help="Directory containing matching ground-truth JSON files.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path where the evaluation report will be written.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    documents_directory = Path(args.documents)
    ground_truth_directory = Path(args.ground_truth)
    output_path = Path(args.output)

    if not documents_directory.exists():
        raise FileNotFoundError(
            f"Documents directory not found: {documents_directory}"
        )

    if not ground_truth_directory.exists():
        raise FileNotFoundError(
            f"Ground-truth directory not found: {ground_truth_directory}"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 70)
    print("OCR EVALUATION PIPELINE")
    print("=" * 70)
    print(f"Documents   : {documents_directory}")
    print(f"Ground truth: {ground_truth_directory}")
    print(f"Output      : {output_path}")
    print()

    ocr = OCREngine(language="eng")

    evaluator = BatchEvaluator(ocr)

    results = evaluator.evaluate_directory(
        documents_directory=str(documents_directory),
        ground_truth_directory=str(ground_truth_directory),
    )

    report_generator = ReportGenerator()

    report = report_generator.generate(
        results,
        str(output_path),
    )

    robustness_report_generator = RobustnessReportGenerator()

    robustness_report_path = (
        output_path.parent / "robustness_report.md"
    )

    robustness_report_generator.generate(
        report["robustness"],
        str(robustness_report_path),
    )

    summary = report["summary"]

    print()
    print("=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"Documents evaluated : "
        f"{summary['total_documents']}"
    )

    print(
        f"PASS                : "
        f"{summary['passed']}"
    )

    print(
        f"REVIEW              : "
        f"{summary['review']}"
    )

    print(
        f"FAIL                : "
        f"{summary['failed']}"
    )

    if summary["errors"]:
        print(
            f"ERROR               : "
            f"{summary['errors']}"
        )

        for result in results:
            if result.get("status") == "ERROR":
                print(
                    f"  - {result['document']}: "
                    f"{result['error']}"
                )

    print(
        f"Average CER         : "
        f"{summary['average_cer']:.4f}"
    )

    print(
        f"Average WER         : "
        f"{summary['average_wer']:.4f}"
    )

    print(
        f"Average field accuracy: "
        f"{summary['average_field_accuracy']:.2%}"
    )

    print()
    print(f"Report written to: {output_path}")
    print(
        f"Robustness report written to: "
        f"{robustness_report_path}"
    )


if __name__ == "__main__":
    main()