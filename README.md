# Blood Pressure Category Calculator (FastAPI)

This project is a small web application that classifies a blood pressure reading
into one of four categories:

- Low blood pressure  
- Ideal blood pressure  
- Pre-high blood pressure  
- High blood pressure  

The classification is based on the chart provided in the assignment:
- Systolic range: 70–190 mmHg (inclusive)
- Diastolic range: 40–100 mmHg (inclusive)
- Systolic must always be higher than diastolic.

The application is implemented using **FastAPI** with a simple HTML interface.

---

## Running the application locally

### Prerequisites

- Python 3.11+ installed
- Git
- (Optional) VS Code with the Python extension

### Setup

```bash
git clone https://github.com/AkhilBhavsar/Blood-Pressure-FastAPI-CI-CD.git
cd Blood-Pressure-FastAPI-CI-CD

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt