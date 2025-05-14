import logging
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
)
from pathlib import Path
from collections import namedtuple
from pprint import pprint
import aiofiles
import aiocsv
from bs4 import BeautifulSoup
import csv


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def uz_click_download_link(driver: webdriver, wait: WebDriverWait):
    """
    Perform a Selenium task that navigates to a URL, finds a button,
    and clicks it to download a file
    """
    driver.save_screenshot(f"/app/screenshots/screenshot_1{time.time()}.png")
    logger.info("Looking for the download link")
    wait.until(
        EC.all_of(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "section form div img ~div")),
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "section form div img ~div")
            ),
        )
    )
    driver.save_screenshot(f"/app/screenshots/screenshot_2{time.time()}.png")
    wait.until(
        EC.none_of(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "tbody.ant-table-tbody tr.ant-table-placeholder")
            ),
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "tbody.ant-table-tbody tr.ant-table-placeholder")
            ),
        )
    )
    driver.save_screenshot(f"/app/screenshots/screenshot_3{time.time()}.png")

    logger.info("Clicking the download link")
    dw_link = driver.find_element(By.CSS_SELECTOR, "section form div img ~div")
    dw_link.click()


Record = namedtuple(
    "Record",
    ["id", "drug_name", "producer", "mnn", "registration_number", "price", "currency"],
)


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


def uz_paginate(driver: webdriver, url: str, wait: WebDriverWait):
    current_page = 68
    while True:
        cur_url = f"{url}?page={current_page}&size=200"
        logger.info(f"Current URL: {cur_url}")
        driver.get(cur_url)
        logger.info(f"Navigating to page {current_page}")

        # Wait for table rows to appear
        wait.until(
            EC.all_of(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "tbody.ant-table-tbody tr.ant-table-row")
                ),
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "tbody.ant-table-tbody tr.ant-table-row")
                ),
            )
        )

        # driver.save_screenshot(f"/app/screenshots/screenshot_{current_page + 1}.png")
        # Wait for placeholder to disappear
        wait.until(
            EC.none_of(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "tbody.ant-table-tbody tr.ant-table-placeholder")
                ),
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "tbody.ant-table-tbody tr.ant-table-placeholder")
                ),
            )
        )

        records_list = []

        soup = BeautifulSoup(
            driver.find_element(By.CSS_SELECTOR, "tbody.ant-table-tbody").get_attribute(
                "innerHTML"
            ),
            "html.parser",
        )

        table_rows = soup.css.select("tr.ant-table-row")
        if not table_rows:
            driver.quit()
            break

        for index, row in enumerate(table_rows):
            _id = row.find("td").text

            _drug_name = row.css.select_one("td:nth-child(2)").text

            _producer = row.css.select_one("td:nth-child(3)").text

            _mnn = row.css.select_one("td:nth-child(4)").text

            _registration_number = row.css.select_one("td:nth-child(5)").text

            _price = row.css.select_one("td:nth-child(6) span")
            if _price:
                _price = _price.text.replace(" ", "")

            _currency = row.css.select_one("td:nth-child(6) span:nth-child(2)")
            if _currency:
                _currency = _currency.text

            logger.info(f"Processing record {index + 1}")
            records_list.append(
                Record(
                    id=_id,
                    drug_name=_drug_name,
                    producer=_producer,
                    mnn=_mnn,
                    registration_number=_registration_number,
                    price=_price,
                    currency=_currency,
                )
            )

        logger.info(f"Found {len(records_list)} records")
        yield records_list

        # "li.ant-pagination-item-active ~li.ant-pagination-item"
        # wait.until(
        #     EC.element_to_be_clickable(
        #         (
        #             By.CSS_SELECTOR,
        #             "li.ant-pagination-item-active ~li.ant-pagination-item",
        #         )
        #     )
        # )
        # next_page_link = driver.find_element(
        #     By.CSS_SELECTOR, "li.ant-pagination-item-active ~li.ant-pagination-item"
        # )
        # logger.info(f"Next page link: {next_page_link}")
        # if not next_page_link:
        #     driver.quit()
        #     break

        current_page += 1


async def uz_download_task(url):
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

    # try:
    # Connect to the Selenium Grid
    logger.info("Connecting to Selenium Hub")
    driver = webdriver.Remote(
        command_executor="http://selenium-hub:4444/wd/hub", options=chrome_options
    )

    logger.info(f"Navigating to {url}")

    wait = WebDriverWait(driver, 100)

    try:
        # Find the download link and click it
        logger.info("Starting to scrape data")
        async with aiofiles.open(Path(download_dir, "data.csv"), "w") as f:
            writer = aiocsv.AsyncWriter(f)
            for data in uz_paginate(driver, url, wait):
                await writer.writerows(data)

    except TimeoutException:
        logger.error("Timeout waiting for download link")
        return []
    except NoSuchElementException as e:
        logger.error(f"Error during Selenium task: {str(e)}")
        return []
    finally:
        driver.quit()
        logger.info("Selenium task completed. Driver closed")


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
        wait = WebDriverWait(driver, 300)

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
