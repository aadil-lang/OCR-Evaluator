FIELD_SEVERITY = {
    "owner_name": "CRITICAL",
    "father_name": "HIGH",
    "survey_number": "CRITICAL",
    "area": "CRITICAL",
    "village": "HIGH",
    "tehsil": "HIGH",
    "district": "HIGH",
    "registration_number": "CRITICAL",
}


def assess_risk(field_results: dict) -> dict:
    """Determine document risk from field-level evaluation results."""

    failed_fields = []

    for field, result in field_results.items():
        if not result["match"]:
            failed_fields.append(
                {
                    "field": field,
                    "severity": FIELD_SEVERITY.get(
                        field,
                        "NORMAL",
                    ),
                }
            )

    if not failed_fields:
        status = "PASS"
    elif any(
        item["severity"] == "CRITICAL"
        for item in failed_fields
    ):
        status = "FAIL"
    else:
        status = "REVIEW"

    return {
        "status": status,
        "failed_fields": failed_fields,
    }
