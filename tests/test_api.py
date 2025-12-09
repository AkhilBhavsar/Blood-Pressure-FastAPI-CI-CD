import os
import sys

# Make sure the project root (where main.py lives) is on sys.path
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
