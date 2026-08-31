"""Convenience wrapper for the canonical evaluation CLI.

The real implementation lives in ``src.evaluate``; this entry
point exists so both
``python run_pipeline.py ...`` and
``python -m src.evaluate ...`` invoke the same code path.
"""

from src.evaluate import main


if __name__ == "__main__":
    main()
