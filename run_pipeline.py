import argparse
from pathlib import Path

from src.evaluation.batch_evaluator import BatchEvaluator
from src.ocr.engine import OCREngine
from src.reporting.report_generator import ReportGenerator


def parse_arguments():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Evaluate OCR performance across documents."
    )

    parser.add_argument(
        "--documents",
        required=True,
        help="Directory containing document images.",
    )

    parser.add_argument(
        "--ground-truth",
        required=True,
        help="Directory containing ground-truth JSON files.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path where the JSON report will be written.",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    print("=" * 60)
    print("OCR EVALUATION PIPELINE")
    print("=" * 60)

    ocr_engine = OCREngine(
        language="eng"
    )

    evaluator = BatchEvaluator(
        ocr_engine
    )

    results = evaluator.evaluate_directory(
        documents_directory=args.documents,
        ground_truth_directory=args.ground_truth,
    )

    report_generator = ReportGenerator()

    report = report_generator.generate(
        results=results,
        output_path=args.output,
    )

    summary = report["summary"]

    print()
    print(f"Documents: {summary['total_documents']}")
    print(f"Processed: {summary['total_documents']}")
    print()
    print(f"PASS:   {summary['passed']}")
    print(f"REVIEW: {summary['review']}")
    print(f"FAIL:   {summary['failed']}")
    print()
    print(
        f"Average CER:             "
        f"{summary['average_cer']:.4f}"
    )
    print(
        f"Average WER:             "
        f"{summary['average_wer']:.4f}"
    )
    print(
        f"Average Field Accuracy:  "
        f"{summary['average_field_accuracy']:.2%}"
    )
    print()
    print(f"Report: {Path(args.output)}")
    print("=" * 60)


if __name__ == "__main__":
    main()