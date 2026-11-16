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
from playwright.sync_api import expect, TimeoutError as PlaywrightTimeoutError


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


def select_option(page, widget, option_name):
    option = page.get_by_role("option", name=option_name, exact=True)
    for _ in range(3):
        widget.get_by_role("button", name="Open").click()
        try:
            option.wait_for(state="visible", timeout=2_500)
        except PlaywrightTimeoutError:
            widget.get_by_role("combobox").click()
            try:
                option.wait_for(state="visible", timeout=2_500)
            except PlaywrightTimeoutError:
                page.keyboard.press("Escape")
                continue
        option.click()
        return
    pytest.fail(f"Selectbox did not expose the {option_name!r} option")


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
    option = page.get_by_role("option", name=re.compile("Hỏi đáp tài liệu"))
    # Streamlit rerenders the React-Aria selectbox asynchronously. When an
    # opener click races with a rerender, the popup can immediately disappear.
    # Use only real user clicks, bounded retries, and verify the resulting page.
    for attempt in range(3):
        mode_widget.get_by_role("button", name="Open").click()
        try:
            option.wait_for(state="visible", timeout=2_500)
        except PlaywrightTimeoutError:
            # Try the accessible combobox trigger as an alternate UI gesture.
            mode_widget.get_by_role("combobox", name="Chọn chế độ AI").click()
            try:
                option.wait_for(state="visible", timeout=2_500)
            except PlaywrightTimeoutError:
                page.keyboard.press("Escape")
                continue
        option.click()
        break
    else:
        pytest.fail("RAG mode dropdown did not expose the option after 3 UI attempts")
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


def test_browser06_session_mentor_creation_matching_removal_and_isolation(browser, local_app):
    first_context = browser.new_context()
    second_context = browser.new_context()
    try:
        first_page = first_context.new_page()
        first_page.goto(local_app, wait_until="domcontentloaded")
        navigate(first_page, "👥 Tìm Mentor")
        expect(first_page.get_by_role("heading", name=re.compile("Tìm Mentor phù hợp"))).to_be_visible(timeout=30_000)
        first_page.get_by_text(
            "➕ Tạo mentor nháp trong phiên này", exact=True
        ).click()
        first_page.get_by_label("Tên mentor", exact=True).fill("Mentor Session Only")
        first_page.get_by_label("Chức danh", exact=True).fill("AI Mentor")
        first_page.get_by_label("Công ty / tổ chức", exact=True).fill("Demo Org")
        first_page.get_by_label("Số năm kinh nghiệm", exact=True).fill("4")
        first_page.get_by_label("Giới thiệu", exact=True).fill(
            "Mentor nháp dùng riêng trong phiên trình duyệt."
        )
        first_page.get_by_label(
            "Kỹ năng (phân cách bằng dấu phẩy)", exact=True
        ).fill("Python, Computer Vision")
        first_page.get_by_label(
            "Có thể hỗ trợ (phân cách bằng dấu phẩy)", exact=True
        ).fill("CV Review")
        first_page.get_by_role("button", name="Tạo mentor nháp").click()
        expect(first_page.get_by_text("Mentor Session Only", exact=False)).to_be_visible()

        created_field = first_page.get_by_role(
            "combobox", name="Lĩnh vực", exact=True
        ).input_value().strip()
        field_filter = first_page.locator('[data-testid="stSelectbox"]').nth(1)
        select_option(first_page, field_filter, created_field)
        support_filter = first_page.locator('[data-testid="stSelectbox"]').nth(2)
        select_option(first_page, support_filter, "CV Review")
        first_page.get_by_role("button", name=re.compile("Tìm Mentor")).click()

        expect(
            first_page.get_by_text("Mentor Session Only • AI Mentor", exact=False)
        ).to_be_visible()
        first_page.get_by_role("button", name=re.compile("Lưu mentor")).click()
        expect(first_page.get_by_text("Mentor đã lưu", exact=False)).to_be_visible()

        first_page.get_by_role("button", name="Xóa mentor nháp", exact=True).click()
        first_page.get_by_role("button", name="Xác nhận xóa", exact=True).click()
        expect(
            first_page.get_by_role("heading", name="Mentor nháp của phiên này")
        ).not_to_be_visible()
        expect(
            first_page.get_by_role("heading", name=re.compile("Mentor đã lưu"))
        ).not_to_be_visible()

        second_page = second_context.new_page()
        second_page.goto(local_app, wait_until="domcontentloaded")
        navigate(second_page, "👥 Tìm Mentor")
        expect(second_page.get_by_text("Mentor Session Only", exact=False)).not_to_be_visible()
    finally:
        first_context.close()
        second_context.close()
