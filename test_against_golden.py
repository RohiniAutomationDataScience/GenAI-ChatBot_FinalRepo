# ============================================================================= 
# © 2025 [SapkalRohini77@gmail.com]. All rights reserved. 
# This code is shared for evaluation purposes only with [NorthBay] 
# Unauthorized use, copying, or redistribution is prohibited.
# =============================================================================    

import os, json, time, re, pytest, allure
from playwright.sync_api import expect
from lib.utils.semantics import sim_en, sim_xl

DATA = json.load(open("data/test-data.json", encoding="utf-8"))
LOADING_MARKERS = ["Just a sec","Scanning the Gov Knowledge Base","Retrieving the right documents","Analyzing documents","⏳","📂","📄","🧠"]

def _norm(t:str)->str:
    t = re.sub(r"[•\-–·]\s*", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip().lower()

def _strip_sources(txt:str)->str:
    # Trim known blocks like “Sources”, “Official Resources”, footers/CTA buttons that could skew similarity
    for cut in ["\nSources", "\nOfficial Resources", "\nالمصادر", "\nمصادر"]:
        if cut in txt:
            return txt.split(cut)[0].strip()
    return txt

def _type_and_send(page, text: str):
    ed = page.locator("//div[@id='chat-input']//p").first
    expect(ed).to_be_visible(timeout=15000)
    ed.click()
    try: ed.fill(text)
    except Exception: page.keyboard.type(text)
    send_btn = page.locator("//button[@type='submit']").first
    expect(send_btn).to_be_enabled()
    send_btn.click()

def _wait_for_final_response(page, timeout_ms: int = 120000) -> str:
    container = page.locator("(//div[@id='response-content-container'])[last()]")
    container.wait_for(state="visible", timeout=45000)
    start = time.time(); last_txt=""; stable=0
    while (time.time()-start)*1000 < timeout_ms:
        txt = container.inner_text().strip()
        if any(m in txt for m in LOADING_MARKERS) or len(txt) < 20:
            page.wait_for_timeout(500); continue
        if txt == last_txt:
            stable += 1
        else:
            stable = 0; last_txt = txt
        if stable >= 2:
            return txt
        page.wait_for_timeout(500)
    raise AssertionError(f"Timed out waiting for final response. Last seen:\n{last_txt}")

@pytest.mark.parametrize("case", [p for p in DATA.get("prompts", []) if p.get("golden")])
def test_app_vs_golden_similarity(logged_in_page, case):
    page = logged_in_page
    user_q = case.get("user") or case.get("prompt","")
    golden = case["golden"].strip()
    lang   = case.get("lang","en")
    facts  = [f.lower() for f in case.get("must_contain", [])]
    base_thr = float(case.get("threshold", 0.85 if lang=="en" else case.get("xl_threshold", 0.80)))

    # Ask & capture
    _type_and_send(page, user_q)
    app_ans_raw = _wait_for_final_response(page)
    app_ans = _strip_sources(app_ans_raw)

    # Similarity
    score = sim_xl(app_ans, golden) if lang=="ar" else sim_en(app_ans, golden)

    # Fact coverage
    app_norm = _norm(app_ans)
    hits = sum(1 for f in facts if f in app_norm) if facts else 0
    needed = max(1, min(2, len(facts))) if facts else 0

    # Length-aware relax
    len_ratio = max(1.0, len(app_ans)/max(1,len(golden)))
    relax = 0.10 if len_ratio >= 3.0 else (0.05 if len_ratio >= 1.8 else 0.0)
    eff_thr = max(0.70, base_thr - relax)

    ok = (score >= base_thr) or ((score >= eff_thr) and (hits >= needed))

    # Allure attachments
    allure.attach(user_q, "prompt", allure.attachment_type.TEXT)
    allure.attach(app_ans, "app_answer", allure.attachment_type.TEXT)
    allure.attach(golden, "golden_answer", allure.attachment_type.TEXT)
    allure.attach(f"{score:.3f}", "similarity", allure.attachment_type.TEXT)
    allure.attach(f"facts_hit={hits}/{len(facts)} len_ratio={len_ratio:.1f} base_thr={base_thr:.2f} eff_thr={eff_thr:.2f}",
                  "diagnostics", allure.attachment_type.TEXT)

    assert ok, (
        f"[{case.get('id','case')}] similarity {score:.2f} (base {base_thr:.2f}, eff {eff_thr:.2f}, len {len_ratio:.1f})\n"
        f"facts {hits}/{len(facts)} -> {facts}\n\nAPP:\n{app_ans}\n\nGOLDEN:\n{golden}"
    )

def test_semantic_en_accuracy(logged_in_page):
    page = logged_in_page
    for p in [x for x in DATA["prompts"] if x["lang"]=="en"]:
        ans = _send_and_get_answer(page, p["user"])
        score = sim_en(ans, p["golden"])
        allure.attach(f"{score:.3f}", f"sim_en::{p['id']}", allure.attachment_type.TEXT)
        assert score >= p.get("threshold", 0.80), f"{p['id']} sim={score:.2f}\nAns: {ans}"