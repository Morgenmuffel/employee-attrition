
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
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
# local, mlflow
ENV MODEL_TARGET=gcs
# local, gcs, bq
ENV DATA_TARGET=gcs

# local, gcs
ENV DATA_SOURCE=gcs
# Install dependencies first for better caching
# COPY requirements_prod.txt .
# RUN pip install --no-cache-dir -r requirements_prod.txt

# Copy application
COPY . .

# Runtime configuration
EXPOSE 8000
CMD ["uvicorn", "employee_attrition.api.fast:app", "--host", "0.0.0.0", "--port", "8000"]
