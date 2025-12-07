FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY gdelt_wrapper.py .
COPY main.py .
COPY mcp_server.py .

# Create exports directory
RUN mkdir -p exports

# Expose port
EXPOSE 8004

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8004/health')"

# Run the service
CMD ["python", "main.py"]
