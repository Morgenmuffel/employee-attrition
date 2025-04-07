
FROM python:3.10.6-slim-bullseye

COPY requirements_prod.txt .

# Install build tools, then remove them after pip install
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential git && \
    python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements_prod.txt && \
    apt-get remove -y build-essential git && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Python optimizations
ENV PYTHONFAULTHADDLE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DOCKER_ENV=true \
    LOGGING_LEVEL=INFO

WORKDIR /app

# Install dependencies first for better caching
# COPY requirements_prod.txt .
# RUN pip install --no-cache-dir -r requirements_prod.txt

# Copy application
COPY . .
COPY prestart.sh /prestart.sh
RUN chmod +x /prestart.sh

EXPOSE 8080
CMD ["/prestart.sh"]  
