"""
Load performance tests for the JSON classification API endpoint.

These tests hit the /api/classify endpoint many times in a tight loop and
check that the average and worst-case response times stay below reasonable
thresholds. This gives a "under load" signal as part of the CD pipeline.
"""

import os
import statistics
import time

import httpx


def get_base_url() -> str:
    """
    Base URL of the running application.

    In CD this can be overridden using BASE_URL to point at the QA deployment
    (e.g. an Azure Web App URL). By default, we assume a local instance.
    """
    return os.getenv("BASE_URL", "http://127.0.0.1:8000")


def test_api_classify_under_sustained_load():
    """
    Send a burst of requests to the /api/classify endpoint and ensure that
    performance remains acceptable.

    This simulates a load test by sending many requests in sequence and
    computing average and worst-case latency. The thresholds are generous to
    keep the test stable on CI runners, but will still catch obvious regressions.
    """
    base_url = get_base_url()
    iterations = 200  # "full load" for this small app
    durations_ms = []

    with httpx.Client(timeout=5.0) as client:
        for _ in range(iterations):
            start = time.perf_counter()
            response = client.get(
                f"{base_url}/api/classify",
                params={"systolic": 100, "diastolic": 80},
            )
            end = time.perf_counter()

            assert response.status_code == 200
            durations_ms.append((end - start) * 1000)

    avg_ms = statistics.mean(durations_ms)
    worst_ms = max(durations_ms)

    # Print metrics for the CI logs / Azure logs
    print(f"Average latency over {iterations} requests: {avg_ms:.2f} ms")
    print(f"Worst-case latency over {iterations} requests: {worst_ms:.2f} ms")

    # Thresholds: generous but catch obvious performance regressions
    assert avg_ms < 200, f"Average latency too high: {avg_ms:.2f} ms"
    assert worst_ms < 500, f"Worst-case latency too high: {worst_ms:.2f} ms"