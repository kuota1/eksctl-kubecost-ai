#!/usr/bin/env bash
set -euo pipefail

kubectl get sc
kubectl -n kubecost get pvc
kubectl -n kubecost get events --sort-by=.metadata.creationTimestamp | tail -n 30