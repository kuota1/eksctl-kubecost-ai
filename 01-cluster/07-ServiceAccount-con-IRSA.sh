#!/usr/bin/env bash
set -euo pipefail

CLUSTER="eks-kubecost-lab"
REGION="us-east-1"
NAMESPACE="ai-rag"
SA_NAME="ai-rag-sa"
POLICY_ARN="arn:aws:iam::084375558336:policy/ai-rag-bedrock-invoke"
ROLE_NAME="AmazonEKS_BedrockInvokeRole"

kubectl create namespace ai-rag --dry-run=client -o yaml | kubectl apply -f -

eksctl create iamserviceaccount \
  --cluster "$CLUSTER" \
  --region "$REGION" \
  --name "$SA_NAME" \
  --namespace "$NAMESPACE" \
  --role-name "$ROLE_NAME" \
  --attach-policy-arn "$POLICY_ARN" \
  --override-existing-serviceaccounts \
  --approve
