FROM python:3.9-slim

WORKDIR /app

# Install system dependencies required for PostgreSQL and healthcheck
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source
COPY ./src /app/src
COPY ./static /app/static

# Create static directory for media files if it doesn't exist
RUN mkdir -p /app/static/media

# Make entrypoint script executable
COPY src/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set proper environment variables
ENV PYTHONPATH=/app

# Expose the port
EXPOSE 8000

# Set entrypoint to our custom script
ENTRYPOINT ["/app/entrypoint.sh"]

# Run the application
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"] 