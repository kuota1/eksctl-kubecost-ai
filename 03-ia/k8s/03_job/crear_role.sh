#!/usr/bin/env bash
aws iam create-role \
  --role-name ai-rag-bedrock-role \
  --assume-role-policy-document file://trust-policy.json