import logging
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_download_options(download_dir):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
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
    return chrome_options


def uz_download_task(url):
    """
    Perform a Selenium task that navigates to a URL, finds a button, and clicks it.
    The button click should trigger a file download to the specified directory.

    Args:
        url: The URL to navigate to
    """
    logger.info(f"Starting Selenium task for URL: {url}")

    # Create download directory if it doesn't exist
    download_dir = "/app/data"
    os.makedirs(download_dir, exist_ok=True)

    # Configure Chrome options
    chrome_options = get_download_options(download_dir)

    try:
        # Connect to the Selenium Grid
        logger.info("Connecting to Selenium Hub")
        driver = webdriver.Remote(
            command_executor="http://selenium-hub:4444/wd/hub", options=chrome_options
        )

        logger.info(f"Navigating to {url}")
        driver.get(url)

        # Wait for the page to load
        logger.info("Waiting for page to load")
        wait = WebDriverWait(driver, 200)

        try:
            # Find the download link and click it
            logger.info("Looking for the download link")
            dw_link = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "section form div img"))
            )

            dw_link.click()
            time.sleep(200)  # Wait for download to complete

            # List files in download directory
            files = os.listdir(download_dir)
            logger.info(f"Files in download directory: {files}")

            # Return the list of files
            return files
        except TimeoutException:
            logger.error("Timeout waiting for download link")
            return []
        except Exception as e:
            logger.error(f"Error during Selenium task: {str(e)}")
            return []
        finally:
            driver.quit()
    except Exception as e:
        logger.error(f"Error connecting to Selenium Grid: {str(e)}")
        return []


def curl_download_task(url):
    """
    Perform a Selenium task that navigates to a URL, finds a button, and clicks it.
    The button click should trigger a file download to the specified directory.

    Args:
        url: The URL to navigate to
    """
    logger.info(f"Starting Selenium task for URL: {url}")

    # Create download directory if it doesn't exist
    download_dir = "/app/data"
    os.makedirs(download_dir, exist_ok=True)

    chrome_options = get_download_options(download_dir)

    try:
        # Connect to the Selenium Grid
        logger.info("Connecting to Selenium Hub")
        driver = webdriver.Remote(
            command_executor="http://selenium-hub:4444/wd/hub", options=chrome_options
        )

        logger.info(f"Navigating to {url}")
        driver.get(url)

        # Wait for the page to load
        logger.info("Waiting for page to load")
        wait = WebDriverWait(driver, 30)

        try:
            # Find the download link and click it
            logger.info("Looking for the download link")
            dw_link = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='download/curl']"))
            )

            # Get the href attribute to download directly
            download_url = dw_link.get_attribute("href")
            logger.info(f"Found download URL: {download_url}")

            # Navigate directly to the download URL
            logger.info("Navigating to download URL")
            driver.get(download_url)

            # Wait for the download to complete
            logger.info("Waiting for download to complete")
            time.sleep(20)  # Wait for download to complete

            # List files in download directory
            files = os.listdir(download_dir)
            logger.info(f"Files in download directory: {files}")

            logger.info("Selenium task completed successfully")
        except TimeoutException:
            logger.error("Timed out waiting for download link to be clickable")
        except Exception as e:
            logger.error(f"Error during download: {str(e)}")

        # Close the browser
        driver.quit()

    except WebDriverException as e:
        logger.error(f"WebDriver error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

    logger.info("Selenium task function completed")
