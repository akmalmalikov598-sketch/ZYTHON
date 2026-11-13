FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN useradd --create-home --uid 10001 appuser

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY zython.py server.py ./

USER appuser

EXPOSE 10000

# Render PORT env ni o'zi beradi; lokal ishlatilganda 10000 ishlatiladi
CMD gunicorn --workers 2 --threads 4 --timeout 30 --bind 0.0.0.0:${PORT:-10000} server:app
