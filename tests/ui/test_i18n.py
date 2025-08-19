# ============================================================================= 
# © 2025 [SapkalRohini77@gmail.com]. All rights reserved. 
# This code is shared for evaluation purposes only with [NorthBay] 
# Unauthorized use, copying, or redistribution is prohibited.
# =============================================================================    


import allure

# TESTS - Multilingual directionality (LTR for English, RTL for Arabic) ← THIS is what's covered - 📌 A. Chatbot UI Behavior
@allure.epic("Chatbot UI Behavior")
@allure.feature("Multilingual Support")
@allure.story("LTR layout validation for English UI")
@allure.title("Validate Left-To-Right direction for English layout")
@allure.description("""
Objective:
Ensure that when the chatbot is displayed in English (or non-RTL language),
the document direction is set correctly to 'ltr', '', or 'auto' for proper layout.
""")
def test_ltr_en(logged_in_page):
    page=logged_in_page
    dir_val = page.evaluate("document.documentElement.dir||getComputedStyle(document.body).direction")
    assert dir_val in ["ltr","","auto"]
    
@allure.epic("Chatbot UI Behavior")
@allure.feature("Multilingual Support")
@allure.story("RTL layout validation for Arabic UI")
@allure.title("Validate Right-To-Left direction for Arabic layout")
@allure.description("""
Objective:
Ensure that when the chatbot language is set to Arabic,
the document direction is correctly set to 'rtl' for proper RTL layout rendering.
""")
def test_rtl_ar(page, config):
    if config["lang"]!="ar":
        return
    page.goto(config["base_url"])
    dir_val = page.evaluate("document.documentElement.dir||getComputedStyle(document.body).direction")
    assert dir_val=="rtl" or "rtl" in dir_val
