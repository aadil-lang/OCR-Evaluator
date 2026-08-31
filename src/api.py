import os
import secrets
import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.evaluation.evaluator import DocumentEvaluator
from src.ocr.engine import OCREngine


DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

ALLOWED_UPLOAD_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
}


def resolve_cors_origins() -> list:
    """Read CORS origins from the OCR_API_CORS_ORIGINS environment variable.

    The value is a comma-separated list of origins. When the variable is
    unset or empty, the default Vite dev-server origins are used.
    """

    raw_value = os.environ.get("OCR_API_CORS_ORIGINS", "")
    origins = [
        origin.strip()
        for origin in raw_value.split(",")
        if origin.strip()
    ]

    return origins or DEFAULT_CORS_ORIGINS


def default_ground_truth_path() -> Path:
    """Locate the sample ground-truth document used by the demo API."""

    project_root = Path(__file__).resolve().parent.parent
    return (
        project_root
        / "data"
        / "ground_truth"
        / "test_document.json"
    )


def create_app(
    ocr_engine=None,
    default_ground_truth=None,
    cors_origins=None,
) -> FastAPI:
    """Build the FastAPI application.

    A single OCREngine is created once and shared by all requests.
    Tests can inject a fake engine and a custom ground-truth path.
    """

    app = FastAPI(
        title="OCR Evaluation API",
        description=(
            "Backend API for OCR evaluation and risk assessment."
        ),
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=(
            cors_origins if cors_origins is not None
            else resolve_cors_origins()
        ),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    engine = ocr_engine or OCREngine()
    evaluator = DocumentEvaluator(engine)

    ground_truth_path = (
        Path(default_ground_truth)
        if default_ground_truth is not None
        else default_ground_truth_path()
    )

    @app.get("/")
    def root():
        return {
            "name": "OCR Evaluation API",
            "status": "running",
        }

    @app.get("/health")
    def health():
        return {
            "status": "healthy",
        }

    @app.post("/evaluate")
    async def evaluate_document(
        file: UploadFile = File(...),
    ):
        if not file.filename or not file.filename.strip():
            raise HTTPException(
                status_code=400,
                detail="No file provided.",
            )

        suffix = Path(file.filename).suffix.lower()

        if suffix not in ALLOWED_UPLOAD_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Only PNG and JPEG images are supported."
                ),
            )

        if not ground_truth_path.exists():
            raise HTTPException(
                status_code=404,
                detail=(
                    "Ground-truth file not found: "
                    f"{ground_truth_path}"
                ),
            )

        # The client-controlled filename is never used on disk;
        # a generated name keeps uploads inside the temp directory.
        safe_name = f"upload_{secrets.token_hex(8)}{suffix}"

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                image_path = Path(temp_dir) / safe_name

                with image_path.open("wb") as output_file:
                    shutil.copyfileobj(
                        file.file,
                        output_file,
                    )

                result = evaluator.evaluate(
                    str(image_path),
                    str(ground_truth_path),
                )
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Evaluation failed: {exc}",
            )

        return {
            "document": result["document"],
            "status": result["status"],
            "summary": {
                "confidence": result["confidence"],
                "cer": result["cer"],
                "wer": result["wer"],
                "field_accuracy": result["field_accuracy"],
                "critical_field_accuracy": (
                    result["critical_field_accuracy"]
                ),
            },
            "fields": {
                field_name: {
                    "value": field_data.get("actual"),
                    "confidence": field_data.get("confidence"),
                }
                for field_name, field_data
                in result["fields"].items()
            },
            "risk": {
                "status": result["status"],
                "failed_fields": result["failed_fields"],
                "low_confidence_fields": (
                    result["low_confidence_fields"]
                ),
            },
            "ocr_text": result["ocr_text"],
        }

    return app


app = create_app()
