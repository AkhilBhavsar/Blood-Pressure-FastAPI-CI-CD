"""
API-level tests for the FastAPI blood pressure calculator.

These tests use TestClient to exercise the HTML endpoints and verify that a
known reading (100/80) is classified as pre-high blood pressure.
"""

import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_home_page_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "Blood Pressure Category" in response.text


def test_post_pre_high_reading():
    response = client.post(
        "/calculate",
        data={"systolic": 100, "diastolic": 80},
    )
    assert response.status_code == 200
    assert "Pre-high blood pressure" in response.text
    assert "100/80 mmHg" in response.text


def test_api_classify_pre_high():
    response = client.get("/api/classify", params={"systolic": 100, "diastolic": 80})
    assert response.status_code == 200
    data = response.json()
    assert data["systolic"] == 100
    assert data["diastolic"] == 80
    assert data["category"] == "Pre-high blood pressure"


def test_api_classify_invalid_reading():
    # systolic must be higher than diastolic, so this should fail
    response = client.get("/api/classify", params={"systolic": 80, "diastolic": 80})
    assert response.status_code == 400
    body = response.json()
    assert "must be higher than diastolic" in body["detail"]
