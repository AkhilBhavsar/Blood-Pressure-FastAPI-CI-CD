Feature: Blood pressure category lookup
  As a user of the calculator
  I want to enter a blood pressure reading
  So that I can see the correct category from the chart

  Scenario: Classify a pre-high blood pressure reading
    Given I open the blood pressure calculator
    When I submit a reading of systolic 100 and diastolic 80
    Then I should see "Pre-high blood pressure" in the result