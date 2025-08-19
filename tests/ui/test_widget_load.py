# ============================================================================= 
# © 2025 [SapkalRohini77@gmail.com]. All rights reserved. 
# This code is shared for evaluation purposes only with [NorthBay] 
# Unauthorized use, copying, or redistribution is prohibited.
# =============================================================================    

from playwright.sync_api import expect
import allure

def _composer(page): return page.locator("//div[@id='chat-input']//p").first
def _send(page, text):
    ed=_composer(page); expect(ed).to_be_visible(timeout=15000); ed.click()
    try: ed.fill(text)
    except Exception: page.keyboard.type(text)
    send_btn = page.locator("//button[@type='submit']").first
    expect(send_btn).to_be_enabled(); send_btn.click()

@allure.epic("Chatbot UI Behavior")
@allure.feature("Chat Widget Loading")
@allure.story("Chat widget UI loads correctly")
@allure.title("Validate chat input composer is visible on load")
@allure.description("""
Objective:
Ensure the chat input composer element is visible, confirming the chat widget loads correctly.
Covers:
- A. Chatbot UI Behavior: Chat widget loads correctly on desktop and mobile
""")
def test_widget_loads(logged_in_page):
    page = logged_in_page
    expect(_composer(page)).to_be_visible(timeout=15000)


@allure.epic("Chatbot UI Behavior")
@allure.feature("Chat Interaction")
@allure.story("Sending messages and rendering AI responses")
@allure.title("Validate sending a message and AI response rendering")
@allure.description("""
Objective:
Send a message and verify the AI response container becomes visible.
Covers:
- A. Chatbot UI Behavior: User can send messages via input box
- A. Chatbot UI Behavior: AI responses are rendered properly in the conversation area
""")
def test_send_and_render(logged_in_page):
    page = logged_in_page
    _send(page, "Hello from Playwright!")
    resp = page.locator("(//div[@id='response-content-container'])[last()]")
    expect(resp).to_be_visible(timeout=45000)


@allure.epic("Chatbot UI Behavior")
@allure.feature("Chat Interaction")
@allure.story("Input box behavior after sending message")
@allure.title("Validate chat input is cleared after sending message")
@allure.description("""
Objective:
Ensure that after sending a message, the chat input composer is cleared.
Covers:
- A. Chatbot UI Behavior: Input is cleared after sending
""")
def test_input_clears_after_send(logged_in_page):
    page = logged_in_page
    _send(page, "Testing input clear")
    expect(_composer(page)).to_have_text("", timeout=5000)


@allure.epic("Chatbot UI Behavior")
@allure.feature("Multilingual Support")
@allure.story("Layout direction for English locale")
@allure.title("Validate Left-To-Right layout direction for English")
@allure.description("""
Objective:
Confirm that the page direction is LTR (left-to-right) for English or default languages.
Covers:
- A. Chatbot UI Behavior: Multilingual support (LTR for English)
""")
def test_ltr_en(logged_in_page):
    page = logged_in_page
    dir_val = page.evaluate("document.dir || getComputedStyle(document.documentElement).direction")
    assert dir_val in ("ltr", ""), f"Expected LTR, got {dir_val}"


@allure.epic("Chatbot UI Behavior")
@allure.feature("Chat UI Layout")
@allure.story("Scroll and accessibility checks")
@allure.title("Validate chat response container visibility and scroll presence")
@allure.description("""
Objective:
Ensure the chat response container is visible and scrollable if content overflows.
Covers:
- A. Chatbot UI Behavior: Scroll and accessibility work as expected
""")
def test_scroll_area_present(logged_in_page):
    page = logged_in_page
    _send(page, "UAE Government Visa details")
    resp = page.locator("(//div[@id='response-content-container'])[last()]")
    expect(resp).to_be_visible(timeout=45000)
    wrap = page.locator("(//div[@id='sidebar']/div/div[contains(@class, 'pl-[8px]') and contains(@class, 'overflow-y-auto')]")
    expect(wrap).to_be_visible(timeout=65000)