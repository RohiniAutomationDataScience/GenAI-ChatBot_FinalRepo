# ============================================================================= 
# © 2025 [SapkalRohini77@gmail.com]. All rights reserved. 
# This code is shared for evaluation purposes only with [NorthBay] 
# Unauthorized use, copying, or redistribution is prohibited.
# =============================================================================    

from playwright.sync_api import Page, expect, TimeoutError as PWTimeout

def _click_login_using_credentials(page: Page, timeout: int = 8000) -> None:
    btn = page.locator("//button[normalize-space(.)='Login using Credentials']").first
    try:
        if btn.count():
            expect(btn).to_be_visible(timeout=timeout)
            btn.scroll_into_view_if_needed()
            btn.click()
            return
    except PWTimeout:
        pass
    except Exception:
        try:
            if btn.count():
                btn.scroll_into_view_if_needed()
                btn.click(force=True)
                return
        except Exception:
            pass
    for frame in page.frames:
        try:
            fbtn = frame.locator("//button[normalize-space(.)='Login using Credentials']").first
            if fbtn.count():
                expect(fbtn).to_be_visible(timeout=timeout)
                fbtn.scroll_into_view_if_needed()
                fbtn.click()
                return
        except Exception:
            continue

def _fill_credentials_and_submit(page: Page, email: str, password: str, timeout: int = 15000) -> None:
    filled = False
    try:
        e = page.locator("#email").first
        p = page.locator("#password").first
        if e.count() and p.count():
            expect(e).to_be_visible(timeout=timeout)
            e.fill(email)
            expect(p).to_be_visible()
            p.fill(password)
            s = page.locator("//button[@type='submit' and normalize-space()='Sign in']").first
            expect(s).to_be_enabled()
            s.click()
            filled = True
    except Exception:
        pass
    if not filled:
        for f in page.frames:
            try:
                e = f.locator("#email").first
                p = f.locator("#password").first
                if e.count() and p.count():
                    expect(e).to_be_visible(timeout=timeout)
                    e.fill(email)
                    expect(p).to_be_visible()
                    p.fill(password)
                    s = f.locator("//button[@type='submit' and normalize-space()='Sign in']").first
                    expect(s).to_be_enabled()
                    s.click()
                    filled = True
                    break
            except Exception:
                continue
    if not filled:
        raise AssertionError("Login form not found: #email/#password/Sign in")

def _wait_chat_composer(page: Page, timeout: int = 20000) -> None:
    composer = page.locator("//div[@id='chat-input']//p").first
    try:
        expect(composer).to_be_visible(timeout=timeout)
    except Exception:
        for f in page.frames:
            try:
                c = f.locator("//div[@id='chat-input']//p").first
                if c.count():
                    expect(c).to_be_visible(timeout=timeout)
                    return
            except Exception:
                continue
        raise

def login(page: Page, base_url: str, email: str, password: str) -> Page:
    page.goto(base_url, wait_until="domcontentloaded")
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    _click_login_using_credentials(page)
    _fill_credentials_and_submit(page, email, password)
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    _wait_chat_composer(page)
    return page
