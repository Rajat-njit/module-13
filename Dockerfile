# 1. Base image
FROM python:3.11-slim

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements first (better caching)
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy FastAPI app
COPY . .

# 7. Copy frontend static files (Module-13 requirement)
COPY frontend ./frontend

# 8. Security best practice: non-root user
RUN useradd -m appuser
USER appuser

# 9. Expose FastAPI port
EXPOSE 8000

# 10. Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
