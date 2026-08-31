from src.evaluation.risk import assess_risk


def test_all_fields_passing_returns_pass():
    field_results = {
        "owner_name": {
            "match": True,
            "confidence": 95.0,
        },
        "survey_number": {
            "match": True,
            "confidence": 96.0,
        },
        "area": {
            "match": True,
            "confidence": 94.0,
        },
        "registration_number": {
            "match": True,
            "confidence": 97.0,
        },
    }

    result = assess_risk(field_results)

    assert result["status"] == "PASS"
    assert result["failed_fields"] == []
    assert result["low_confidence_fields"] == []


def test_critical_field_failure_returns_fail():
    field_results = {
        "owner_name": {
            "match": True,
            "confidence": 95.0,
        },
        "survey_number": {
            "match": False,
            "confidence": 96.0,
        },
        "area": {
            "match": True,
            "confidence": 94.0,
        },
        "registration_number": {
            "match": True,
            "confidence": 97.0,
        },
    }

    result = assess_risk(field_results)

    assert result["status"] == "FAIL"
    assert len(result["failed_fields"]) == 1
    assert result["failed_fields"][0]["field"] == "survey_number"
    assert result["failed_fields"][0]["severity"] == "CRITICAL"
    assert result["failed_fields"][0]["reason"] == "FIELD_MISMATCH"


def test_high_field_failure_returns_review():
    field_results = {
        "owner_name": {
            "match": True,
            "confidence": 95.0,
        },
        "survey_number": {
            "match": True,
            "confidence": 96.0,
        },
        "area": {
            "match": True,
            "confidence": 94.0,
        },
        "registration_number": {
            "match": True,
            "confidence": 97.0,
        },
        "village": {
            "match": False,
            "confidence": 88.0,
        },
    }

    result = assess_risk(field_results)

    assert result["status"] == "REVIEW"
    assert len(result["failed_fields"]) == 1
    assert result["failed_fields"][0]["field"] == "village"
    assert result["failed_fields"][0]["severity"] == "HIGH"
    assert result["failed_fields"][0]["reason"] == "FIELD_MISMATCH"


def test_critical_failure_overrides_high_failure():
    field_results = {
        "owner_name": {
            "match": True,
            "confidence": 95.0,
        },
        "survey_number": {
            "match": False,
            "confidence": 96.0,
        },
        "area": {
            "match": True,
            "confidence": 94.0,
        },
        "registration_number": {
            "match": True,
            "confidence": 97.0,
        },
        "village": {
            "match": False,
            "confidence": 88.0,
        },
    }

    result = assess_risk(field_results)

    assert result["status"] == "FAIL"
    assert len(result["failed_fields"]) == 2


def test_low_confidence_correct_field_requires_review():
    field_results = {
        "owner_name": {
            "match": True,
            "confidence": 95.0,
        },
        "survey_number": {
            "match": True,
            "confidence": 42.0,
        },
        "area": {
            "match": True,
            "confidence": 94.0,
        },
        "registration_number": {
            "match": True,
            "confidence": 97.0,
        },
    }

    result = assess_risk(field_results)

    assert result["status"] == "REVIEW"
    assert result["failed_fields"] == []

    assert len(result["low_confidence_fields"]) == 1
    assert result["low_confidence_fields"][0]["field"] == "survey_number"
    assert result["low_confidence_fields"][0]["confidence"] == 42.0
    assert result["low_confidence_fields"][0]["reason"] == "LOW_CONFIDENCE"


def test_low_confidence_high_field_requires_review():
    field_results = {
        "owner_name": {
            "match": True,
            "confidence": 95.0,
        },
        "village": {
            "match": True,
            "confidence": 45.0,
        },
    }

    result = assess_risk(field_results)

    assert result["status"] == "REVIEW"
    assert result["failed_fields"] == []

    assert len(result["low_confidence_fields"]) == 1
    assert result["low_confidence_fields"][0]["field"] == "village"


def test_low_confidence_does_not_override_critical_failure():
    field_results = {
        "survey_number": {
            "match": False,
            "confidence": 95.0,
        },
        "village": {
            "match": True,
            "confidence": 35.0,
        },
    }

    result = assess_risk(field_results)

    assert result["status"] == "FAIL"

    assert len(result["failed_fields"]) == 1
    assert result["failed_fields"][0]["field"] == "survey_number"

    assert len(result["low_confidence_fields"]) == 1
    assert result["low_confidence_fields"][0]["field"] == "village"


def test_missing_confidence_does_not_create_risk():
    field_results = {
        "owner_name": {
            "match": True,
            "confidence": None,
        },
        "survey_number": {
            "match": True,
            "confidence": None,
        },
    }

    result = assess_risk(field_results)

    assert result["status"] == "PASS"
    assert result["failed_fields"] == []
    assert result["low_confidence_fields"] == []