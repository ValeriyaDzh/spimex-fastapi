FROM python:3.11-slim

ENV POETRY_VERSION=1.8.3

WORKDIR /app

COPY ./ /app

RUN python -m pip install --no-cache-dir "poetry==${POETRY_VERSION}" \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi \
    && pip cache purge

EXPOSE 8000

