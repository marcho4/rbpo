# Build stage
FROM python:3.12-slim AS build
WORKDIR /app
COPY pyproject.toml poetry.lock* requirements*.txt* ./
RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip && \
    pip wheel --wheel-dir=/wheels -r requirements.txt

# Runtime stage
FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
RUN groupadd -r app && useradd -r -g app app
COPY --from=build /wheels /wheels
RUN --mount=type=cache,target=/root/.cache \
    pip install --no-cache-dir /wheels/*

COPY . .

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
