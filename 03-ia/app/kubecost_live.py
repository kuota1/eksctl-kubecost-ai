# kubecost_live.py
import os
import time
import requests

KUBECOST_BASE = os.getenv(
    "KUBECOST_BASE",
    "http://kubecost-frontend.kubecost.svc.cluster.local:9090"
)

# cache simple
_CACHE = {"ts": 0, "text": None}
_CACHE_TTL = int(os.getenv("KUBECOST_CACHE_TTL", "90"))  # segundos


def should_fetch_kubecost(question: str) -> bool:
    q = (question or "").lower()
    keywords = [
        "cost", "costs", "costo", "costos", "gasto", "gastos", "spend",
        "kubecost", "namespace", "namespaces", "pod", "pods", "node", "nodes",
        "ahorro", "optimiz", "saving", "chargeback", "showback"
    ]
    return any(k in q for k in keywords)


def kubecost_namespace_summary(window="today", top=8) -> str:
    url = f"{KUBECOST_BASE.rstrip('/')}/model/allocation"
    params = {"window": window, "aggregate": "namespace"}
    r = requests.get(url, params=params, timeout=(3, 25))
    r.raise_for_status()

    data = r.json()
    totals = {}

    # Normalizar: si viene list, envolver
    if isinstance(data, list):
        data = {"data": data}

    if not isinstance(data, dict):
        return f"Kubecost live summary: unexpected JSON type={type(data)}"

    data_data = data.get("data")

    # Formato "sets" (dict)
    if isinstance(data_data, dict):
        sets = data_data.get("sets") or {}
        if isinstance(sets, dict) and sets:
            for _, v in sets.items():
                allocs = v.get("allocations") or {}
                for ns, a in allocs.items():
                    cost = a.get("totalCost") or a.get("cost") or 0
                    try:
                        cost = float(cost)
                    except Exception:
                        cost = 0.0
                    totals[ns] = totals.get(ns, 0.0) + cost

    # Formato lista (tu caso): [{"__idle__": {...}}, {"ai-rag": {...}}]
    elif isinstance(data_data, list):
        for entry in data_data:
            if isinstance(entry, dict):
                for k, v in entry.items():
                    if isinstance(v, dict):
                        ns = (
                            v.get("name")
                            or v.get("properties", {}).get("namespace")
                            or k
                        )
                        cost = v.get("totalCost") or v.get("cost") or 0
                        try:
                            cost = float(cost)
                        except Exception:
                            cost = 0.0
                        if ns:
                            totals[ns] = totals.get(ns, 0.0) + cost

    # Ordenar y formatear salida
    items = sorted(totals.items(), key=lambda x: x[1], reverse=True)

    lines = [f"Kubecost live summary (window={window}):"]
    for ns, cost in items[:top]:
        lines.append(f"- {ns}: ${cost:.2f}")

    return "\n".join(lines)


def get_kubecost_context(pregunta: str) -> str:
    """
    Regresa contexto de Kubecost para el prompt.
    - En DEBUG no filtra.
    - Ya incluye cache para no pegarle a Kubecost a cada pregunta.
    """
    debug_no_filter = os.getenv("KUBECOST_DEBUG_NO_FILTER", "true").lower() in ("1", "true", "yes")

    if (not debug_no_filter) and (not should_fetch_kubecost(pregunta)):
        return ""

    now = time.time()
    if _CACHE["text"] and (now - _CACHE["ts"] < _CACHE_TTL):
        return _CACHE["text"]

    try:
        text = kubecost_namespace_summary(
            window=os.getenv("KUBECOST_WINDOW", "today"),
            top=int(os.getenv("KUBECOST_TOP", "10"))
        )
        _CACHE["ts"] = now
        _CACHE["text"] = text
        return text
    except Exception as e:
        return f"[Kubecost error] {e}"
