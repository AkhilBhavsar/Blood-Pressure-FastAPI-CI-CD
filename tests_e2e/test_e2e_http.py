"""
End-to-end HTTP tests against a running instance of the application.

These tests assume that the FastAPI app is already running and reachable via
BASE_URL (default: http://127.0.0.1:8000). They exercise the application from
the outside, as a real user or client would.
"""

import os

import httpx


def get_base_url() -> str:
    """
    Return the base URL of the running application.

    In CI/CD, this can be overridden using the BASE_URL environment variable
    to point at the QA deployment (e.g. Azure Web App). By default, we target
    a local instance on port 8000.
    """
    return os.getenv("BASE_URL", "http://127.0.0.1:8000")


def test_home_page_loads():
    """The main HTML form page should load successfully."""
    base_url = get_base_url()
    response = httpx.get(f"{base_url}/", timeout=5.0)

    assert response.status_code == 200
    assert "Blood Pressure Category" in response.text


def test_api_classify_pre_high():
    """
    The JSON API endpoint should classify 100/80 as pre-high blood pressure,
    consistent with the assignment chart and the HTML form.
    """
    base_url = get_base_url()
    response = httpx.get(
        f"{base_url}/api/classify",
        params={"systolic": 100, "diastolic": 80},
        timeout=5.0,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["systolic"] == 100
    assert data["diastolic"] == 80
    assert data["category"] == "Pre-high blood pressure"


def test_form_submission_pre_high():
    """
    Submitting the HTML form with 100/80 should render the correct category
    in the response page, matching the E2E behaviour a user would see.
    """
    base_url = get_base_url()
    response = httpx.post(
        f"{base_url}/calculate",
        data={"systolic": "100", "diastolic": "80"},
        timeout=5.0,
        follow_redirects=True,
    )

    assert response.status_code == 200
    text = response.text
    # Check that the category and formatted reading appear in the HTML
    assert "Pre-high blood pressure" in text
    assert "100/80 mmHg" in text


def test_form_submission_invalid_reading_shows_error():
    """
    Submitting an invalid reading should not crash the app and should show
    a helpful error message instead of a normal category result.
    """
    base_url = get_base_url()
    # systolic <= diastolic is invalid according to our rules
    response = httpx.post(
        f"{base_url}/calculate",
        data={"systolic": "80", "diastolic": "80"},
        timeout=5.0,
        follow_redirects=True,
    )

    assert response.status_code == 200
    text = response.text

    # Expect an error message somewhere in the page
    assert "Invalid reading" in text or "must be higher than diastolic" in text

    # And we should not see a normal category string like "Pre-high blood pressure"
    assert "Pre-high blood pressure" not in text
