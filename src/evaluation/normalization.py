"""Centralized text normalization for OCR comparison.

OCR output routinely contains dash variants (em/en dashes, the
Unicode minus sign) and mojibake from double-decoding UTF-8
through Windows-1252. This module is the single place that
maps those artifacts to plain hyphens so that equivalent
values compare as equal in every metric.

Four scopes are exposed:

- ``normalize_text``: full-text comparison (CER/WER,
  faithfulness).
- ``normalize_for_match``: exact field-value match (adds
  dash-space stripping).
- ``clean_value``: extracted field values (the extractor and
  the raw-value reader).
- ``normalize_token``: single-word matching for OCR
  confidence (adds punctuation stripping).

All four apply the same dash/mojibake table, so the two
sides of every comparison normalize consistently. Dash
artifacts are matched on the raw text before case-folding:
the double-mojibake sequences begin with a case-sensitive
letter (U+00C3), so lowercasing first would defeat the
match.
"""

import re


# Dash artifacts observed in OCR output, mapped to "-".
# Order matters: longer (double-mojibake) sequences first so
# they are consumed before their shorter sub-sequences.
# The sequences look identical when printed; the codepoint
# for each entry is given in its comment.
DASH_REPLACEMENTS = (
    # Double-mojibake em dash (U+2014 through cp1252 twice):
    # U+00C3 U+00A2 U+00E2 U+201A U+00AC U+00E2 U+20AC U+201D
    "Ã¢â‚¬â€”",
    # Double-mojibake en dash (U+2013 through cp1252 twice):
    # U+00C3 U+00A2 U+00E2 U+201A U+00AC U+00E2 U+20AC U+0153
    "Ã¢â‚¬â€œ",
    # Single-mojibake em dash: U+00E2 U+20AC U+201D
    "â€”",
    # Single-mojibake en dash: U+00E2 U+20AC U+201C
    "â€“",
    # Actual Unicode dash characters.
    "—",
    "–",
    "−",
)


_REPEATED_DASHES = re.compile(r"-{2,}")
_WHITESPACE = re.compile(r"\s+")
_DASH_SPACES = re.compile(r"\s*-\s*")
_TOKEN_PUNCTUATION = ".,;:!?()[]{}\"'"


def apply_dash_replacements(text: str) -> str:
    """Replace all known dash artifacts with a plain hyphen."""

    for artifact in DASH_REPLACEMENTS:
        text = text.replace(artifact, "-")

    return _REPEATED_DASHES.sub("-", text)


def normalize_text(text: str) -> str:
    """Normalize full text for comparison.

    Maps dash artifacts to hyphens, lowercases, collapses
    repeated whitespace. Dash replacement runs before
    case-folding because the artifacts are case-sensitive.
    """

    text = apply_dash_replacements(text)

    text = text.lower()

    text = _WHITESPACE.sub(" ", text)
    text = text.strip()

    return text


def normalize_for_match(text: str) -> str:
    """Normalize a field value for exact-match comparison.

    Like ``normalize_text``, but also removes whitespace
    around dash separators so that ``REG - 2026 - 00128``
    and ``REG-2026-00128`` compare as equal. Used by
    ``exact_match``; CER/WER keep the spacing-preserving
    ``normalize_text``.
    """

    text = apply_dash_replacements(text)

    text = text.lower()

    text = _DASH_SPACES.sub("-", text)

    text = _WHITESPACE.sub(" ", text)
    text = text.strip()

    return text


def clean_value(value: str) -> str:
    """Clean an extracted field value.

    Applies dash replacement (without lowercasing, to preserve
    the value's original casing) and removes accidental
    whitespace around dash separators so that
    ``REG - 2026 - 00128`` and ``REG-2026-00128`` compare as
    equal.
    """

    value = value.strip()

    value = apply_dash_replacements(value)

    value = _DASH_SPACES.sub("-", value)

    return value.strip()


def normalize_token(token: str) -> str:
    """Normalize a single OCR word for confidence matching.

    Applies dash replacement, lowercases, and strips
    surrounding punctuation while preserving meaningful
    characters such as the slash in ``128/3``.
    """

    token = token.strip()

    token = apply_dash_replacements(token)

    token = token.lower()

    token = token.strip(_TOKEN_PUNCTUATION)

    return token
