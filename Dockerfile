# Multi-platform: linux/amd64, linux/arm64
# Build with: docker buildx build --platform linux/amd64,linux/arm64 -t mcp-pypandoc-hwpx .

FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/aliencube/mcp-pypandoc-hwpx" \
      org.opencontainers.image.title="mcp-pypandoc-hwpx" \
      org.opencontainers.image.description="MCP server for converting .docx, .html, and .md files to .hwpx format using pypandoc-hwpx" \
      org.opencontainers.image.licenses="MIT"

# Install pandoc and clean up apt cache in a single layer
RUN apt-get update \
    && apt-get install -y --no-install-recommends pandoc \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy dependency manifests first to maximise layer caching
COPY pyproject.toml uv.lock .python-version ./

# Sync dependencies (no dev extras, lockfile enforced)
RUN uv sync --frozen --no-dev

# Copy application source
COPY src/ src/

# Default: stdio transport; pass --http [--port PORT] for Streamable HTTP
ENTRYPOINT ["uv", "run", "python", "-m", "src.server"]
