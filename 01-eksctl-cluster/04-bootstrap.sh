#!/usr/bin/env bash
set -euo pipefail

CLUSTER="eks-kubecost-lab"
REGION="us-east-1"
ROLE_NAME="AmazonEKS_EBS_CSI_DriverRole"

echo "==> Associate OIDC provider (required for IRSA)"
eksctl utils associate-iam-oidc-provider \
  --cluster "$CLUSTER" \
  --region "$REGION" \
  --approve

echo "==> Create IAM role for EBS CSI driver (IRSA)"
eksctl create iamserviceaccount \
  --name ebs-csi-controller-sa \
  --namespace kube-system \
  --cluster "$CLUSTER" \
  --region "$REGION" \
  --role-name "$ROLE_NAME" \
  --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
  --approve \
  --role-only || true

ROLE_ARN=$(aws iam get-role \
  --role-name "$ROLE_NAME" \
  --query 'Role.Arn' \
  --output text)

echo "==> Using IAM Role: $ROLE_ARN"

echo "==> Install aws-ebs-csi-driver addon"
eksctl create addon \
  --name aws-ebs-csi-driver \
  --cluster "$CLUSTER" \
  --region "$REGION" \
  --service-account-role-arn "$ROLE_ARN" \
  --force

echo "==> Verifying CSI driver"
kubectl -n kube-system get pods | grep -i ebs || true
kubectl get csidrivers | grep -i ebs || true

echo "==> EBS CSI bootstrap completed"