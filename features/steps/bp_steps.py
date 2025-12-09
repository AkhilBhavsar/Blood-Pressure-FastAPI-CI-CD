from behave import given, when, then
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@given("I open the blood pressure calculator")
def step_open_calculator(context):
    response = client.get("/")
    assert response.status_code == 200
    context.response = response


@when('I submit a reading of systolic {systolic:d} and diastolic {diastolic:d}')
def step_submit_reading(context, systolic, diastolic):
    response = client.post(
        "/calculate",
        data={"systolic": systolic, "diastolic": diastolic},
    )
    assert response.status_code == 200
    context.response = response


@then('I should see "{text}" in the result')
def step_see_result(context, text):
    assert text in context.response.text
