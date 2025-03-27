import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def debug_download():
    """
    Debug script to test file downloads with Selenium Grid
    """
    download_dir = "/app/data"
    os.makedirs(download_dir, exist_ok=True)

    logger.info(f"Download directory: {download_dir}")
    logger.info(f"Directory exists: {os.path.exists(download_dir)}")
    logger.info(f"Directory permissions: {oct(os.stat(download_dir).st_mode)[-3:]}")

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # Set download preferences
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "plugins.always_open_pdf_externally": True,
        "browser.download.manager.showWhenStarting": False,
        "browser.download.folderList": 2,
        "browser.helperApps.neverAsk.saveToDisk": "application/x-gzip,application/zip,application/x-zip-compressed,application/x-tar,application/tar,application/x-7z-compressed,application/octet-stream,application/x-bzip2",
    }
    chrome_options.add_experimental_option("prefs", prefs)

    try:
        # Connect to Selenium Grid
        logger.info("Connecting to Selenium Hub")
        driver = webdriver.Remote(
            command_executor="http://selenium-hub:4444/wd/hub", options=chrome_options
        )

        # Test with a simple file download
        url = "https://curl.se/download.html"
        logger.info(f"Navigating to {url}")
        driver.get(url)

        # Wait for page to load
        wait = WebDriverWait(driver, 30)

        # Find download link
        logger.info("Looking for download link")
        download_link = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='download/curl']"))
        )

        # Get download URL
        download_url = download_link.get_attribute("href")
        logger.info(f"Found download URL: {download_url}")

        # Navigate directly to download URL
        logger.info("Navigating to download URL")
        driver.get(download_url)

        # Wait for download to complete
        logger.info("Waiting for download to complete")
        time.sleep(20)

        # Check if file was downloaded
        files = os.listdir(download_dir)
        logger.info(f"Files in download directory: {files}")

        driver.quit()

    except Exception as e:
        logger.error(f"Error during debug: {str(e)}")


if __name__ == "__main__":
    debug_download()
