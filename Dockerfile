# Use the official Playwright image which includes browsers and system deps
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install Python dependencies
RUN python -m pip install --upgrade pip setuptools wheel
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libgtk-3-0 \
    libasound2 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

# Copy source code
COPY src ./src

# Set default output path inside container; can be overridden with -e CSV_FILE=...
ENV CSV_FILE=/data/out.csv

# Default command to run the application
CMD ["python", "src/main.py"]