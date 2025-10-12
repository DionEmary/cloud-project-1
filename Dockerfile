# Stage 1: Builder
FROM python:3.9-slim AS builder

WORKDIR /app

# Copy requirements file first to leverage caching
COPY requirements.txt .

# Create directory for dependencies
RUN mkdir -p /install

# Install dependencies into that directory
RUN pip install --no-cache-dir --target=/install -r requirements.txt


# Stage 2: Runtime
FROM python:3.9-slim

WORKDIR /app

# Copy installed dependencies from builder so that we don't need to reinstall them
COPY --from=builder /install /usr/local/lib/python3.9/site-packages

# Copy application code to container
COPY . /app

# Default command to run the data analysis script
CMD ["python", "data_analysis.py"]
