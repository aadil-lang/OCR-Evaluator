from pathlib import Path

import pytest

from src.ocr.engine import OCREngine


IMAGE_PATH = Path("data/documents/test_document.png")


@pytest.fixture
def ocr_engine():
    return OCREngine(language="eng")


def test_sample_document_exists():
    assert IMAGE_PATH.exists()


def test_ocr_returns_document_name(ocr_engine):
    result = ocr_engine.extract(str(IMAGE_PATH))

    assert result["document"] == IMAGE_PATH.name


def test_ocr_returns_text(ocr_engine):
    result = ocr_engine.extract(str(IMAGE_PATH))

    assert isinstance(result["text"], str)
    assert result["text"].strip() != ""


def test_ocr_detects_expected_content(ocr_engine):
    result = ocr_engine.extract(str(IMAGE_PATH))

    text = result["text"].lower()

    assert "owner" in text
    assert "survey" in text
    assert "area" in text


def test_missing_image_raises_error(ocr_engine):
    with pytest.raises(FileNotFoundError):
        ocr_engine.extract(
            "data/documents/does_not_exist.png"
        )
