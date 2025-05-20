# Use Python 3.9 as base image
FROM python:3.9-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    find /usr/local/lib/python3.9/site-packages -type d -name "tests" -exec rm -rf {} + && \
    find /usr/local/lib/python3.9/site-packages -type d -name "test" -exec rm -rf {} + && \
    find /usr/local/lib/python3.9/site-packages -type f -name "*.pyc" -delete && \
    find /usr/local/lib/python3.9/site-packages -type f -name "*.pyo" -delete

# Final stage
FROM python:3.9-slim

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy only necessary application files
COPY ui/ ui/
COPY src/ src/
COPY requirements.txt .

# Set Python path for relative imports
ENV PYTHONPATH=/app

# Expose Streamlit's default port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
