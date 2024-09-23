# Base image with necessary runtime dependencies
FROM python:3.11.10-slim-bookworm AS base
ARG TARGETARCH

# Install essential OS packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates curl git make openssl tar zip unzip groff-base iputils-ping && \
    apt-get install --only-upgrade libexpat1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Node.js installation (minimized)
RUN ARCH=$(dpkg --print-architecture) && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest && \
    node --version && npm --version

# Create work directory and localstack user
RUN mkdir -p /opt/code/localstack && \
    useradd -ms /bin/bash localstack && \
    mkdir -p /var/lib/localstack /tmp/localstack /.npm && \
    chown -R localstack:localstack /var/lib/localstack /tmp/localstack /.npm

USER localstack
WORKDIR /opt/code/localstack

# Install Python dependencies
COPY requirements-runtime.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-runtime.txt

# Copy entrypoint script and configuration
COPY --chown=localstack:localstack bin/docker-entrypoint.sh /usr/local/bin/
COPY --chown=localstack:localstack bin/hosts /etc/hosts

# Set environment variables
ENV USER=localstack
ENV PYTHONUNBUFFERED=1
EXPOSE 4566 4510-4559 5678

# Healthcheck
HEALTHCHECK CMD localstack status services --format=json

# Default command
ENTRYPOINT ["docker-entrypoint.sh"]
