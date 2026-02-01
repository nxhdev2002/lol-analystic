"""
Unit tests for mini-fb-service browser automation.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add services/mini-fb-service/src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "mini-fb-service" / "src"))

from mini_fb_service.browser import FacebookBrowser


class TestFacebookBrowser:
    """Tests for FacebookBrowser."""

    @pytest.fixture
    def browser(self):
        """Create a browser instance for testing."""
        return FacebookBrowser(headless=True, browser_type="chromium")

    def test_browser_initialization(self):
        """Test browser initialization."""
        browser = FacebookBrowser(headless=True, browser_type="chromium")
        assert browser.headless is True
        assert browser.browser_type == "chromium"
        assert browser._playwright is None
        assert browser._browser is None

    def test_browser_initialization_firefox(self):
        """Test browser initialization with Firefox."""
        browser = FacebookBrowser(headless=False, browser_type="firefox")
        assert browser.headless is False
        assert browser.browser_type == "firefox"

    @patch("mini_fb_service.browser.sync_playwright")
    def test_start_chromium(self, mock_playwright):
        """Test starting Chromium browser."""
        mock_pw = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        mock_pw.return_value.start.return_value = mock_pw
        mock_pw.chromium.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_playwright.return_value = mock_pw

        browser = FacebookBrowser(headless=True, browser_type="chromium")
        browser.start()

        mock_pw.start.assert_called_once()
        mock_pw.chromium.assert_called_once_with(headless=True)
        mock_browser.new_context.assert_called_once()
        mock_context.new_page.assert_called_once()

    @patch("mini_fb_service.browser.sync_playwright")
    def test_start_firefox(self, mock_playwright):
        """Test starting Firefox browser."""
        mock_pw = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        mock_pw.return_value.start.return_value = mock_pw
        mock_pw.firefox.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_playwright.return_value = mock_pw

        browser = FacebookBrowser(headless=True, browser_type="firefox")
        browser.start()

        mock_pw.firefox.assert_called_once_with(headless=True)

    @patch("mini_fb_service.browser.sync_playwright")
    def test_start_invalid_browser_type(self, mock_playwright):
        """Test starting with invalid browser type."""
        mock_pw = MagicMock()
        mock_playwright.return_value.start.return_value = mock_pw

        browser = FacebookBrowser(headless=True, browser_type="invalid")

        with pytest.raises(ValueError, match="Unsupported browser type"):
            browser.start()

    @patch("mini_fb_service.browser.sync_playwright")
    def test_stop(self, mock_playwright):
        """Test stopping browser."""
        mock_pw = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_pw.return_value.start.return_value = mock_pw
        mock_pw.chromium.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        browser = FacebookBrowser(headless=True, browser_type="chromium")
        browser._playwright = mock_pw
        browser._browser = mock_browser
        browser._context = mock_context
        browser._page = mock_page

        browser.stop()

        mock_context.close.assert_called_once()
        mock_browser.close.assert_called_once()
        mock_pw.stop.assert_called_once()

    @patch("mini_fb_service.browser.sync_playwright")
    def test_context_manager(self, mock_playwright):
        """Test browser as context manager."""
        mock_pw = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_pw.return_value.start.return_value = mock_pw
        mock_pw.chromium.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        with FacebookBrowser(headless=True, browser_type="chromium") as browser:
            assert browser._page is not None

        # Verify cleanup was called
        mock_context.close.assert_called_once()
        mock_browser.close.assert_called_once()
        mock_pw.stop.assert_called_once()

    @patch("mini_fb_service.browser.sync_playwright")
    def test_login_success(self, mock_playwright):
        """Test successful login flow."""
        mock_pw = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_pw.return_value.start.return_value = mock_pw
        mock_pw.chromium.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_playwright.return_value = mock_pw

        browser = FacebookBrowser(headless=True, browser_type="chromium")
        browser.start()

        # Mock login flow
        mock_page.goto.return_value = None
        mock_page.fill.return_value = None
        mock_page.click.return_value = None
        mock_page.wait_for_load_state.return_value = None

        # Set URL after login (success)
        mock_page.url = "https://www.facebook.com/home"

        # Mock cookies
        mock_context.cookies.return_value = [
            {"name": "datr", "value": "test123"},
            {"name": "xs", "value": "test456"},
        ]

        cookie = browser.login(email="test@example.com", password="password123")

        assert cookie == "datr=test123; xs=test456"
        mock_page.goto.assert_called_with("https://www.facebook.com/login", wait_until="networkidle")
        mock_page.fill.assert_any_call('input[name="email"]', "test@example.com")
        mock_page.fill.assert_any_call('input[name="pass"]', "password123")
        mock_page.click.assert_called_once_with('button[name="login"]')

    @patch("mini_fb_service.browser.sync_playwright")
    def test_login_failure(self, mock_playwright):
        """Test login failure (still on login page)."""
        mock_pw = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_pw.return_value.start.return_value = mock_pw
        mock_pw.chromium.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_playwright.return_value = mock_pw

        browser = FacebookBrowser(headless=True, browser_type="chromium")
        browser.start()

        # Mock login flow
        mock_page.goto.return_value = None
        mock_page.fill.return_value = None
        mock_page.click.return_value = None
        mock_page.wait_for_load_state.return_value = None

        # Set URL after login (failure - still on login page)
        mock_page.url = "https://www.facebook.com/login"

        cookie = browser.login(email="test@example.com", password="wrong_password")

        assert cookie is None

    @patch("mini_fb_service.browser.sync_playwright")
    def test_extract_account_id_from_url(self, mock_playwright):
        """Test extracting account ID from URL."""
        mock_pw = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_pw.return_value.start.return_value = mock_pw
        mock_pw.chromium.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_playwright.return_value = mock_pw

        browser = FacebookBrowser(headless=True, browser_type="chromium")
        browser.start()

        # Mock navigation
        mock_page.goto.return_value = None

        # Set URL with account ID
        mock_page.url = "https://www.facebook.com/profile.php?id=123456789&ref=bookmarks"

        account_id = browser.extract_account_id()

        assert account_id == "123456789"

    @patch("mini_fb_service.browser.sync_playwright")
    def test_extract_account_id_from_meta(self, mock_playwright):
        """Test extracting account ID from meta tag."""
        mock_pw = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_pw.return_value.start.return_value = mock_pw
        mock_pw.chromium.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_playwright.return_value = mock_pw

        browser = FacebookBrowser(headless=True, browser_type="chromium")
        browser.start()

        # Mock navigation and evaluate
        mock_page.goto.return_value = None
        mock_page.evaluate.return_value = "987654321"

        account_id = browser.extract_account_id()

        assert account_id == "987654321"
        mock_page.goto.assert_called_with("https://www.facebook.com/me", wait_until="networkidle")
