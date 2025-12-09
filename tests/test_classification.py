import os
import sys

# Make sure the project root (where main.py lives) is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import classify_blood_pressure
import pytest


@pytest.mark.parametrize(
    "systolic, diastolic, expected",
    [
        # Low
        (80, 50, "Low blood pressure"),
        (89, 59, "Low blood pressure"),
        # Ideal
        (100, 70, "Ideal blood pressure"),
        (119, 79, "Ideal blood pressure"),
        # Pre-high
        (120, 60, "Pre-high blood pressure"),
        (130, 78, "Pre-high blood pressure"),
        (100, 80, "Pre-high blood pressure"),
        # High
        (140, 60, "High blood pressure"),
        (150, 95, "High blood pressure"),
        (110, 95, "High blood pressure"),
    ],
)
def test_valid_categories(systolic, diastolic, expected):
    assert classify_blood_pressure(systolic, diastolic) == expected


@pytest.mark.parametrize(
    "systolic, diastolic",
    [
        (60, 50),  # systolic too low
        (200, 80),  # systolic too high
        (100, 30),  # diastolic too low
        (100, 150),  # diastolic too high
    ],
)
def test_out_of_range_values(systolic, diastolic):
    with pytest.raises(ValueError):
        classify_blood_pressure(systolic, diastolic)


def test_systolic_must_be_greater_than_diastolic():
    with pytest.raises(ValueError):
        classify_blood_pressure(80, 80)

def test_boundary_cases():
    # Lower systolic boundary in low range
    assert classify_blood_pressure(70, 50) == "Low blood pressure"

    # Boundary between low and ideal (systolic = 90, diastolic in 40–59)
    assert classify_blood_pressure(90, 59) == "Ideal blood pressure"

    # Boundary between ideal and pre-high (systolic = 120, diastolic in 60–79)
    assert classify_blood_pressure(120, 79) == "Pre-high blood pressure"

    # Boundary between pre-high and high (systolic = 140, diastolic in 80–89)
    assert classify_blood_pressure(140, 89) == "High blood pressure"
