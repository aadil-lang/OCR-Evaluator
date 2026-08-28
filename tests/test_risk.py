from src.evaluation.risk import assess_risk


def test_all_fields_passing_returns_pass():
    field_results = {
        "owner_name": {"match": True},
        "survey_number": {"match": True},
        "area": {"match": True},
        "registration_number": {"match": True},
    }

    result = assess_risk(field_results)

    assert result["status"] == "PASS"
    assert result["failed_fields"] == []


def test_critical_field_failure_returns_fail():
    field_results = {
        "owner_name": {"match": True},
        "survey_number": {"match": False},
        "area": {"match": True},
        "registration_number": {"match": True},
    }

    result = assess_risk(field_results)

    assert result["status"] == "FAIL"
    assert len(result["failed_fields"]) == 1
    assert result["failed_fields"][0]["field"] == "survey_number"
    assert result["failed_fields"][0]["severity"] == "CRITICAL"


def test_high_field_failure_returns_review():
    field_results = {
        "owner_name": {"match": True},
        "survey_number": {"match": True},
        "area": {"match": True},
        "registration_number": {"match": True},
        "village": {"match": False},
    }

    result = assess_risk(field_results)

    assert result["status"] == "REVIEW"
    assert len(result["failed_fields"]) == 1
    assert result["failed_fields"][0]["field"] == "village"
    assert result["failed_fields"][0]["severity"] == "HIGH"


def test_critical_failure_overrides_high_failure():
    field_results = {
        "owner_name": {"match": True},
        "survey_number": {"match": False},
        "area": {"match": True},
        "registration_number": {"match": True},
        "village": {"match": False},
    }

    result = assess_risk(field_results)

    assert result["status"] == "FAIL"
    assert len(result["failed_fields"]) == 2