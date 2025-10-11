# Use Python 3.9 slim image for smaller size
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy all files to container
COPY . /app

# Install required Python packages
RUN pip install --no-cache-dir pandas matplotlib seaborn

# Run the data analysis script
CMD ["python", "data_analysis.py"]