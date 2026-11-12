FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --system --create-home appuser
COPY --chown=appuser:appuser pyproject.toml .
COPY --chown=appuser:appuser app ./app
RUN pip install --no-cache-dir .
COPY --chown=appuser:appuser alembic.ini .
COPY --chown=appuser:appuser migrations ./migrations
USER appuser
EXPOSE 4000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-4000}"]
