# ============================================================================= 
# © 2025 [SapkalRohini77@gmail.com]. All rights reserved. 
# This code is shared for evaluation purposes only with [NorthBay] 
# Unauthorized use, copying, or redistribution is prohibited.
# =============================================================================    

# lib/utils/chat.py

from playwright.sync_api import expect
import time
import allure

LOADING_MARKERS = ["Just a sec","Scanning the Gov Knowledge Base","Retrieving the right documents","Analyzing documents","⏳","📂","📄","🧠"]


def _strip_sources(txt:str)->str:
    for cut in ["\nSources", "\nOfficial Resources", "\nالمصادر", "\nمصادر"]:
        if cut in txt:
            return txt.split(cut)[0].strip()
    return txt

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
            page.wait_for_timeout(500); continue
        if txt == last_txt:
            stable += 1
        else:
            stable = 0; last_txt = txt
        if stable >= 2:
            return txt
        page.wait_for_timeout(500)
    raise AssertionError(f"Timed out waiting for final response. Last seen:\n{last_txt}")

def _send_and_get_answer(page, prompt: str) -> str:
    _type_and_send(page, prompt)
    ans = _wait_for_final_response(page)
    return _strip_sources(ans)
