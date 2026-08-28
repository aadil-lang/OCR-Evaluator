CRITICAL_FIELDS = {
    "owner_name",
    "survey_number",
    "area",
    "registration_number",
}

HIGH_FIELDS = {
    "father_name",
    "village",
    "tehsil",
    "district",
}


def calculate_critical_field_accuracy(
    expected_fields: dict,
    predicted_fields: dict,
) -> dict:
    """Calculate accuracy specifically for legally important fields."""

    results = {}

    for field in CRITICAL_FIELDS:
        expected = expected_fields.get(field)
        actual = predicted_fields.get(field)

        results[field] = {
            "expected": expected,
            "actual": actual,
            "match": (
                expected is not None
                and actual is not None
                and expected.strip() == actual.strip()
            ),
        }

    total = len(results)

    correct = sum(
        1
        for result in results.values()
        if result["match"]
    )

    accuracy = (
        correct / total
        if total
        else 0.0
    )

    failed = [
        field
        for field, result in results.items()
        if not result["match"]
    ]

    return {
        "accuracy": accuracy,
        "fields": results,
        "failed_fields": failed,
    }
