# ============================================================================= 
# © 2025 [SapkalRohini77@gmail.com]. All rights reserved. 
# This code is shared for evaluation purposes only with [NorthBay] 
# Unauthorized use, copying, or redistribution is prohibited.
# =============================================================================    

# lib/utils/reporting.py

import os
import time
import allure
import traceback

def take_screenshot(page, name="screenshot"):
    """
    Takes a screenshot and attaches it to the Allure report.
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.png"
    filepath = os.path.join("reports", filename)

    page.screenshot(path=filepath)

    with open(filepath, "rb") as f:
        allure.attach(f.read(), name, allure.attachment_type.PNG)

    return filepath

def attach_dom(page, name="dom_snapshot"):
    """
    Captures the current DOM content and attaches it to Allure report.
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.html"
    filepath = os.path.join("reports", filename)

    html = page.content()
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    with open(filepath, "r", encoding="utf-8") as f:
        allure.attach(f.read(), name, allure.attachment_type.HTML)

    return filepath

def attach_on_failure(item, page):
    """
    Attaches screenshot and DOM to report if test fails.
    """
    try:
        take_screenshot(page, name=f"FAILED_{item.name}")
        attach_dom(page, name=f"DOM_{item.name}")
    except Exception as e:
        print(f"[WARN] Error during failure attachment for {item.name}: {e}")
        traceback.print_exc()
