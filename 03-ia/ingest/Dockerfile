FROM python:3.11-slim

WORKDIR /app

# Dependencias
RUN pip install --no-cache-dir boto3 chromadb python-docx requests

# Copiamos scripts y documentos
COPY subir_documentos_chroma.py /app/subir_documentos_chroma.py
COPY 04-traer-y-resumir.py /app/04-traer-y-resumir.py
COPY documentos /app/documentos

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

CMD ["python", "/app/subir_documentos_chroma.py"]
