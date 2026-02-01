#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="kubecost"
RELEASE="kubecost"
CLUSTER_ID="${CLUSTER_ID:-eksctl-kubecost-ia}"

# Repo correcto para Kubecost 3.x
helm repo rm kubecost >/dev/null 2>&1 || true
helm repo add kubecost https://kubecost.github.io/kubecost/ >/dev/null
helm repo update >/dev/null

kubectl create namespace "${NAMESPACE}" 2>/dev/null || true

helm upgrade --install "${RELEASE}" kubecost/kubecost \
  --namespace "${NAMESPACE}" \
  --set global.clusterId="${CLUSTER_ID}"