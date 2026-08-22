FROM python:3.12-slim@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY requirements.txt ./
RUN pip install --no-cache-dir --retries 5 --timeout 120 -r requirements.txt

COPY ml ./ml
COPY remediation ./remediation
COPY observability ./observability

RUN adduser --system --uid 10001 --group autoguard
USER 10001
