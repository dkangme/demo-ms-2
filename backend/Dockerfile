FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port that Cloud Run expects
EXPOSE 8080

# Environment variables (defaults; overwritten by Cloud Run)
ENV GCP_PROJECT=""
ENV FIRESTORE_COLLECTION="clientes"
ENV APP_PORT=8080
ENV PYTHONUNBUFFERED=1

# Entrypoint
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
