from pathlib import Path

import cv2
import numpy as np


SOURCE = Path("data/documents/test_document.png")
OUTPUT_DIR = Path("data/degraded/test_document")


def save_image(name: str, image: np.ndarray) -> None:
    output_path = OUTPUT_DIR / name
    cv2.imwrite(str(output_path), image)
    print(f"Created: {output_path}")


def apply_rotation(
    image: np.ndarray,
    angle: float,
) -> np.ndarray:
    height, width = image.shape[:2]

    matrix = cv2.getRotationMatrix2D(
        (width / 2, height / 2),
        angle,
        1.0,
    )

    return cv2.warpAffine(
        image,
        matrix,
        (width, height),
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )


def apply_jpeg_compression(
    image: np.ndarray,
    quality: int,
) -> np.ndarray:
    encode_params = [
        int(cv2.IMWRITE_JPEG_QUALITY),
        quality,
    ]

    success, encoded = cv2.imencode(
        ".jpg",
        image,
        encode_params,
    )

    if not success:
        raise RuntimeError(
            f"JPEG encoding failed for quality {quality}"
        )

    decoded = cv2.imdecode(
        encoded,
        cv2.IMREAD_COLOR,
    )

    if decoded is None:
        raise RuntimeError(
            f"JPEG decoding failed for quality {quality}"
        )

    return decoded


def apply_noise(
    image: np.ndarray,
    sigma: int,
    rng: np.random.Generator,
) -> np.ndarray:
    noise = rng.normal(
        0,
        sigma,
        image.shape,
    ).astype(np.float32)

    return np.clip(
        image.astype(np.float32) + noise,
        0,
        255,
    ).astype(np.uint8)


def apply_contrast(
    image: np.ndarray,
    alpha: float,
    beta: int,
) -> np.ndarray:
    return cv2.convertScaleAbs(
        image,
        alpha=alpha,
        beta=beta,
    )


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Source document not found: {SOURCE}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    image = cv2.imread(str(SOURCE))

    if image is None:
        raise ValueError(
            f"Could not read source image: {SOURCE}"
        )

    rng = np.random.default_rng(42)

    print("=" * 60)
    print("CREATING OCR DEGRADATION DATASET")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Blur
    # ---------------------------------------------------------

    blur_levels = {
        3: (3, 3),
        7: (7, 7),
        11: (11, 11),
        15: (15, 15),
    }

    for severity, kernel in blur_levels.items():
        degraded = cv2.GaussianBlur(
            image,
            kernel,
            0,
        )

        save_image(
            f"blur_{severity}.png",
            degraded,
        )

    # ---------------------------------------------------------
    # 2. Gaussian noise
    # ---------------------------------------------------------

    noise_levels = {
        10: 10,
        25: 25,
        40: 40,
        60: 60,
    }

    for severity, sigma in noise_levels.items():
        degraded = apply_noise(
            image,
            sigma,
            rng,
        )

        save_image(
            f"noise_{severity}.png",
            degraded,
        )

    # ---------------------------------------------------------
    # 3. JPEG compression
    # ---------------------------------------------------------

    jpeg_levels = {
        50: 50,
        20: 20,
        10: 10,
        5: 5,
    }

    for quality, value in jpeg_levels.items():
        degraded = apply_jpeg_compression(
            image,
            value,
        )

        save_image(
            f"jpeg_{quality}.png",
            degraded,
        )

    # ---------------------------------------------------------
    # 4. Rotation
    # ---------------------------------------------------------

    rotation_levels = {
        2: 2,
        5: 5,
        10: 10,
        15: 15,
    }

    for severity, angle in rotation_levels.items():
        degraded = apply_rotation(
            image,
            angle,
        )

        save_image(
            f"rotation_{severity}.png",
            degraded,
        )

    # ---------------------------------------------------------
    # 5. Contrast
    # ---------------------------------------------------------

    contrast_levels = {
        "low": (0.55, 90),
        "medium": (0.70, 70),
        "high": (1.80, -100),
        "extreme": (2.20, -140),
    }

    for severity, (alpha, beta) in contrast_levels.items():
        degraded = apply_contrast(
            image,
            alpha,
            beta,
        )

        save_image(
            f"contrast_{severity}.png",
            degraded,
        )

    print()
    print("=" * 60)
    print("DEGRADATION DATASET CREATED")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()