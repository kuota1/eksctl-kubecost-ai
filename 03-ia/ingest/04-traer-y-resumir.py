import os, requests

KUBECOST_BASE = os.getenv(
    "KUBECOST_BASE",
    "http://kubecost-frontend.kubecost.svc.cluster.local:9090"
)

def kubecost_namespace_summary(window="today", top=5) -> str:
    url = f"{KUBECOST_BASE.rstrip('/')}/model/allocation"
    params = {"window": window, "aggregate": "namespace"}
    r = requests.get(url, params=params, timeout=(3, 25))
    r.raise_for_status()
    data = r.json()

    totals = {}

    sets = ((data.get("data") or {}).get("sets") or {})
    if isinstance(sets, dict) and sets:
        for _, v in sets.items():
            allocs = v.get("allocations") or {}
            for ns, a in allocs.items():
                cost = a.get("totalCost") or a.get("cost") or 0
                try:
                    cost = float(cost)
                except Exception:
                    cost = 0
                totals[ns] = totals.get(ns, 0) + cost
    else:
        data_list = data.get("data") or []
        for entry in data_list:
            if isinstance(entry, dict):
                for _, v in entry.items():
                    if isinstance(v, dict):
                        ns = v.get("name") or v.get("properties", {}).get("namespace")
                        cost = v.get("totalCost") or v.get("cost") or 0
                        try:
                            cost = float(cost)
                        except Exception:
                            cost = 0
                        if ns:
                            totals[ns] = totals.get(ns, 0) + cost

    items = sorted(totals.items(), key=lambda x: x[1], reverse=True)

    lines = [f"Kubecost live summary (window={window}):"]
    for ns, cost in items[:top]:
        lines.append(f"- {ns}: ${cost:.2f}")

    ai = totals.get("ai-rag")
    if ai is not None:
        lines.append(f"ai-rag: ${ai:.2f}")

    return "\n".join(lines)
