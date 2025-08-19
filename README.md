# U-Ask (UAE Gov) – E2E QA Automation
Stack: Python 3.10+, Playwright, PyTest, SentenceTransformers, Allure.
## Setup
pip install -r requirements.txt
python -m playwright install
## Run
pytest
LANG=ar pytest
allure serve reports/allure-results
