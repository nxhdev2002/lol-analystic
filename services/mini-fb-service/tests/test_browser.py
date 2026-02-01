"""
Unit tests for mini-fb-service browser automation.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from mini_fb_service.browser import FacebookBrowser


class TestFacebookBrowser:
    """Tests for FacebookBrowser."""

    @pytest.fixture
    def browser(self):
        """Create a browser instance for testing."""
        return FacebookBrowser(headless=True)

    def test_browser_initialization(self):
        """Test browser initialization."""
        browser = FacebookBrowser(headless=True)
        assert browser.headless is True
        assert browser._driver is None

    def test_browser_initialization_headful(self):
        """Test browser initialization with headful mode."""
        browser = FacebookBrowser(headless=False)
        assert browser.headless is False

    @patch("undetected_chromedriver.Chrome")
    def test_start(self, mock_chrome):
        """Test starting browser."""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        browser = FacebookBrowser(headless=True)
        browser.start()

        mock_chrome.assert_called_once()
        assert browser._driver is not None

    @patch("undetected_chromedriver.Chrome")
    def test_stop(self, mock_chrome):
        """Test stopping browser."""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        browser = FacebookBrowser(headless=True)
        browser._driver = mock_driver

        browser.stop()

        mock_driver.quit.assert_called_once()

    @patch("undetected_chromedriver.Chrome")
    def test_context_manager(self, mock_chrome):
        """Test browser as context manager."""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        with FacebookBrowser(headless=True) as browser:
            assert browser._driver is not None

        # Verify cleanup was called
        mock_driver.quit.assert_called_once()

    @patch("undetected_chromedriver.Chrome")
    def test_login_success(self, mock_chrome):
        """Test successful login flow."""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        # Mock driver methods
        mock_driver.current_url = "https://www.facebook.com/home"
        mock_driver.get_cookies.return_value = [
            {"name": "datr", "value": "test123"},
            {"name": "xs", "value": "test456"},
        ]

        # Mock find_element for email input
        mock_email_input = MagicMock()
        mock_password_input = MagicMock()
        mock_login_button = MagicMock()

        def find_element_side_effect(by, value):
            if value == "email":
                return mock_email_input
            elif value == "pass":
                return mock_password_input
            elif value == "login":
                return mock_login_button
            return MagicMock()

        mock_driver.find_element.side_effect = find_element_side_effect

        browser = FacebookBrowser(headless=True)
        browser._driver = mock_driver

        cookie = browser.login(email="test@example.com", password="password123")

        assert cookie == "datr=test123; xs=test456"
        mock_driver.get.assert_called_with("https://www.facebook.com/login")
        mock_email_input.clear.assert_called_once()
        # Check that send_keys was called for each character in email
        assert mock_email_input.send_keys.call_count == len("test@example.com")
        mock_password_input.clear.assert_called_once()
        # Check that send_keys was called for each character in password
        assert mock_password_input.send_keys.call_count == len("password123")
        mock_login_button.click.assert_called_once()

    @patch("undetected_chromedriver.Chrome")
    def test_login_failure(self, mock_chrome):
        """Test login failure (still on login page)."""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        # Mock driver methods
        mock_driver.current_url = "https://www.facebook.com/login"

        # Mock find_element
        mock_email_input = MagicMock()
        mock_password_input = MagicMock()
        mock_login_button = MagicMock()

        def find_element_side_effect(by, value):
            if value == "email":
                return mock_email_input
            elif value == "pass":
                return mock_password_input
            elif value == "login":
                return mock_login_button
            return MagicMock()

        mock_driver.find_element.side_effect = find_element_side_effect

        browser = FacebookBrowser(headless=True)
        browser._driver = mock_driver

        cookie = browser.login(email="test@example.com", password="wrong_password")

        assert cookie is None

    @patch("undetected_chromedriver.Chrome")
    def test_login_checkpoint(self, mock_chrome):
        """Test login requiring checkpoint/2FA."""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        # Mock driver methods
        mock_driver.current_url = "https://www.facebook.com/checkpoint/123456789"

        # Mock find_element
        mock_email_input = MagicMock()
        mock_password_input = MagicMock()
        mock_login_button = MagicMock()

        def find_element_side_effect(by, value):
            if value == "email":
                return mock_email_input
            elif value == "pass":
                return mock_password_input
            elif value == "login":
                return mock_login_button
            return MagicMock()

        mock_driver.find_element.side_effect = find_element_side_effect

        browser = FacebookBrowser(headless=True)
        browser._driver = mock_driver

        cookie = browser.login(email="test@example.com", password="password123")

        assert cookie is None

    @patch("undetected_chromedriver.Chrome")
    def test_extract_account_id_from_url(self, mock_chrome):
        """Test extracting account ID from URL."""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        # Mock driver methods
        mock_driver.current_url = "https://www.facebook.com/profile.php?id=123456789&ref=bookmarks"

        browser = FacebookBrowser(headless=True)
        browser._driver = mock_driver

        account_id = browser.extract_account_id()

        assert account_id == "123456789"
        mock_driver.get.assert_called_with("https://www.facebook.com/me")

    @patch("undetected_chromedriver.Chrome")
    def test_extract_account_id_from_meta(self, mock_chrome):
        """Test extracting account ID from meta tag."""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        # Mock driver methods
        mock_driver.current_url = "https://www.facebook.com/me"

        # Mock meta tag
        mock_meta_tag = MagicMock()
        mock_meta_tag.get_attribute.return_value = "fb://profile/987654321"
        mock_driver.find_element.return_value = mock_meta_tag

        browser = FacebookBrowser(headless=True)
        browser._driver = mock_driver

        account_id = browser.extract_account_id()

        assert account_id == "987654321"
        mock_driver.get.assert_called_with("https://www.facebook.com/me")
        mock_driver.find_element.assert_called_once()

    @patch("undetected_chromedriver.Chrome")
    def test_extract_account_id_not_found(self, mock_chrome):
        """Test extracting account ID when not found."""
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        # Mock driver methods
        mock_driver.current_url = "https://www.facebook.com/me"

        # Mock find_element to raise exception (meta tag not found)
        from selenium.common.exceptions import NoSuchElementException
        mock_driver.find_element.side_effect = NoSuchElementException()

        browser = FacebookBrowser(headless=True)
        browser._driver = mock_driver

        account_id = browser.extract_account_id()

        assert account_id is None
