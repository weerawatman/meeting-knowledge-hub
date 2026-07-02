FROM python:3.11-slim

WORKDIR /app

# System deps for audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy source before editable install
COPY pyproject.toml .
COPY src/ ./src/
ARG INSTALL_EXTRAS=""
RUN if [ -n "$INSTALL_EXTRAS" ]; then \
      pip install --no-cache-dir -e ".[${INSTALL_EXTRAS}]"; \
    else \
      pip install --no-cache-dir -e .; \
    fi

# Create data dirs
RUN mkdir -p data/uploads data/results data/workdir

EXPOSE 8001

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8001"]
