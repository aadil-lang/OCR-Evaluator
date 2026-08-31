import json
from pathlib import Path


class RobustnessManifest:
    """Load and validate a robustness experiment manifest."""

    REQUIRED_FIELDS = {
        "experiment",
        "version",
        "ground_truth",
        "tests",
    }

    TEST_REQUIRED_FIELDS = {
        "document",
        "degradation",
        "severity",
    }

    def __init__(self, manifest_path: str):
        self.path = Path(manifest_path)

        if not self.path.exists():
            raise FileNotFoundError(
                f"Manifest not found: {self.path}"
            )

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as file:
            self.data = json.load(file)

        self._validate()

    def _validate(self) -> None:
        """Validate the manifest structure."""

        if not isinstance(self.data, dict):
            raise ValueError(
                "Manifest root must be a JSON object."
            )

        missing = (
            self.REQUIRED_FIELDS
            - self.data.keys()
        )

        if missing:
            raise ValueError(
                "Manifest missing required fields: "
                f"{sorted(missing)}"
            )

        if not isinstance(
            self.data["tests"],
            list,
        ):
            raise ValueError(
                "Manifest 'tests' must be a list."
            )

        for index, test in enumerate(
            self.data["tests"]
        ):
            if not isinstance(test, dict):
                raise ValueError(
                    f"Manifest test at index {index} "
                    "must be an object."
                )

            missing_test_fields = (
                self.TEST_REQUIRED_FIELDS
                - test.keys()
            )

            if missing_test_fields:
                raise ValueError(
                    f"Manifest test at index {index} "
                    "missing required fields: "
                    f"{sorted(missing_test_fields)}"
                )

            if not isinstance(
                test["document"],
                str,
            ):
                raise ValueError(
                    f"Manifest test at index {index} "
                    "'document' must be a string."
                )

            if not isinstance(
                test["degradation"],
                str,
            ):
                raise ValueError(
                    f"Manifest test at index {index} "
                    "'degradation' must be a string."
                )

            if not isinstance(
                test["severity"],
                (int, float, str),
            ):
                raise ValueError(
                    f"Manifest test at index {index} "
                    "'severity' must be numeric or a string."
                )

    @property
    def experiment(self) -> str:
        return self.data["experiment"]

    @property
    def version(self) -> str:
        return self.data["version"]

    @property
    def ground_truth(self) -> str:
        return self.data["ground_truth"]

    @property
    def baseline(self) -> str | None:
        return self.data.get("baseline")

    @property
    def tests(self) -> list[dict]:
        return self.data["tests"]

    def get_test(self, document: str) -> dict | None:
        """Return metadata for a document in the experiment."""

        for test in self.tests:
            if test["document"] == document:
                return test

        return None