# Selenium WebDriver with FastAPI in Docker

This project demonstrates how to use Selenium WebDriver with Chrome in a containerized environment using Docker Compose. The setup includes:

- Selenium Hub
- Chrome Node
- FastAPI application

## Project Structure

```
selenium_example/
├── app/
│   ├── main.py                # FastAPI application
│   ├── selenium_task.py       # Selenium script
│   ├── requirements.txt       # Python dependencies
│   ├── test_page.html         # Test page with download button
│   └── serve_test_page.py     # Server for test page
├── data/                      # Shared volume for downloaded files
├── Dockerfile                 # Dockerfile for FastAPI app
├── docker-compose.yml         # Docker Compose configuration
└── README.md                  # This file
```

## How It Works

1. The FastAPI application exposes an endpoint `/start-selenium`
2. When this endpoint receives a request, it starts a Selenium task
3. The Selenium task connects to the Chrome node via Selenium Hub
4. It navigates to a specified URL, finds a button, and clicks it
5. The button click triggers a file download to the `/app/data` directory
6. The directory is shared between containers via a Docker volume

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Running the Application

1. Start the containers:

```bash
docker-compose up -d
```

2. The FastAPI application will be available at `http://localhost:8000`

### Testing the Application

1. To test with the included test page, first start the test page server:

```bash
docker-compose exec fastapi-app python serve_test_page.py
```

2. Then make a request to the FastAPI endpoint:

```bash
curl -X POST "http://localhost:8000/start-selenium?url=http://fastapi-app:8080"
```

3. Check the `/data` directory for downloaded files:

```bash
ls -la data/
```

## API Endpoints

- `GET /`: Root endpoint, returns a simple message
- `POST /start-selenium?url={url}`: Starts a Selenium task for the specified URL
- `GET /health`: Health check endpoint

## Customization

To customize the Selenium script for your specific needs, modify the `selenium_task.py` file. You'll likely need to update the CSS selector for the button and possibly add additional wait conditions depending on the target website.
