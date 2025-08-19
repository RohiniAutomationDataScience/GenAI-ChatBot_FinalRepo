
# Project Title

Case Study: AI/ML QA Automation for U-Ask – UAE Government Chatbot


## Appendix
Any additional information goes here


## Authors
# Hi, I'm Rohini! 👋

@sapkalrohini77@gmail.com
Copyright (c) 2025 [Rohini Sapkal - sapkalrohini77@gmail.com]

This code is shared with explicit permission for evaluation purposes only.

Unauthorized use, reproduction, distribution, or modification of this code 
is strictly prohibited without prior written consent.

This repository and its contents are licensed for **non-commercial, read-only use**
and may not be used in any product, service, or derivative work.

Any violation of these terms may result in legal action.

Shared with: [NorthBay], [19-08-2025]

## Screenshots
![Allure Report - Sample](https://github.com/user-attachments/assets/5c502303-d94b-4c9b-996d-501f15349f8c)


Copyright (c) 2025 [Rohini Sapkal]

This code is shared with explicit permission for evaluation purposes only.

Unauthorized use, reproduction, distribution, or modification of this code 
is strictly prohibited without prior written consent.

This repository and its contents are licensed for **non-commercial, read-only use**
and may not be used in any product, service, or derivative work.

Any violation of these terms may result in legal action.

Shared with: [NorthBay], [19th August 2025]

## Installation 

from CMD -
Install Dependencies : pip install -r requirements.txt
python -m playwright install chromium
Install Allure (if not already installed)download allure.zip  from  https://github.com/allure-framework/allure2/releases
Update system env var  Path to bin directory of allure


## Running Tests

To run tests, run the following command

### to run all under specific class
C:\Project\uask-e2e-ready>pytest tests/genai/test_against_golden.py --headed --maxfail=0 --alluredir=reports/allure-results --clean-alluredir
allure serve reports/allure-results

OR 
### to run all under tests
pytest tests/ --headed --maxfail=0 --alluredir=reports/allure-results --clean-alluredir   
allure serve reports/allure-results



 
## Features
📌 Feature Coverage
🔵 Chatbot UI Behavior

✅ Chat widget loads correctly (desktop covered; mobile can be extended)

✅ User can send messages via input box

✅ AI responses are rendered properly in the conversation area

✅ Multilingual support (LTR: English, RTL: Arabic)

✅ Input field clears after sending

✅ Scroll behavior validated

🟢 GPT-Powered Response Validation

✅ AI provides clear and helpful responses to public service queries

✅ Responses validated against golden dataset (data/test-data.json)

✅ No hallucinated or fabricated responses

✅ Consistency across English & Arabic intents

✅ Response formatting validated (no broken HTML, complete thoughts)

🟣 Security & Injection Handling

✅ Input sanitization (e.g., <script> handled safely)

✅ AI protected against malicious prompt injection
## Project Overview


🏗️ Project Architecture Overview
uask-e2e-ready/
├── config/
│   └── .env                  # Environment variables
├── data/
│   └── test-data.json        # Test prompts + expected outputs (EN/AR)
├── lib/utils/                # Utility modules
│   ├── auth.py               # Authentication helpers
│   ├── chat.py               # Chatbot interaction helpers
│   ├── common.py             # Common test utils
│   ├── reporting.py          # Custom test reporting
│   └── semantics.py          # Semantic similarity checks
├── tests/
│   ├── ui/                   # UI behavior tests
│   │   ├── test_widget_load.py
│   │   ├── test_i18n.py
│   │   └── test_security.py
│   └── genai/                # AI/ML response validation tests
│       ├── test_against_golden.py
│       ├── test_quality_extras.py
│       └── test_semantic.py
├── README.md                 # How to run tests + setup
├── pytest.ini                # Pytest config
├── requirements.txt          # Dependencies
└── .github/workflows/ci.yml  # CI/CD pipeline
## Usage/Examples 


NA```


## Code/snippest
![codeSnippest 1](https://github.com/user-attachments/assets/e20aa293-2eae-4a45-8b98-fb2d4ddfe8e2)
<img width="1632" height="556" alt="codeSnippest 2 jpg" src="https://github.com/user-attachments/assets/54ebcae1-6cd0-49b8-9d54-40676f247b2f" />
<img width="1917" height="1064" alt="codeSnippest 3 jpg" src="https://github.com/user-attachments/assets/53bef3d7-785c-411b-9eb5-03fd754c8812" />




## Tech Stack

pytest==8.2.2
playwright==1.46.0
pytest-xdist==3.6.1
python-dotenv==1.0.1
allure-pytest==2.13.5
requests==2.32.3
sentence-transformers==2.7.0
torch>=2.1.0

