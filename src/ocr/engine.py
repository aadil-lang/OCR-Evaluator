from pathlib import Path

import pytesseract
from PIL import Image


class OCREngine:
    """OCR engine wrapper providing a standardized interface."""

    def __init__(self, language: str = "eng"):
        self.language = language

    def extract(self, image_path: str) -> dict:
        """Run OCR on an image and return the extracted text."""

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = Image.open(image_path)

        text = pytesseract.image_to_string(
            image,
            lang=self.language
        )

        return {
            "document": image_path.name,
            "text": text,
        }
