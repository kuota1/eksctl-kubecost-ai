FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask boto3 chromadb gunicorn requests

COPY app.py /app/app.py
COPY templates /app/templates

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]