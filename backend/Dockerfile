FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for FAISS and Psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies list
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source
COPY . .

# Expose port
EXPOSE 8000

# Set Python path to find app module
ENV PYTHONPATH=/app

# Run server
CMD ["python", "app/main.py"]
