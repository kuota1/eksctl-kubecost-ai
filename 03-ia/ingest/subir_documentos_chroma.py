import os
import json
import chromadb
import boto3

# --- CONFIG ---
DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", "/app/documentos")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "info_ia_generativa")

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_EMBED_MODEL = os.getenv("BEDROCK_EMBED_MODEL", "amazon.titan-embed-text-v2:0")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def dividir_texto_en_chunks(texto, tamaño=CHUNK_SIZE, solapamiento=CHUNK_OVERLAP):
    chunks = []
    inicio = 0
    while inicio < len(texto):
        fin = min(inicio + tamaño, len(texto))
        chunk = texto[inicio:fin].strip()
        if chunk:
            chunks.append(chunk)
        inicio += tamaño - solapamiento
    return chunks


# Bedrock runtime (usa IAM credentials del entorno: en EKS será IRSA)
brt = boto3.client("bedrock-runtime", region_name=AWS_REGION)

def embed_text(text: str) -> list[float]:
    body = json.dumps({"inputText": text})
    resp = brt.invoke_model(
        modelId=BEDROCK_EMBED_MODEL,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    payload = json.loads(resp["body"].read())
    # Titan embeddings devuelve "embedding"
    return payload["embedding"]


# Chroma server
chroma = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
collection = chroma.get_or_create_collection(name=COLLECTION_NAME)

ids, docs, embeds, metas = [], [], [], []

for filename in os.listdir(DOCUMENTS_DIR):
    if not filename.endswith(".txt"):
        continue

    filepath = os.path.join(DOCUMENTS_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        contenido = f.read()

    chunks = dividir_texto_en_chunks(contenido)

    for i, chunk in enumerate(chunks):
        doc_id = f"{filename}_chunk{i}"
        ids.append(doc_id)
        docs.append(chunk)
        embeds.append(embed_text(chunk))
        metas.append({"source": filename, "chunk": i})

# Subir a Chroma
collection.upsert(ids=ids, documents=docs, embeddings=embeds, metadatas=metas)

print(f" {len(docs)} fragmentos insertados en '{COLLECTION_NAME}'.")

