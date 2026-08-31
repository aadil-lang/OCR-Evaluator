import json
from pathlib import Path

from src.evaluation.evaluator import DocumentEvaluator


GROUND_TRUTH_PATH = Path(
    "data/ground_truth/test_document.json"
)

IMAGE_PATH = "data/documents/test_document.png"


class FakeOCREngine:
    """Deterministic OCR engine for adversarial evaluation tests."""

    def __init__(
        self,
        text: str,
        confidence: float = 95.0,
        words: list[dict] | None = None,
    ):
        self.text = text
        self.confidence = confidence
        self.words = words or self._build_words(
            text,
            confidence,
        )

    @staticmethod
    def _build_words(
        text: str,
        confidence: float,
    ) -> list[dict]:
        return [
            {
                "text": word,
                "confidence": confidence,
            }
            for word in text.split()
        ]

    def extract(self, image_path: str) -> dict:
        return {
            "document": Path(image_path).name,
            "text": self.text,
            "confidence": self.confidence,
            "words": self.words,
        }


def load_ground_truth() -> dict:
    """Load the real ground-truth document."""

    with GROUND_TRUTH_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def build_text(
    *,
    owner_name: str | None = None,
    father_name: str | None = None,
    survey_number: str | None = None,
    area: str | None = None,
    village: str | None = None,
    tehsil: str | None = None,
    district: str | None = None,
    registration_number: str | None = None,
) -> str:
    """Build OCR text using the actual ground-truth values by default."""

    fields = load_ground_truth()["fields"]

    owner_name = (
        fields["owner_name"]
        if owner_name is None
        else owner_name
    )

    father_name = (
        fields["father_name"]
        if father_name is None
        else father_name
    )

    survey_number = (
        fields["survey_number"]
        if survey_number is None
        else survey_number
    )

    area = (
        fields["area"]
        if area is None
        else area
    )

    village = (
        fields["village"]
        if village is None
        else village
    )

    tehsil = (
        fields["tehsil"]
        if tehsil is None
        else tehsil
    )

    district = (
        fields["district"]
        if district is None
        else district
    )

    registration_number = (
        fields["registration_number"]
        if registration_number is None
        else registration_number
    )

    return f"""
SALE DEED

Owner Name: {owner_name}
Father Name: {father_name}
Survey Number: {survey_number}
Area: {area}
Village: {village}
Tehsil: {tehsil}
District: {district}
Registration Number: {registration_number}
""".strip()


def test_correct_document_with_high_confidence_passes():
    """Correct fields and high OCR confidence should PASS."""

    text = build_text()

    evaluator = DocumentEvaluator(
        FakeOCREngine(
            text=text,
            confidence=95.0,
        )
    )

    result = evaluator.evaluate(
        image_path=IMAGE_PATH,
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    assert result["status"] == "PASS"
    assert result["critical_failed_fields"] == []
    assert result["failed_fields"] == []
    assert result["low_confidence_fields"] == []


def test_correct_critical_field_with_low_confidence_requires_review():
    """A correct critical field with low confidence should require REVIEW."""

    text = build_text()

    words = [
        {
            "text": word,
            "confidence": (
                40.0
                if word == "128/3"
                else 95.0
            ),
        }
        for word in text.split()
    ]

    evaluator = DocumentEvaluator(
        FakeOCREngine(
            text=text,
            confidence=95.0,
            words=words,
        )
    )

    result = evaluator.evaluate(
        image_path=IMAGE_PATH,
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    assert result["status"] == "REVIEW"

    low_confidence_fields = {
        item["field"]
        for item in result["low_confidence_fields"]
    }

    assert "survey_number" in low_confidence_fields
    assert result["critical_failed_fields"] == []


def test_wrong_critical_field_causes_fail():
    """A wrong critical field must cause FAIL."""

    text = build_text(
        survey_number="128/8",
    )

    evaluator = DocumentEvaluator(
        FakeOCREngine(
            text=text,
            confidence=98.0,
        )
    )

    result = evaluator.evaluate(
        image_path=IMAGE_PATH,
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    assert result["status"] == "FAIL"

    assert "survey_number" in result["critical_failed_fields"]

    failed_fields = {
        item["field"]
        for item in result["failed_fields"]
    }

    assert "survey_number" in failed_fields


def test_wrong_high_severity_field_causes_review():
    """A wrong HIGH-severity field should require REVIEW."""

    text = build_text(
        village="Lakshmi Nagar",
    )

    evaluator = DocumentEvaluator(
        FakeOCREngine(
            text=text,
            confidence=98.0,
        )
    )

    result = evaluator.evaluate(
        image_path=IMAGE_PATH,
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    assert result["status"] == "REVIEW"

    failed_fields = {
        item["field"]
        for item in result["failed_fields"]
    }

    assert "village" in failed_fields

    assert result["critical_failed_fields"] == []


def test_missing_critical_field_causes_fail():
    """A missing critical field should cause FAIL."""

    text = build_text().replace(
        "Survey Number: 128/3",
        "",
    )

    evaluator = DocumentEvaluator(
        FakeOCREngine(
            text=text,
            confidence=95.0,
        )
    )

    result = evaluator.evaluate(
        image_path=IMAGE_PATH,
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    assert result["status"] == "FAIL"
    assert "survey_number" in result["critical_failed_fields"]


def test_missing_high_severity_field_causes_review():
    """A missing HIGH-severity field should cause REVIEW."""

    text = build_text().replace(
        "Village: Rampur",
        "",
    )

    evaluator = DocumentEvaluator(
        FakeOCREngine(
            text=text,
            confidence=95.0,
        )
    )

    result = evaluator.evaluate(
        image_path=IMAGE_PATH,
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    assert result["status"] == "REVIEW"

    failed_fields = {
        item["field"]
        for item in result["failed_fields"]
    }

    assert "village" in failed_fields


def test_critical_failure_overrides_low_confidence():
    """A critical mismatch must remain FAIL despite low confidence elsewhere."""

    text = build_text(
        survey_number="128/8",
    )

    words = [
        {
            "text": word,
            "confidence": (
                35.0
                if word == "Rampur"
                else 95.0
            ),
        }
        for word in text.split()
    ]

    evaluator = DocumentEvaluator(
        FakeOCREngine(
            text=text,
            confidence=95.0,
            words=words,
        )
    )

    result = evaluator.evaluate(
        image_path=IMAGE_PATH,
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    assert result["status"] == "FAIL"

    assert "survey_number" in result["critical_failed_fields"]

    low_confidence_fields = {
        item["field"]
        for item in result["low_confidence_fields"]
    }

    assert "village" in low_confidence_fields


def test_multiple_failures_preserve_highest_risk():
    """Multiple failures should preserve the highest severity decision."""

    text = build_text(
        survey_number="128/8",
        village="Lakshmi Nagar",
        district="Lucknow",
    )

    evaluator = DocumentEvaluator(
        FakeOCREngine(
            text=text,
            confidence=95.0,
        )
    )

    result = evaluator.evaluate(
        image_path=IMAGE_PATH,
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    assert result["status"] == "FAIL"

    failed_fields = {
        item["field"]
        for item in result["failed_fields"]
    }

    assert "survey_number" in failed_fields
    assert "village" in failed_fields
    assert "district" in failed_fields

    assert "survey_number" in result["critical_failed_fields"]


def test_missing_confidence_does_not_create_low_confidence_risk():
    """Missing field confidence should not automatically create REVIEW."""

    text = build_text()

    # Simulate an OCR engine that provides no usable
    # word-level confidence for the extracted fields.
    words = []

    evaluator = DocumentEvaluator(
        FakeOCREngine(
            text=text,
            confidence=95.0,
            words=words,
        )
    )

    result = evaluator.evaluate(
        image_path=IMAGE_PATH,
        ground_truth_path=str(GROUND_TRUTH_PATH),
    )

    assert result["status"] == "PASS"
    assert result["low_confidence_fields"] == []