#!/usr/bin/env bash
aws iam create-policy \
  --policy-name ai-rag-bedrock-invoke \
  --policy-document file://bedrock-invoke-policy.json
