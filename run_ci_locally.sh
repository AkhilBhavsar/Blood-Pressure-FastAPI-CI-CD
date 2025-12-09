#!/usr/bin/env bash
set -e

echo "Running flake8..."
flake8 .

echo "Running pytest with coverage..."
pytest --maxfail=1 --disable-warnings \
       --cov=. --cov-report=term-missing --cov-fail-under=80

echo "Running behave..."
behave

echo "Running bandit..."
bandit -r main.py

echo "Running pip-audit..."
pip-audit

echo "All checks passed"