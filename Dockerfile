# RAG LLM API Dockerfile - RHEL 9 Base Image
# Multi-stage build for optimized production image

# =============================================================================
# STAGE 1: Base RHEL 9 with system dependencies
# =============================================================================
FROM registry.access.redhat.com/ubi9/ubi:latest AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies and development tools
RUN dnf update -y && \
    dnf install -y \
        python3 \
        python3-pip \
        python3-devel \
        gcc \
        gcc-c++ \
        make \
        wget \
        curl \
        git \
        ca-certificates \
        openssl \
        && \
    dnf clean all

# =============================================================================
# STAGE 2: Install OCR and image processing dependencies
# =============================================================================
FROM base AS ocr-deps

# Install Tesseract OCR and related dependencies
RUN dnf install -y \
        tesseract \
        tesseract-langpack-eng \
        tesseract-langpack-fra \
        tesseract-langpack-deu \
        tesseract-langpack-spa \
        poppler-utils \
        poppler-cpp-devel \
        libpoppler-cpp \
        && \
    dnf clean all

# Install additional image processing libraries
RUN dnf install -y \
        libjpeg-turbo-devel \
        libpng-devel \
        libtiff-devel \
        freetype-devel \
        lcms2-devel \
        libwebp-devel \
        tcl-devel \
        tk-devel \
        && \
    dnf clean all

# =============================================================================
# STAGE 3: Python dependencies and application setup
# =============================================================================
FROM ocr-deps AS app-deps

# Create application user and directory
RUN useradd --create-home --shell /bin/bash app && \
    mkdir -p /app && \
    chown -R app:app /app

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

# =============================================================================
# STAGE 4: Application code and final setup
# =============================================================================
FROM app-deps AS production

# Switch to app user
USER app

# Copy application code
COPY --chown=app:app app/ ./app/
COPY --chown=app:app config/ ./config/
COPY --chown=app:app scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p /app/logs /app/temp /app/certs

# Set environment variables for the application
ENV PYTHONPATH=/app \
    APP_ENV=production \
    HOST=0.0.0.0 \
    PORT=8000 \
    TESSERACT_LANG=eng \
    OCR_CONFIDENCE_THRESHOLD=60

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# STAGE 5: Development image with testing dependencies
# =============================================================================
FROM app-deps AS development

# Switch to app user
USER app

# Copy application code
COPY --chown=app:app app/ ./app/
COPY --chown=app:app config/ ./config/
COPY --chown=app:app scripts/ ./scripts/
COPY --chown=app:app tests/ ./tests/
COPY --chown=app:app docs/ ./docs/
COPY --chown=app:app README.md .
COPY --chown=app:app .gitignore .

# Create necessary directories
RUN mkdir -p /app/logs /app/temp /app/certs /app/htmlcov

# Set environment variables for development
ENV PYTHONPATH=/app \
    APP_ENV=development \
    HOST=0.0.0.0 \
    PORT=8000 \
    DEBUG=True \
    TESSERACT_LANG=eng \
    OCR_CONFIDENCE_THRESHOLD=60

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command for development
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 