# ============================================================================= 
# © 2025 [SapkalRohini77@gmail.com]. All rights reserved. 
# This code is shared for evaluation purposes only with [NorthBay] 
# Unauthorized use, copying, or redistribution is prohibited.
# =============================================================================    

from playwright.sync_api import expect



def _composer(page): return page.locator("//div[@id='chat-input']//p").first
def _send(page, text):
    ed=_composer(page); expect(ed).to_be_visible(timeout=15000); ed.click()
    try: ed.fill(text)
    except Exception: page.keyboard.type(text)
    send_btn = page.locator("//button[@type='submit']").first
    expect(send_btn).to_be_enabled(); send_btn.click()
    
def test_chat_input_xss_blocked(logged_in_page):
    page = logged_in_page
    _send(page, "<script>window.xssInjected=true;</script>")

    # Locate the response area correctly
    resp = page.locator("//div[@id='response-content-container']")

    # Ensure fallback message appears
    expect(resp).to_contain_text("I’m sorry")
    expect(resp).to_contain_text("for your understanding")

    # Verify the script did not execute
    result = page.evaluate("window.xssInjected === undefined")
    assert result, "XSS script executed!"