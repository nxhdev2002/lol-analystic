"""
Facebook browser automation using Selenium + undetected_chromedriver.
Handles automated login and cookie extraction.
"""

import logging
import os
import random
import re
import subprocess
import time
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)


def get_chrome_version() -> Optional[str]:
    """
    Get installed Chrome version.
    
    Returns:
        Chrome version as string (e.g., "144"), None if not found
    """
    try:
        # Try Windows
        if os.name == 'nt':
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            ]
            for path in chrome_paths:
                if os.path.exists(path):
                    result = subprocess.run(
                        [path, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        match = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', result.stdout)
                        if match:
                            return match.group(1)
        # Try Linux/Mac
        else:
            result = subprocess.run(
                ['google-chrome', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                match = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', result.stdout)
                if match:
                    return match.group(1)
    except Exception as e:
        logger.warning(f"Could not detect Chrome version: {e}")
    return None


class FacebookBrowser:
    """
    Automated Facebook browser using Selenium + undetected_chromedriver.
    Handles login and cookie extraction.
    """

    def __init__(
        self,
        headless: bool = True,
        chrome_version: Optional[str] = None,
        user_data_dir: Optional[str] = None,
        proxy: Optional[str] = None,
    ):
        self.headless = headless
        self.chrome_version = chrome_version
        self.user_data_dir = user_data_dir
        self.proxy = proxy
        self._driver = None
        self._options = None

    def start(self):
        """Start the browser."""
        try:
            import undetected_chromedriver as uc

            # Detect Chrome version if not provided
            if not self.chrome_version:
                self.chrome_version = get_chrome_version()
                if self.chrome_version:
                    logger.info(f"Detected Chrome version: {self.chrome_version}")
                else:
                    logger.warning("Could not detect Chrome version, letting undetected_chromedriver auto-detect")

            # Configure Chrome options
            self._options = uc.ChromeOptions()

            if self.headless:
                self._options.add_argument("--headless=new")

            # Use proxy if provided (reduces CAPTCHA)
            if self.proxy:
                self._options.add_argument(f"--proxy-server={self.proxy}")

            # Use user data directory for persistent session (reduces CAPTCHA)
            if self.user_data_dir:
                self._options.add_argument(f"--user-data-dir={self.user_data_dir}")

            # Common options for stability and anti-detection
            self._options.add_argument("--no-sandbox")
            self._options.add_argument("--disable-dev-shm-usage")
            self._options.add_argument("--disable-blink-features=AutomationControlled")
            self._options.add_argument("--disable-gpu")
            self._options.add_argument("--window-size=1920,1080")
            self._options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

            # Exclude automation flags
            #self._options.add_experimental_option("excludeSwitches", ["enable-automation"])
            #self._options.add_experimental_option("useAutomationExtension", False)

            # Start the driver with version if detected
            driver_kwargs = {"options": self._options}
            if self.chrome_version:
                driver_kwargs["version_main"] = self.chrome_version
            if self.user_data_dir:
                driver_kwargs["user_data_dir"] = self.user_data_dir
            
            self._driver = uc.Chrome(**driver_kwargs)

            # Remove webdriver property
            self._driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """
            })

            logger.info(f"Started Chromium browser with undetected_chromedriver (headless={self.headless})")

        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise

    def stop(self):
        """Stop the browser."""
        try:
            if self._driver:
                self._driver.quit()
                logger.info("Stopped browser")
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")

    def login(
        self,
        email: str,
        password: str,
    ) -> Optional[str]:
        """
        Perform Facebook login and extract cookie.

        Args:
            email: Facebook account email or phone
            password: Facebook account password

        Returns:
            Cookie string if successful, None otherwise
        """
        try:
            if not self._driver:
                self.start()

            logger.info(f"Navigating to Facebook login page...")
            self._driver.get("https://www.facebook.com/login")

            # Wait for email input to be present
            wait = WebDriverWait(self._driver, 10)
            email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))

            # Fill in login form with human-like delays
            logger.info("Filling login form...")
            time.sleep(random.uniform(0.5, 1.5))  # Random delay before typing
            
            email_input.clear()
            
            # Type email character by character with random delays
            for char in email:
                email_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            time.sleep(random.uniform(0.5, 1.5))  # Random delay before password

            password_input = self._driver.find_element(By.NAME, "pass")
            password_input.clear()
            
            # Type password character by character with random delays
            for char in password:
                password_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            time.sleep(random.uniform(0.5, 1.5))  # Random delay before clicking login

            # Click login button
            login_button = self._driver.find_element(By.NAME, "login")
            login_button.click()

            # Wait for navigation
            time.sleep(3)  # Brief wait for navigation

            # Wait for page to load
            try:
                wait.until(EC.url_changes("https://www.facebook.com/login"))
            except TimeoutException:
                # URL might not have changed if login failed
                pass

            # Check if login was successful
            current_url = self._driver.current_url
            if current_url == "https://www.facebook.com/login":
                logger.error("Login failed - still on login page")
                return None

            # Check for 2FA or other security checks
            if "checkpoint" in current_url:
                logger.warning("Login requires additional verification (2FA/checkpoint)")
                # TODO: Handle 2FA/checkpoint scenarios
                return None

            logger.info(f"Login successful! Current URL: {current_url}")

            # Extract cookies
            cookies = self._driver.get_cookies()
            cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in cookies])

            logger.info(f"Extracted {len(cookies)} cookies")

            return cookie_string

        except Exception as e:
            logger.error(f"Error during login: {e}")
            return None

    def extract_account_id(self) -> Optional[str]:
        """
        Extract Facebook account ID from current session.

        Returns:
            Account ID if found, None otherwise
        """
        try:
            if not self._driver:
                return None

            # Navigate to profile page
            self._driver.get("https://www.facebook.com/me")
            time.sleep(2)  # Wait for page to load

            # Extract account ID from URL or page content
            url = self._driver.current_url
            if "profile.php?id=" in url:
                account_id = url.split("profile.php?id=")[1].split("&")[0]
                logger.info(f"Extracted account ID: {account_id}")
                return account_id

            # Alternative: extract from page content using meta tag
            try:
                meta_tag = self._driver.find_element(By.CSS_SELECTOR, 'meta[property="al:android:url"]')
                meta_content = meta_tag.get_attribute("content")
                import re
                match = re.search(r'/(\d+)$', meta_content)
                if match:
                    account_id = match.group(1)
                    logger.info(f"Extracted account ID: {account_id}")
                    return account_id
            except NoSuchElementException:
                pass

            logger.warning("Could not extract account ID")
            return None

        except Exception as e:
            logger.error(f"Error extracting account ID: {e}")
            return None

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
