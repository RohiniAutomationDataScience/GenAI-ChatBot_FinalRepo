# ============================================================================= 
# © 2025 [SapkalRohini77@gmail.com]. All rights reserved. 
# This code is shared for evaluation purposes only with [NorthBay] 
# Unauthorized use, copying, or redistribution is prohibited.
# =============================================================================    

import os, json, time, re, pytest, allure
from playwright.sync_api import expect
from lib.utils.semantics import sim_en, sim_xl
from lib.utils.chat import _send_and_get_answer
from lib.utils.common import _norm
from lib.utils.reporting import take_screenshot, attach_dom


DATA = json.load(open("data/test-data.json", encoding="utf-8"))
LOADING_MARKERS = ["Just a sec","Scanning the Gov Knowledge Base","Retrieving the right documents","Analyzing documents","⏳","📂","📄","🧠"]



# IMPORTANT: include ALL prompts (no filtering) so 4/4 run
@allure.epic("Response Accuracy and Relevance")
@allure.feature("Response Accuracy and Relevance")
@allure.story("Validate AI responses against golden answers and fact checks")
@allure.title("Validate chatbot response similarity and fact coverage for all prompts - {case[id]}")
@allure.description("""
Objective:
To verify that for all prompts (English and Arabic), the AI response is similar to the golden response
when available, contains required factual information, and meets quality thresholds.
""")
#@pytest.mark.parametrize("case", DATA.get("prompts", []))
@pytest.mark.parametrize("case", DATA.get("prompts", []), ids=lambda c: c.get("id", "no-id"))
def test_app_vs_golden_similarity(logged_in_page, case):
    allure.dynamic.title(f"Validate AI response accuracy and semantics - {case.get('id', 'no-id')}")
    page   = logged_in_page
    user_q = case.get("user") or case.get("prompt","")
    golden = (case.get("golden") or "").strip()  # may be empty in future
    lang   = case.get("lang","en")
    facts  = [f.lower() for f in case.get("must_contain", [])]
    base_thr = float(case.get("threshold", 0.85 if lang=="en" else case.get("xl_threshold", 0.80)))

    # Ask & capture
    app_ans = _send_and_get_answer(page, user_q)

    # Similarity (if golden present)
    score = None
    if golden:
        score = sim_xl(app_ans, golden) if lang=="ar" else sim_en(app_ans, golden)

    # Fact coverage
    app_norm = _norm(app_ans)
    hits = sum(1 for f in facts if f in app_norm) if facts else 0
    needed = max(1, min(2, len(facts))) if facts else 0

    # Length-aware relax (only if golden exists)
    if golden:
        len_ratio = max(1.0, len(app_ans)/max(1,len(golden)))
        relax = 0.10 if len_ratio >= 3.0 else (0.05 if len_ratio >= 1.8 else 0.0)
        eff_thr = max(0.70, base_thr - relax)
        ok = (score >= base_thr) or ((score >= eff_thr) and (hits >= needed))
    else:
        # No golden: require substantive answer + facts hit (when provided)
        ok = (len(app_ans.strip()) > 50) and (hits >= needed)

    # Allure attachments
    allure.attach(user_q, "prompt", allure.attachment_type.TEXT)
    allure.attach(app_ans, "app_answer", allure.attachment_type.TEXT)
    if golden:
        allure.attach(golden, "golden_answer", allure.attachment_type.TEXT)
        allure.attach(f"{score:.3f}", "similarity", allure.attachment_type.TEXT)
        allure.attach(
            f"url={page.url}\n"
            f"facts_hit={hits}/{len(facts)}\n"
            f"base_thr={base_thr:.2f}\n"
            f"eff_thr={eff_thr:.2f}\n",
            "diagnostics",
            allure.attachment_type.TEXT
        )
    else:
        allure.attach(
            f"url={page.url}\n"
            f"facts_hit={hits}/{len(facts)}\n"
            f"no_golden=True\n",
            "diagnostics",
            allure.attachment_type.TEXT
        )

    if not ok:
        take_screenshot(page, f"fail_{case.get('id','case')}_fullpage")
        try:
            resp_el = page.locator("(//div[@id='response-content-container'])[last()]")
            if resp_el.count():
                allure.attach(resp_el.screenshot(), f"fail_{case.get('id','case')}_response", allure.attachment_type.PNG)
        except Exception:
            pass
        attach_dom(page, f"dom_fail_{case.get('id','case')}")

    assert ok, (
        f"[{case.get('id','case')}] "
        + (f"similarity {score:.2f} " if score is not None else "no_golden ")
        + f"facts {hits}/{len(facts)}"
    )