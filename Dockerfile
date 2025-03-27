FROM python:3.9-slim

WORKDIR /app

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create data directory with proper permissions
RUN mkdir -p /app/data && chmod 777 /app/data

COPY ./app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

# Ensure proper permissions for the app directory
RUN chmod -R 755 /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
