# ============================================================================= 
# © 2025 [SapkalRohini77@gmail.com]. All rights reserved. 
# This code is shared for evaluation purposes only with [NorthBay] 
# Unauthorized use, copying, or redistribution is prohibited.
# =============================================================================    

import os
import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from lib.utils.auth import login
from lib.utils.reporting import attach_on_failure


# Helper functions to parse environment variables
def _env_bool(name: str, default: bool) -> bool:
    v = os.environ.get(name, str(default)).strip().lower()
    return v in ("1", "true", "yes", "y", "on")


def _env_str(name: str, default: str) -> str:
    return os.environ.get(name, default).strip()


# ---- Add custom CLI options: --headed, --browser, --mobile ----
def pytest_addoption(parser):
    parser.addoption("--headed", action="store_true", help="Run browser in headed mode")
    parser.addoption("--browser", choices=["chromium", "firefox", "webkit"], default=None, help="Select browser engine")
    parser.addoption("--mobile", action="store_true", help="Emulate a phone-sized viewport")


# ---- Load config from CLI or .env ----
@pytest.fixture(scope="session")
def config(pytestconfig):
    load_dotenv(dotenv_path=os.path.join("config", ".env"))

    cli_headed = pytestconfig.getoption("--headed")
    cli_browser = pytestconfig.getoption("--browser")
    cli_mobile = pytestconfig.getoption("--mobile")

    env_headless = _env_bool("HEADLESS", True)
    env_browser = _env_str("BROWSER", "chromium")
    env_mobile = _env_bool("MOBILE", False)

    headless = not cli_headed if cli_headed else env_headless
    browser = cli_browser if cli_browser else env_browser
    mobile = True if cli_mobile else env_mobile

    return {
        "base_url": _env_str("BASE_URL", "https://govgpt.sandbox.dge.gov.ae/"),
        "email": _env_str("EMAIL", ""),
        "password": _env_str("PASSWORD", ""),
        "lang": _env_str("LANG", "en"),
        "headless": headless,
        "browser": browser,
        "mobile": mobile
    }


# ---- Playwright browser fixture ----
@pytest.fixture(scope="session")
def browser(config):
    with sync_playwright() as p:
        launcher = {
            "chromium": p.chromium,
            "firefox": p.firefox,
            "webkit": p.webkit
        }[config["browser"]]
        b = launcher.launch(headless=config["headless"])
        yield b
        b.close()


# ---- Page context fixture ----
@pytest.fixture()
def page(browser, config):
    if config["mobile"]:
        viewport = {"width": 390, "height": 844}
        ua = ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 "
              "(KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1")
    else:
        viewport = {"width": 1280, "height": 800}
        ua = None

    ctx = browser.new_context(
        locale="ar-AE" if config["lang"] == "ar" else "en-US",
        viewport=viewport,
        user_agent=ua
    )
    pg = ctx.new_page()
    yield pg
    ctx.close()


# ---- Login fixture ----
@pytest.fixture()
def logged_in_page(page, config):
    return login(page, config["base_url"], config["email"], config["password"])


# ---- Pytest hook: Capture failed test reporting ----
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()

    if result.when == "call" and result.failed:
        page = item.funcargs.get("logged_in_page") or item.funcargs.get("page")
        if page:
            attach_on_failure(item, page)
