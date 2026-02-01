import os, requests

KUBECOST_URL = os.getenv("KUBECOST_URL", "http://kubecost-cost-analyzer.kubecost:9090")

def kubecost_namespace_summary(window="1d", top=5) -> str:
    url = f"{KUBECOST_URL}/model/allocation"
    params = {"window": window, "aggregate": "namespace"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    # Kubecost suele devolver un dict con "data" -> "sets" -> etc.
    # Como puede variar por versión/config, lo ideal es imprimir 1 vez y ajustar el parseo.
    # Aquí dejo una extracción defensiva:
    items = []
    sets = (data.get("data") or {}).get("sets") or {}
    for _, v in sets.items():
        allocs = v.get("allocations") or {}
        for ns, a in allocs.items():
            cost = float(a.get("totalCost", 0))
            items.append((ns, cost))

    items.sort(key=lambda x: x[1], reverse=True)

    lines = [f"Top namespaces (window={window}):"]
    for ns, cost in items[:top]:
        lines.append(f"- {ns}: ${cost:.2f}")

    # costo específico del proyecto
    ai = next((c for n, c in items if n == "ai-rag"), None)
    if ai is not None:
        lines.append(f"ai-rag: ${ai:.2f}")

    return "\n".join(lines)
