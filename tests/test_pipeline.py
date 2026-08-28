import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_pipeline_help():
    result = subprocess.run(
        [
            sys.executable,
            "run_pipeline.py",
            "--help",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--documents" in result.stdout
    assert "--ground-truth" in result.stdout
    assert "--output" in result.stdout


def test_pipeline_runs_successfully(tmp_path):
    output_path = tmp_path / "evaluation_report.json"

    result = subprocess.run(
        [
            sys.executable,
            "run_pipeline.py",
            "--documents",
            "data/documents",
            "--ground-truth",
            "data/ground_truth",
            "--output",
            str(output_path),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert output_path.exists()
    assert "OCR EVALUATION PIPELINE" in result.stdout