import os
import json
import chromadb
import boto3
import requests
from flask import Flask, render_template, request, session, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "cambia_esto")

# --- Chroma ---
CHROMA_HOST = os.environ.get("CHROMA_HOST", "chroma")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
CHROMA_COLLECTION = os.environ.get("CHROMA_COLLECTION", "info_ia_generativa")

chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
collection = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION)

# --- Bedrock ---
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_EMBED_MODEL = os.getenv("BEDROCK_EMBED_MODEL", "amazon.titan-embed-text-v2:0")
BEDROCK_CHAT_MODEL = os.getenv("BEDROCK_CHAT_MODEL", "anthropic.claude-3-5-sonnet-20240620")
# --- Kubecost ---
KUBECOST_BASE = os.getenv("KUBECOST_BASE", "http://kubecost-cost-analyzer.kubecost:9090")
KUBECOST_WINDOW = os.getenv("KUBECOST_WINDOW", "today")

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


def call_model(prompt: str) -> str:
    """
    Implementación compatible con modelos Anthropic en Bedrock.
    Recomendado: anthropic.claude-3-5-sonnet-20240620 (como en tu script).
    """
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "messages": [{"role": "user", "content": prompt}],
        }
    )
    resp = brt.invoke_model(
        modelId=BEDROCK_CHAT_MODEL,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    payload = json.loads(resp["body"].read())
    return payload["content"][0]["text"]


@app.get("/health")
def health():
    return "ok", 200


@app.get("/kubecost/summary")
def kubecost_summary():
    window = request.args.get("window", KUBECOST_WINDOW)

    r = requests.get(
        f"{KUBECOST_BASE}/model/allocation",
        params={"window": window, "aggregate": "namespace"},
        timeout=20
    )
    r.raise_for_status()
    payload = r.json()

    out = []
    for item in payload.get("data", []):
        if not isinstance(item, dict):
            continue
        for ns_name, ns_data in item.items():
            if not isinstance(ns_data, dict):
                continue
            out.append({
                "namespace": ns_name,
                "totalCost": round(float(ns_data.get("totalCost", 0.0) or 0.0), 5),
                "cpuCost": round(float(ns_data.get("cpuCost", 0.0) or 0.0), 5),
                "ramCost": round(float(ns_data.get("ramCost", 0.0) or 0.0), 5),
                "pvCost": round(float(ns_data.get("pvCost", 0.0) or 0.0), 5),
                "loadBalancerCost": round(float(ns_data.get("loadBalancerCost", 0.0) or 0.0), 5),
                "start": ns_data.get("start"),
                "end": ns_data.get("end"),
            })

    out.sort(key=lambda x: x["totalCost"], reverse=True)
    return jsonify(window=window, top=out[:20])


@app.route("/", methods=["GET", "POST"])
def index():
    if "historial" not in session:
        session["historial"] = []

    if request.method == "POST":
        pregunta = request.form["pregunta"].strip()
        if not pregunta:
            return render_template("index.html", historial=session["historial"])

        q_emb = embed_query(pregunta)

        results = collection.query(
            query_embeddings=[q_emb],
            n_results=4,
            include=["documents"],
        )

        docs = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]

        context = "\n".join(docs)

        prompt = (
            "Eres un asistente experto en Inteligencia Artificial Generativa.\n"
            "Responde con máximo 300 caracteres, siempre en texto plano.\n"
            "No uses Markdown, listas, ni emojis.\n"
            "Usa únicamente la información del CONTEXTO.\n"
            "Si no está en el contexto, responde: 'No tengo información en el contexto para responder eso.'\n\n"
            f"CONTEXTO:\n{context}\n\n"
            f"PREGUNTA:\n{pregunta}\n\n"
            "RESPUESTA:"
        )

        respuesta = (call_model(prompt) or "").strip()
        if len(respuesta) > 300:
            respuesta = respuesta[:300].rstrip()

        session["historial"].append({"pregunta": pregunta, "respuesta": respuesta})
        session.modified = True

    return render_template("index.html", historial=session["historial"])
