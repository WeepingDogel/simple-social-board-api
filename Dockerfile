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

# Copy the rest of the application
COPY . .

# Create static directory for media files
RUN mkdir -p static/media

# Make scripts executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/src/init_db.py

# Expose the port
EXPOSE 8000

# Run the application
CMD ["/app/entrypoint.sh"] 