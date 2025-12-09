from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Blood Pressure Category Calculator")

templates = Jinja2Templates(directory="templates")


def classify_blood_pressure(systolic: int, diastolic: int) -> str:
    """
    Classify blood pressure using the chart (ranges 70–190 / 40–100).

    Diastolic bands (mmHg):
      D1: 40–59
      D2: 60–79
      D3: 80–89
      D4: 90–100

    Systolic bands (mmHg):
      S1: 70–89
      S2: 90–119
      S3: 120–139
      S4: 140–190

    Colours from the chart:
      - Purple  (low)
      - Green   (ideal)
      - Yellow  (pre-high)
      - Red     (high)
    """

    # Validate overall allowed range
    if not (70 <= systolic <= 190):
        raise ValueError("Systolic must be between 70 and 190 mmHg.")
    if not (40 <= diastolic <= 100):
        raise ValueError("Diastolic must be between 40 and 100 mmHg.")
    if systolic <= diastolic:
        raise ValueError("Systolic (top number) must be higher than diastolic (bottom number).")

    # --- Classify using the rectangular regions in the image ---

    # D1: diastolic 40–59
    if 40 <= diastolic < 60:
        if 70 <= systolic < 90:
            return "Low blood pressure"
        elif 90 <= systolic < 120:
            return "Ideal blood pressure"
        elif 120 <= systolic < 140:
            return "Pre-high blood pressure"
        else:  # systolic >= 140
            return "High blood pressure"

    # D2: diastolic 60–79
    elif 60 <= diastolic < 80:
        if 70 <= systolic < 120:
            return "Ideal blood pressure"
        elif 120 <= systolic < 140:
            return "Pre-high blood pressure"
        else:  # systolic >= 140
            return "High blood pressure"

    # D3: diastolic 80–89
    elif 80 <= diastolic < 90:
        if systolic < 140:
            # Whole 80–89 / 70–139 area is yellow in the chart
            return "Pre-high blood pressure"
        else:
            return "High blood pressure"

    # D4: diastolic 90–100
    else:  # 90 <= diastolic <= 100
        # Entire 90–100 band is red in the chart
        return "High blood pressure"


@app.get("/", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": None,
            "error": None,
            "systolic": "",
            "diastolic": "",
        },
    )


@app.post("/calculate", response_class=HTMLResponse)
async def calculate(
    request: Request,
    systolic: int = Form(...),
    diastolic: int = Form(...),
):
    error = None
    result = None

    try:
        result = classify_blood_pressure(systolic, diastolic)
    except ValueError as e:
        error = str(e)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result,
            "error": error,
            "systolic": systolic,
            "diastolic": diastolic,
        },
    )
