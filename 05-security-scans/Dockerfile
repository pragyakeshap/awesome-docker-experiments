# Security-hardened Dockerfile following best practices
FROM python:3.11-slim as builder

# Build stage - install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage - minimal base image
FROM python:3.11-slim as runtime

# Install only runtime dependencies and security updates
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user with specific UID/GID
RUN groupadd -r -g 1000 appgroup && \
    useradd -r -g appgroup -u 1000 -d /app -s /bin/bash appuser

# Set working directory and copy from builder
WORKDIR /app
COPY --from=builder --chown=appuser:appgroup /root/.local /home/appuser/.local
COPY --chown=appuser:appgroup . .

# Set secure environment
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Remove package managers to reduce attack surface
RUN rm -rf /usr/bin/apt* /usr/bin/dpkg* /var/lib/dpkg /var/cache/apt

# Set file permissions
RUN chown -R appuser:appgroup /app && \
    chmod -R 755 /app && \
    chmod -R 644 /app/*.py

# Switch to non-root user
USER appuser

# Use specific port (not 80/443)
EXPOSE 8080

# Health check with timeout
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Add labels for metadata
LABEL maintainer="security-team@company.com" \
      version="1.0.0" \
      description="Security-hardened AI API" \
      org.opencontainers.image.source="https://github.com/company/secure-ai-api"

# Run with specific signal handling
CMD ["python", "-u", "app.py"]
