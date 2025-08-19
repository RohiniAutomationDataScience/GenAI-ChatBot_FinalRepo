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


# ---- Data ----------
DATA = json.load(open("data/test-data.json", encoding="utf-8"))

_pairs = []
_by_base = {}

def _base_id(case_id: str) -> str:
    return re.sub(r'_(en|ar)$', '', case_id or "")

for p in DATA["prompts"]:
    _by_base.setdefault(_base_id(p.get("id")), {}).update({p.get("lang"): p})
for base, d in _by_base.items():
    if "en" in d and "ar" in d:
        _pairs.append((d["en"], d["ar"]))

# ---- Shared helpers (local/lightweight; no cross-file deps) ----------
LOADING_MARKERS = [
    "Just a sec", "Scanning the Gov Knowledge Base",
    "Retrieving the right documents", "Analyzing documents", "⏳", "📂", "📄", "🧠"
]

def _type_and_send(page, text: str):
    ed = page.locator("//div[@id='chat-input']//p").first
    expect(ed).to_be_visible(timeout=15000)
    ed.click()
    try:
        ed.fill(text)
    except Exception:
        page.keyboard.type(text)
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
            page.wait_for_timeout(400); continue
        if txt == last_txt: stable += 1
        else: stable = 0; last_txt = txt
        if stable >= 2: return txt
        page.wait_for_timeout(400)
    raise AssertionError(f"Timed out waiting final response. Last:\n{last_txt}")

def _send(page, q: str) -> str:
    _type_and_send(page, q)
    return _wait_for_final_response(page)

def _base_id(case_id: str) -> str:
    return re.sub(r'_(en|ar)$', '', case_id or "")

def _looks_clean(text: str) -> bool:
    # Reject <script>/<style> and obviously broken tags (very light check)
    if re.search(r"<\s*(script|style)\b", text, flags=re.I): return False
    # tolerate self-closing tags and small mismatch
    opens = re.findall(r"<([a-zA-Z]+)[^>/]*>", text)
    closes = re.findall(r"</([a-zA-Z]+)\s*>", text)
    for t in ["br","hr","img","input","meta","link"]:  # ignore self-closers
        opens = [x for x in opens if x.lower() != t]
    return len(closes) <= len(opens) + 2

GOV_ALLOW = r"(gdrfad\.gov\.ae|icp\.gov\.ae|u\.ae|gov\.ae)"
def _links_are_gov_whitelisted(ans: str) -> bool:
    urls = re.findall(r"https?://[^\s)\]]+", ans)
    return all(re.search(GOV_ALLOW, u, flags=re.I) for u in urls)
# ---------------------------- Tests ----------------------------

import allure  # Make sure this is imported if not already

# 1) EN↔AR intent consistency
@allure.epic("EN↔AR intent consistency")
@allure.feature("Multilingual Intent Consistency")
@allure.story("Ensure consistent AI responses across EN and AR for same user intent")
@allure.title("Validate cross-language intent consistency (EN ↔ AR) - Multilingual consistency, Clear & helpful responses")
@allure.description("""
**Objective:**  
To verify that AI responses for the same user intent are consistent in both English and Arabic, by checking semantic similarity.
""")
@pytest.mark.parametrize("en_case,ar_case", _pairs)
def test_intent_consistency_cross_lang(logged_in_page, en_case, ar_case):
    page = logged_in_page
    en_ans = _send(page, en_case["user"])
    ar_ans = _send(page, ar_case["user"])
    score = sim_xl(en_ans, ar_ans)  # multilingual similarity
    allure.attach(f"{score:.3f}", f"en_ar_similarity::{_base_id(en_case['id'])}", allure.attachment_type.TEXT)
    if score < 0.70:
        take_screenshot(page, f"fail_consistency_{_base_id(en_case['id'])}")
        attach_dom(page, f"dom_consistency_{_base_id(en_case['id'])}")
    assert score >= 0.70, f"EN–AR consistency too low ({score:.2f})"

# 2) Loading markers appear while building the answer
@allure.epic("Loading markers appear while building the answer")
@allure.feature("User Experience")
@allure.story("Visual feedback should appear while response is being generated")
@allure.title("Validate presence of loading markers during response generation - Loading states and fallback messages ")
@allure.description("""
**Objective:**  
Ensure that appropriate loading indicators (e.g., 'Scanning', 'Analyzing documents', etc.) are shown while the AI is generating a response.
""")
@pytest.mark.parametrize("case", [c for c in DATA["prompts"] if c.get("lang")=="en"][:1])
def test_loading_markers_appear(logged_in_page, case):
    page = logged_in_page
    _type_and_send(page, case["user"])
    container = page.locator("(//div[@id='response-content-container'])[last()]")
    container.wait_for(state="visible", timeout=45000)
    saw_loading = False
    for _ in range(30):
        txt = container.inner_text()
        if any(m in txt for m in LOADING_MARKERS):
            saw_loading = True
            break
        page.wait_for_timeout(250)
    if not saw_loading:
        take_screenshot(page, "fail_loading_markers")
        attach_dom(page, "dom_loading_markers")
    assert saw_loading, "Expected loading indicators not shown"

# 3) Response formatting is clean
@allure.epic("Response formatting is clean")
@allure.feature("Response Formatting")
@allure.story("Ensure response does not contain broken or unsafe HTML")
@allure.title("Validate HTML formatting of AI-generated responses - Clean formatting")
@allure.description("""
**Objective:**  
To verify that the generated responses do not contain broken HTML, unsafe scripts, or incomplete formatting that could impact UI rendering or security.
""")
@pytest.mark.parametrize("case", [c for c in DATA["prompts"] if c.get("lang")=="en"][:1])
def test_response_format_is_clean(logged_in_page, case):
    page = logged_in_page
    ans = _send(page, case["user"])
    ok = _looks_clean(ans)
    allure.attach(ans, "answer_text", allure.attachment_type.TEXT)
    if not ok:
        take_screenshot(page, "fail_format_clean")
        attach_dom(page, "dom_format_clean")
    assert ok, "Response contains unsafe/broken HTML/markup"

# 4) Government domain links only (no hallucinated URLs)
@allure.epic("Government domain links only (no hallucinated URLs)")
@allure.feature("Anti-Hallucination & Trust")
@allure.story("Responses must only contain whitelisted government domain URLs")
@allure.title("Validate that all links in responses point to approved government domains - Anti-hallucination")
@allure.description("""
**Objective:**  
Ensure that any hyperlinks in AI-generated answers refer only to whitelisted and official government domains (e.g., gdrfad.gov.ae, icp.gov.ae), to avoid hallucination and misinformation.
""")
@pytest.mark.parametrize("case", [c for c in DATA["prompts"] if c.get("lang")=="en"][:1])
def test_links_are_gov_whitelisted(logged_in_page, case):
    page = logged_in_page
    ans = _send(page, case["user"])
    ok = _links_are_gov_whitelisted(ans)
    allure.attach(ans, "answer_text", allure.attachment_type.TEXT)
    if not ok:
        take_screenshot(page, "fail_link_whitelist")
        attach_dom(page, "dom_link_whitelist")
    assert ok, "Found non-gov links in answer"

# 5) Fallback message appears for gibberish/invalid input
@allure.epic("Fallback message appears for gibberish/invalid input")
@allure.feature("Fallback Handling")
@allure.story("System should show fallback messages for gibberish or unclear input")
@allure.title("Validate fallback response for invalid/gibberish input - Loading states and fallback messages")
@allure.description("""
Objective:
To ensure that when a user provides an unclear or malformed query (e.g., gibberish or special characters), 
the system responds with a proper fallback message such as 'Sorry, I didn’t catch that...'
""")
@pytest.mark.parametrize("case", [c for c in DATA["prompts"] if "fallback_test" in c.get("id", "")])
def test_fallback_message_shown(logged_in_page, case):
    page = logged_in_page
    ans = _send(page, case["user"])
    allure.attach(ans, "fallback_response", allure.attachment_type.TEXT)

    # Basic similarity check if golden present
    if "golden" in case:
        score = sim_xl(ans, case["golden"])
        allure.attach(f"{score:.3f}", f"sim_score::{case['id']}", allure.attachment_type.TEXT)
        assert score >= case.get("threshold", 0.80), f"Low similarity to golden fallback response ({score:.2f})"

    # Must contain certain key fallback phrases
    missing_phrases = [kw for kw in case.get("must_contain", []) if kw.lower() not in ans.lower()]
    assert not missing_phrases, f"Missing fallback keywords: {missing_phrases}"
