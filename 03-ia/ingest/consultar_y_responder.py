import os
import json
import chromadb
import boto3

COLLECTION_NAME = "info_ia_generativa"
N_RESULTS = 4

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_EMBED_MODEL = os.getenv("BEDROCK_EMBED_MODEL", "amazon.titan-embed-text-v2:0")
BEDROCK_CHAT_MODEL = os.getenv("BEDROCK_CHAT_MODEL", "anthropic.claude-3-5-sonnet-20240620")

brt = boto3.client("bedrock-runtime", region_name=AWS_REGION)

def embed_query(text: str) -> list[float]:
    body = json.dumps({"inputText": text})
    resp = brt.invoke_model(
        modelId=BEDROCK_EMBED_MODEL,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    payload = json.loads(resp["body"].read())
    return payload["embedding"]

def call_llm(prompt: str) -> str:
    # Ejemplo para Claude (formato típico). Puede variar según modelo.
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 200,
        "messages": [{"role": "user", "content": prompt}],
    })
    resp = brt.invoke_model(
        modelId=BEDROCK_CHAT_MODEL,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    payload = json.loads(resp["body"].read())
    # Claude suele devolver content list
    return payload["content"][0]["text"]

chroma = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
collection = chroma.get_or_create_collection(name=COLLECTION_NAME)

query = input("💬 Introduce tu pregunta: ").strip()

q_emb = embed_query(query)

results = collection.query(
    query_embeddings=[q_emb],
    n_results=N_RESULTS,
    include=["documents", "metadatas"],
)

docs = results["documents"][0] if results.get("documents") else []
contexto = "\n".join(docs)

prompt = (
    "Responde usando SOLO el contexto.\n"
    "Máximo 300 caracteres, texto plano, sin listas ni emojis.\n"
    "Si no está en el contexto, responde: 'No tengo información en el contexto para responder eso.'\n\n"
    f"CONTEXTO:\n{contexto}\n\n"
    f"PREGUNTA:\n{query}\n\n"
    "RESPUESTA:"
)

respuesta = call_llm(prompt).strip()
print(respuesta[:300])
