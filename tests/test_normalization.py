"""Regression tests for centralized text normalization.

Guards three former bugs:

1. The double-mojibake sequences must be the full 8-character
   form, not a 7-character truncation that left an orphan.
2. Dash artifacts must be replaced on the raw text *before*
   case-folding. The double-mojibake sequences begin with a
   case-sensitive letter (U+00C3); lowercasing first turns it
   into U+00E3 and defeats the match.
3. Dash-space stripping must apply to both sides of an
   exact-match comparison, not just the predicted value.

The mojibake sequences are built at runtime from explicit
codepoint lists so the test source is pure ASCII and cannot be
silently corrupted by an encoding round-trip. The
``test_mojibake_constants_match_cp1252_derivation`` test ties
those codepoints back to real UTF-8/Windows-1252 derivation.
"""

from src.evaluation.metrics import exact_match, calculate_cer
from src.evaluation.normalization import (
    normalize_text,
    normalize_for_match,
    clean_value,
    normalize_token,
)
from src.evaluation.extractor import clean_ocr_value


def seq(*codes):
    """Build a string from explicit codepoints (pure-ASCII source)."""

    return "".join(chr(code) for code in codes)


# --- Dash artifacts under test -------------------------------------------
#
# Single-mojibake: a UTF-8 dash decoded once through Windows-1252.
EM_SINGLE = seq(0x00E2, 0x20AC, 0x201D)   # em dash, one decode
EN_SINGLE = seq(0x00E2, 0x20AC, 0x201C)   # en dash, one decode

# Double-mojibake: decoded a second time through Windows-1252.
EM_DOUBLE = seq(
    0x00C3, 0x00A2, 0x00E2, 0x201A, 0x00AC, 0x00E2, 0x20AC, 0x201D,
)
EN_DOUBLE = seq(
    0x00C3, 0x00A2, 0x00E2, 0x201A, 0x00AC, 0x00E2, 0x20AC, 0x0153,
)

# Actual Unicode dash characters.
EM_DASH = seq(0x2014)
EN_DASH = seq(0x2013)
MINUS = seq(0x2212)


def test_mojibake_constants_match_cp1252_derivation():
    """Self-verify: the codepoint constants must be the real
    UTF-8 -> Windows-1252 artifacts, so a future edit that
    changes them fails here rather than testing the wrong
    bytes."""

    em = seq(0x2014)
    en = seq(0x2013)

    # Single decode (strict cp1252, both defined).
    assert EM_SINGLE == em.encode("utf-8").decode("cp1252")
    assert EN_SINGLE == en.encode("utf-8").decode("cp1252")

    # Double decode of the en dash is strictly defined.
    assert EN_DOUBLE == EN_SINGLE.encode("utf-8").decode("cp1252")

    # The em-dash double decode is NOT strictly defined (0x9D is
    # undefined in cp1252); the Windows best-fit decoder maps it
    # to U+201D, which is what this pipeline's environment
    # produces. Assert the constant's shape rather than deriving
    # it, so the guard still holds across platforms.
    assert EM_DOUBLE[:6] == EN_DOUBLE[:6]
    assert EM_DOUBLE[-1] == seq(0x201D)
    assert len(EM_DOUBLE) == 8


def test_single_mojibake_em_dash():
    assert normalize_text(f"REG{EM_SINGLE}2026") == "reg-2026"
    assert clean_value(f"REG{EM_SINGLE}2026") == "REG-2026"


def test_double_mojibake_em_dash():
    """Regression: the literal must be the full 8-character
    double-mojibake em dash, and it must survive the
    normalize_text path (which lowercases) as well as
    clean_value."""

    assert len(EM_DOUBLE) == 8

    assert normalize_text(f"REG{EM_DOUBLE}2026") == "reg-2026"
    assert clean_value(f"REG{EM_DOUBLE}2026") == "REG-2026"


def test_double_mojibake_en_dash():
    assert len(EN_DOUBLE) == 8

    assert normalize_text(f"REG{EN_DOUBLE}2026") == "reg-2026"
    assert clean_value(f"REG{EN_DOUBLE}2026") == "REG-2026"


def test_unicode_dash_variants():
    assert normalize_text(f"REG{EM_DASH}2026") == "reg-2026"
    assert normalize_text(f"REG{EN_DASH}2026") == "reg-2026"
    assert normalize_text(f"REG{MINUS}2026") == "reg-2026"


def test_normalized_dash_space_equivalence():
    """Regression: dash-space stripping must apply to both
    sides of a comparison, not just the predicted value."""

    ground_truth = "REG - 2026 - 00128"
    prediction = "REG-2026-00128"

    # Exact match is symmetric and dash-space aware.
    assert exact_match(ground_truth, prediction)
    assert exact_match(prediction, ground_truth)

    # Cleaned values are equal in both directions.
    assert clean_value(ground_truth) == clean_value(prediction)

    # The dedicated matcher collapses the spaces around dashes.
    assert (
        normalize_for_match(ground_truth)
        == normalize_for_match(prediction)
    )


def test_cer_of_equivalent_dash_form_is_zero():
    # Full-text comparison of equivalent dash forms must not
    # report errors.
    assert calculate_cer("REG-2026-00128", f"REG{EM_DASH}2026-00128") == 0.0


def test_normalizers_agree_on_dashes():
    """All normalizers must map the same artifacts to hyphens
    so metrics never disagree with each other."""

    text = f"REG{EM_DASH}2026{EN_DASH}00128{MINUS}999"

    normalized = normalize_text(text)
    cleaned = clean_value(text)
    tokens = [normalize_token(part) for part in text.split()]

    for target in (normalized, cleaned, *tokens):
        assert EM_DASH not in target
        assert EN_DASH not in target
        assert MINUS not in target
        assert EM_SINGLE not in target
        assert EN_SINGLE not in target

    assert "-" in normalized
    assert "-" in cleaned


def test_token_normalization_strips_punctuation():
    assert normalize_token('"(Daniel).') == "daniel"


def test_clean_ocr_value_is_the_shared_clean_value():
    # Backward-compatible alias must be the same function.
    assert clean_ocr_value is clean_value
