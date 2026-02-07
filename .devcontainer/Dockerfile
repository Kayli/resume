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
