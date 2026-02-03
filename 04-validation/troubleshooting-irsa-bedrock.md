# Troubleshooting – IRSA & Amazon Bedrock Integration

This document describes the real-world troubleshooting process followed to
successfully integrate **Amazon Bedrock** with workloads running inside **Amazon EKS**
using **IAM Roles for Service Accounts (IRSA)**.

The goal was to allow Kubernetes Pods to securely invoke Bedrock models
without static AWS credentials.

---

## Context

- Kubernetes namespace: `ai-rag`
- ServiceAccount: `ai-rag-sa`
- AWS Service: Amazon Bedrock (InvokeModel)
- Authentication method: IRSA (OIDC + AssumeRoleWithWebIdentity)

---

## Issue 1 – Bedrock invocation fails from Kubernetes Job

### Symptom

The document ingestion Job (`chroma-ingest`) failed with the following error:

botocore.exceptions.ClientError:
An error occurred (AccessDenied) when calling the
AssumeRoleWithWebIdentity operation


The pod terminated with status `Error`.

---

### Initial Verification

Checked that the ServiceAccount was correctly annotated:

```bash
kubectl -n ai-rag get sa ai-rag-sa -o yaml | grep role-arn
Result showed a role ARN configured, but Bedrock calls still failed.

Issue 2 – IAM Role did not exist or was incomplete
Root Cause
The referenced IAM role did not exist, or

The role existed but lacked a valid trust relationship with the EKS OIDC provider

Confirmed by running:

aws iam get-role --role-name ai-rag-bedrock-role
Result:

NoSuchEntity: The role with name ai-rag-bedrock-role cannot be found
Resolution – Proper IRSA Role Creation
Step 1 – Identify EKS OIDC Provider
aws eks describe-cluster \
  --name eks-kubecost-lab \
  --region us-east-1 \
  --query "cluster.identity.oidc.issuer" \
  --output text
Example output:

https://oidc.eks.us-east-1.amazonaws.com/id/XXXXXXXX
Step 2 – Create IAM Trust Policy
Created a trust policy allowing the Kubernetes ServiceAccount
to assume the role via web identity:

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/XXXXXXXX"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "oidc.eks.us-east-1.amazonaws.com/id/XXXXXXXX:aud": "sts.amazonaws.com",
          "oidc.eks.us-east-1.amazonaws.com/id/XXXXXXXX:sub": "system:serviceaccount:ai-rag:ai-rag-sa"
        }
      }
    }
  ]
}
Step 3 – Create IAM Role
aws iam create-role \
  --role-name ai-rag-bedrock-role \
  --assume-role-policy-document file://trust-policy.json
Step 4 – Attach Bedrock Invoke Policy
aws iam put-role-policy \
  --role-name ai-rag-bedrock-role \
  --policy-name bedrock-invoke \
  --policy-document file://bedrock-policy.json
The policy allows:

bedrock:InvokeModel

bedrock:InvokeModelWithResponseStream

Step 5 – Annotate Kubernetes ServiceAccount
kubectl -n ai-rag annotate serviceaccount ai-rag-sa \
  eks.amazonaws.com/role-arn=arn:aws:iam::<ACCOUNT_ID>:role/ai-rag-bedrock-role \
  --overwrite
Validation – IRSA Working Correctly
Run a debug pod using the same ServiceAccount
kubectl -n ai-rag run irsa-debug --rm -it \
  --image=python:3.11-slim \
  --restart=Never \
  --overrides='{"spec":{"serviceAccountName":"ai-rag-sa"}}' \
  -- sh
Inside the pod:

pip install boto3
python - << 'PY'
import boto3
sts = boto3.client("sts", region_name="us-east-1")
print(sts.get_caller_identity())
PY
Successful Output
Arn: arn:aws:sts::<ACCOUNT_ID>:assumed-role/ai-rag-bedrock-role/...
This confirmed:

IRSA was working

The pod successfully assumed the IAM role

AWS credentials were injected correctly

Final Result
Document ingestion Job completed successfully

Bedrock embedding and chat models were invoked correctly

AI application retrieved live Kubecost data and generated responses

No static AWS credentials were used at any point

Key Lessons Learned
Always verify IAM role existence before annotating ServiceAccounts

IRSA failures often come from incorrect trust policies, not permissions

Debug pods are the fastest way to validate IRSA

Documenting real troubleshooting adds significant production value

Status
    Resolved and validated
This troubleshooting process reflects real-world AWS + Kubernetes operations.