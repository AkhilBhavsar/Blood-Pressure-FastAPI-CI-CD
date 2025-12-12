"""
Basic security-oriented tests for the deployed application.

These tests check that invalid inputs are handled safely (returning 400 rather
than 500) and that unexpected paths return 404 instead of leaking internal
errors. This is a lightweight, repeatable "mini pen test" for the CD pipeline.
"""

import os

import httpx


def get_base_url() -> str:
    return os.getenv("BASE_URL", "http://127.0.0.1:8000")


def test_invalid_range_returns_400():
    """
    Out-of-range values should not be accepted and should return HTTP 400
    with a useful error message (not a 500).
    """
    base_url = get_base_url()
    # systolic below 70 and diastolic below 40 should be rejected
    response = httpx.get(
        f"{base_url}/api/classify",
        params={"systolic": 50, "diastolic": 30},
        timeout=5.0,
    )

    assert response.status_code == 400
    body = response.json()
    # Just check that some detail is present
    assert "detail" in body
    assert isinstance(body["detail"], str)
    assert body["detail"] != ""


def test_equal_systolic_diastolic_returns_400():
    """
    According to the business rules, systolic must be greater than diastolic.
    Equal values should be rejected with HTTP 400 rather than causing a crash.
    """
    base_url = get_base_url()
    response = httpx.get(
        f"{base_url}/api/classify",
        params={"systolic": 80, "diastolic": 80},
        timeout=5.0,
    )

    assert response.status_code == 400
    body = response.json()
    # This should match your ValueError message in classify_blood_pressure
    assert "must be higher than diastolic" in body["detail"]


def test_unexpected_path_returns_404_not_500():
    """
    Accessing a strange path should return 404, not 500, and should not expose
    internal stack traces.
    """
    base_url = get_base_url()
    response = httpx.get(f"{base_url}/../../etc/passwd", timeout=5.0)

    assert response.status_code == 404
    # We don't want to see typical stack trace markers in the body
    if response.text:
        assert "Traceback" not in response.text
        assert "Exception" not in response.text

def test_many_invalid_requests_do_not_break_the_app():
    """
    Send a burst of invalid requests to simulate a simple abuse scenario.
    The app should consistently return 400 responses and never 500s.
    """
    base_url = get_base_url()
    with httpx.Client(timeout=5.0) as client:
        for _ in range(50):
            response = client.get(
                f"{base_url}/api/classify",
                params={"systolic": 9999, "diastolic": -10},
            )
            assert response.status_code == 400
            body = response.json()
            assert "detail" in body


def test_error_responses_do_not_leak_stack_traces():
    """
    For deliberately bad inputs we should see controlled error messages,
    not Python stack traces or internal framework details.
    """
    base_url = get_base_url()
    responses = []

    # Invalid range
    responses.append(
        httpx.get(
            f"{base_url}/api/classify",
            params={"systolic": 10, "diastolic": 5},
            timeout=5.0,
        )
    )
    # Equal systolic/diastolic
    responses.append(
        httpx.get(
            f"{base_url}/api/classify",
            params={"systolic": 80, "diastolic": 80},
            timeout=5.0,
        )
    )

    for resp in responses:
        assert resp.status_code in (400, 422)
        text = resp.text or ""
        assert "Traceback" not in text
        assert "File &quot;" not in text
        assert "Exception" not in text


def test_security_headers_present_on_responses():
    """
    All normal responses should include basic security headers such as
    X-Frame-Options and X-Content-Type-Options.
    """
    base_url = get_base_url()
    response = httpx.get(f"{base_url}/", timeout=5.0)

    assert response.status_code == 200
    headers = response.headers
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-Content-Type-Options") == "nosniff"