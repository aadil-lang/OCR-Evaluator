from pathlib import Path

import pytesseract
from PIL import Image


class OCREngine:
    """OCR engine wrapper providing text and confidence information.

    A single Tesseract pass (``image_to_data``) provides both the
    word-level confidences and the full text, which is
    reconstructed from the same data to avoid a second OCR pass.
    """

    def __init__(self, language: str = "eng"):
        self.language = language

    def extract(self, image_path: str) -> dict:
        """Run OCR and return text with word-level confidence data."""

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = Image.open(image_path)

        data = pytesseract.image_to_data(
            image,
            lang=self.language,
            output_type=pytesseract.Output.DICT,
        )

        words = []
        lines: dict[tuple, list[str]] = {}
        line_order: list[tuple] = []

        for index, raw_word in enumerate(data["text"]):
            word = raw_word.strip()

            try:
                confidence = float(data["conf"][index])
            except (ValueError, TypeError):
                confidence = -1.0

            if not word:
                continue

            if confidence >= 0:
                words.append(
                    {
                        "text": word,
                        "confidence": confidence,
                    }
                )

            line_key = (
                data["block_num"][index],
                data["par_num"][index],
                data["line_num"][index],
            )

            if line_key not in lines:
                lines[line_key] = []
                line_order.append(line_key)

            lines[line_key].append(word)

        text = "\n".join(
            " ".join(lines[line_key])
            for line_key in line_order
        )

        confidences = [
            word["confidence"]
            for word in words
        ]

        average_confidence = (
            sum(confidences) / len(confidences)
            if confidences
            else 0.0
        )

        return {
            "document": image_path.name,
            "text": text,
            "confidence": average_confidence,
            "words": words,
        }
