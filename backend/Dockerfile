FROM python:3.12-slim

WORKDIR /app

# Install build tools if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend app code
COPY backend/app/ /app/app/
COPY .env* /app/

# Expose FastAPI port
EXPOSE 8000

ENV PYTHONPATH=/app

CMD ["python", "app/main.py"]
