# ============================================================================= 
# © 2025 [SapkalRohini77@gmail.com]. All rights reserved. 
# This code is shared for evaluation purposes only with [NorthBay] 
# Unauthorized use, copying, or redistribution is prohibited.
# =============================================================================    

import json
import pytest
import allure
from lib.utils.semantics import sim_en, sim_xl
from lib.utils.chat import _send_and_get_answer
from lib.utils.common import _norm
from lib.utils.reporting import take_screenshot, attach_dom


@pytest.fixture(scope="session")
def test_data():
    try:
        with open("data/test-data.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        pytest.fail(f"Could not load test-data.json: {e}")


# -------------------
# Test: English accuracy vs golden responses
#✅ AI provides a clear and helpful response to common public service queries
#✅ Responses are not hallucinated (i.e., fabricated or irrelevant)
#✅ Response formatting is clean (no broken HTML or incomplete thoughts)
# -------------------

@allure.epic("English accuracy vs golden responses")
@allure.feature("Accuracy vs Golden Responses")
@allure.story("System should generate factual, relevant, and well-formatted answers")
@allure.title("English prompt: Validate AI response accuracy against golden dataset")
@allure.description("""
Objective:
To verify that for known English prompts, the AI gives accurate and relevant answers
that match expected golden responses or contain required facts.
""")
@pytest.mark.parametrize("prompt_case", [
    pytest.param(p, id=p.get("id", "case"))
    for p in json.load(open("data/test-data.json", encoding="utf-8")).get("prompts", [])
    if p.get("lang") == "en"
])
def test_semantic_en_accuracy(logged_in_page, prompt_case):
    page = logged_in_page
    p = prompt_case
    prompt = p.get("user") or p.get("prompt", "")
    golden = (p.get("golden") or "").strip()
    ans = _send_and_get_answer(page, prompt)
    facts = [f.lower() for f in p.get("must_contain", [])]

    score = sim_en(ans, golden) if golden else None
    hits = sum(1 for f in facts if f in _norm(ans)) if facts else 0
    needed = max(1, min(2, len(facts))) if facts else 0

    if golden:
        thr = float(p.get("threshold", 0.70))
        ok = score is not None and score >= thr
    else:
        ok = (len(ans.strip()) > 50) and (hits >= needed)

    # Reporting to Allure
    allure.attach(prompt, f"prompt::{p.get('id','case')}", allure.attachment_type.TEXT)
    allure.attach(ans, f"app_answer::{p.get('id','case')}", allure.attachment_type.TEXT)
    if golden:
        allure.attach(golden, f"golden::{p.get('id','case')}", allure.attachment_type.TEXT)
        allure.attach(f"{score:.3f}", f"sim_en::{p.get('id','case')}", allure.attachment_type.TEXT)

    if not ok:
        take_screenshot(page, f"fail_{p.get('id','case')}")
        attach_dom(page, f"dom_fail_{p.get('id','case')}")

    assert ok, f"{p.get('id','case')} failed; score={score}, facts={hits}/{len(facts)}"


# -------------------
# Test: English <-> Arabic semantic consistency
#✅ Responses stay consistent for similar intent in both English and Arabic
# -------------------
@allure.epic("English <-> Arabic semantic consistency")
@allure.feature("Multilingual Semantic Consistency")
@allure.story("Responses should be semantically consistent across English and Arabic prompts")
@allure.title("Validate EN↔AR response consistency for paired prompts")
@allure.description("""
Objective:
To ensure the AI provides consistent answers when asked similar questions
in English and Arabic, maintaining intent and meaning.
""")
@pytest.mark.parametrize("pair", [
    pytest.param((en, ar), id=f"{en.get('id')}↔{ar.get('id')}")
    for en, ar in zip(
        [p for p in json.load(open("data/test-data.json", encoding="utf-8")).get("prompts", []) if p.get("lang") == "en"],
        [p for p in json.load(open("data/test-data.json", encoding="utf-8")).get("prompts", []) if p.get("lang") == "ar"]
    )
])
def test_semantic_en_ar_consistency(logged_in_page, pair):
    page = logged_in_page
    e, a = pair
    prompt_en = e["user"]
    prompt_ar = a["user"]

    ans_en = _send_and_get_answer(page, prompt_en)
    ans_ar = _send_and_get_answer(page, prompt_ar)

    score = sim_xl(ans_en, ans_ar)
    thr = max(e.get("xl_threshold", 0.80), a.get("xl_threshold", 0.80))

    # Reporting
    allure.attach(prompt_en, f"prompt_en::{e['id']}", allure.attachment_type.TEXT)
    allure.attach(prompt_ar, f"prompt_ar::{a['id']}", allure.attachment_type.TEXT)
    allure.attach(ans_en, f"answer_en::{e['id']}", allure.attachment_type.TEXT)
    allure.attach(ans_ar, f"answer_ar::{a['id']}", allure.attachment_type.TEXT)
    allure.attach(f"{score:.3f}", f"sim_xl::{e['id']}::{a['id']}", allure.attachment_type.TEXT)

    if score < thr:
        take_screenshot(page, f"fail_consistency_{e['id']}_{a['id']}")
        attach_dom(page, f"dom_consistency_{e['id']}_{a['id']}")

    assert score >= thr, (
        f"[EN↔AR consistency failed]\n"
        f"Score: {score:.2f} (threshold: {thr})\n"
        f"EN: {ans_en}\nAR: {ans_ar}"
    )