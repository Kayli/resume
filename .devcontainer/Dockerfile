FROM mcr.microsoft.com/devcontainers/python:3.14

RUN apt-get update \
    && apt-get install -y --no-install-recommends just nodejs npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspaces/resume

COPY pyproject.toml /workspaces/resume/pyproject.toml

RUN python -m pip install --upgrade pip \
    && python -m pip install -e ".[dev]"
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN mkdir -p /ms-playwright \
    && npx playwright install chromium \
    && chmod -R a+rX /ms-playwright

RUN sudo npx playwright install-deps

# Install additional packages required for Cloud SDK, then install Cloud SDK
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl apt-transport-https ca-certificates gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux \
    && mkdir -p /usr/share/keyrings \
    && curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
        | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
        > /etc/apt/sources.list.d/google-cloud-sdk.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-cloud-sdk \
    && rm -rf /var/lib/apt/lists/*

