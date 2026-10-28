"""Actual Chromium browser smoke against a local Streamlit HTTP/WebSocket server.

Runs only in the dedicated browser-e2e CI job. It is deliberately outside
pytest's default test_*.py file discovery, so Linux/Windows unit jobs do not
require the Playwright/browser dependency.

Uses no Groq API key. Does not certify the public Render deployment or live AI.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

import pytest
from playwright.sync_api import expect


ROOT = Path(__file__).resolve().parents[1]
PORT = 8579
URL = f"http://127.0.0.1:{PORT}"


@pytest.fixture(scope="session")
def local_app():
    env = os.environ.copy()
    env["GROQ_API_KEY"] = ""  # network-independent test; never use cloud secrets
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    args = [
        sys.executable, "-m", "streamlit", "run", str(ROOT / "app.py"),
        "--server.headless", "true", "--server.address", "127.0.0.1",
        "--server.port", str(PORT), "--browser.gatherUsageStats", "false",
    ]
    with open(os.devnull, "w", encoding="utf-8") as sink:
        process = subprocess.Popen(args, cwd=ROOT, env=env, stdout=sink, stderr=sink)
        try:
            for _ in range(80):
                if process.poll() is not None:
                    pytest.fail(f"Streamlit terminated at startup with code {process.returncode}")
                try:
                    with urlopen(f"{URL}/_stcore/health", timeout=1) as response:
                        if response.status == 200:
                            break
                except (OSError, URLError):
                    pass
                time.sleep(0.5)
            else:
                pytest.fail("Streamlit health endpoint did not become ready")
            yield URL
        finally:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=8)


def navigate(page, target):
    page.locator('[data-testid="stSidebar"]').get_by_text(target, exact=True).click()


def test_browser01_dashboard_renders_in_real_chromium(page, local_app):
    page.goto(local_app, wait_until="domcontentloaded")
    expect(page.get_by_role("heading", name="🏠 CMC AI Mentor Network", exact=True)).to_be_visible(timeout=30_000)
    expect(page.get_by_text("Tài liệu RAG", exact=True)).to_be_visible()


def test_browser02_mentor_search_save_and_delete_in_real_chromium(page, local_app):
    page.goto(local_app, wait_until="domcontentloaded")
    navigate(page, "👥 Tìm Mentor")
    expect(page.get_by_role("heading", name=re.compile("Tìm Mentor phù hợp"))).to_be_visible(timeout=30_000)
    page.get_by_role("button", name=re.compile("Tìm Mentor")).click()
    save = page.get_by_role("button", name=re.compile("Lưu mentor")).first
    expect(save).to_be_visible(timeout=20_000)
    save.click()
    expect(page.get_by_role("heading", name=re.compile("Mentor đã lưu"))).to_be_visible()
    page.get_by_role("button", name="Xóa", exact=True).click()
    expect(page.get_by_role("heading", name=re.compile("Mentor đã lưu"))).not_to_be_visible()


def test_browser03_offline_chat_blocked_and_grounded_rag(page, local_app):
    page.goto(local_app, wait_until="domcontentloaded")
    navigate(page, "💬 AI Assistant")
    expect(page.get_by_role("heading", name=re.compile("CMC AI Assistant"))).to_be_visible(timeout=30_000)
    expect(page.get_by_text("Chưa bật AI thực", exact=False)).to_be_visible()
    # React-Aria Streamlit selectbox exposes an explicit Open/listbox/option,
    # unlike older BaseWeb releases. Select via accessibility roles rather
    # than a keyboard shortcut that can leave the current selection unchanged.
    mode_widget = page.locator('[data-testid="stSelectbox"]').first
    mode_widget.get_by_role("button", name="Open").click()
    option = page.get_by_role("option", name=re.compile("Hỏi đáp tài liệu"))
    expect(option).to_be_visible(timeout=10_000)
    option.click()
    expect(page.get_by_role("heading", name=re.compile("Grounded AI Assistant"))).to_be_visible(timeout=20_000)
    chat = page.locator('[data-testid="stChatInput"] textarea')
    expect(chat).to_be_enabled()
    chat.fill("Issue và Pull Request sau commit?")
    chat.press("Enter")
    expect(page.get_by_text("Trạng thái:", exact=False).last).to_be_visible(timeout=20_000)


def test_browser04_general_chat_is_disabled_without_online_consent(page, local_app):
    """Guest must not be able to submit an online general chat request."""
    page.goto(local_app, wait_until="domcontentloaded")
    navigate(page, "💬 AI Assistant")
    expect(page.get_by_text("Chưa bật AI thực", exact=False)).to_be_visible(timeout=30_000)
    expect(page.locator('[data-testid="stChatInput"] textarea')).to_be_disabled()


def test_browser05_favorites_are_isolated_across_browser_sessions(browser, local_app):
    """Distinct browser contexts must not share one another's saved mentors."""
    first_context = browser.new_context()
    second_context = browser.new_context()
    try:
        first_page = first_context.new_page()
        first_page.goto(local_app, wait_until="domcontentloaded")
        navigate(first_page, "👥 Tìm Mentor")
        first_page.get_by_role("button", name=re.compile("Tìm Mentor")).click()
        save_button = first_page.get_by_role("button", name=re.compile("Lưu mentor")).first
        expect(save_button).to_be_visible(timeout=20_000)
        save_button.click()
        expect(first_page.get_by_role("heading", name=re.compile("Mentor đã lưu"))).to_be_visible()

        second_page = second_context.new_page()
        second_page.goto(local_app, wait_until="domcontentloaded")
        navigate(second_page, "👥 Tìm Mentor")
        expect(second_page.get_by_role("heading", name=re.compile("Tìm Mentor phù hợp"))).to_be_visible(timeout=30_000)
        expect(second_page.get_by_role("heading", name=re.compile("Mentor đã lưu"))).not_to_be_visible()
    finally:
        first_context.close()
        second_context.close()
