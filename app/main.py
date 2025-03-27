from fastapi import FastAPI, BackgroundTasks
import logging
from selenium_task import curl_download_task, uz_download_task
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def root():
    contents = Path("data").glob("*.*")
    return {
        "message": "Selenium WebDriver API is running",
        "files": [c.name for c in contents],
    }


@app.post("/start-selenium")
async def start_selenium(
    background_tasks: BackgroundTasks,
    url: str = "https://uzpharmagency.uz/ru/reference-prices",
):
    """
    Endpoint to start a Selenium task that loads a page and clicks a button.
    The button click should trigger a file download to the specified directory.

    Args:
        url: The URL to navigate to (default: https://uzpharmagency.uz/ru/reference-prices)
    """
    logger.info(f"Received request to start Selenium task for URL: {url}")

    # Add the Selenium task to background tasks
    background_tasks.add_task(uz_download_task, url)

    return {"message": "Selenium task started", "status": "processing"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
