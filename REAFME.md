# EKS + Kubecost AI Assistant (RAG)

## Overview
This project demonstrates a complete **FinOps-oriented Kubernetes lab** that integrates real-time cost visibility with Generative AI.

It combines **Amazon EKS**, **Kubecost**, **ChromaDB**, and **Amazon Bedrock** to allow users to ask natural language questions about Kubernetes costs and receive **live, AI-generated answers** based on actual cluster data.

The project is designed as a **hands-on DevOps / FinOps lab**, focusing on cost awareness, automation, and cloud-native best practices.

---

## Key Technologies
- Amazon EKS (Kubernetes)
- Kubecost (FinOps & cost allocation)
- Amazon Bedrock (LLM – on-demand)
- ChromaDB (Vector database for RAG)
- Flask (AI web application)
- Docker & Kubernetes manifests
- IAM + IRSA (secure access)

---

## Architecture
**High-level flow:**

1. EKS cluster provisioned with `eksctl`
2. Kubecost deployed inside the cluster
3. ChromaDB stores FinOps and Kubernetes documentation embeddings
4. Documents are ingested via a Kubernetes Job
5. AI web application:
   - Queries Kubecost live cost data
   - Retrieves context from ChromaDB
   - Calls Amazon Bedrock for inference
6. Users interact through a web UI using natural language

This design keeps infrastructure **ephemeral and cost-efficient**, ideal for labs and demos.

---

## Features
- Live Kubernetes cost queries by namespace
- AI-powered FinOps explanations
- Real Kubecost data (no mock data)
- Secure IAM access using IRSA
- Fully destroyable lab (no leftover resources)
- Cost-aware design (short-lived, on-demand)

---

## Repository Structure
.
├── 00-prereqs # AWS and access prerequisites
├── 01-cluster # EKS cluster, IAM, IRSA, storage
├── 02-kubecost # Kubecost installation and validation
├── 03-ia # AI application, ingestion, and manifests
│ ├── app # Flask AI web app
│ ├── ingest # Document ingestion jobs
│ └── k8s # Kubernetes manifests
├── 04-validation # Screenshots and validation evidence
└── README.md


---

## Deployment Flow
1. Create EKS cluster with `eksctl`
2. Configure IAM roles and IRSA
3. Install Kubecost
4. Deploy ChromaDB
5. Ingest documents into ChromaDB
6. Build and deploy the AI web application
7. Validate results via UI and Kubecost

---

## Validation
Validation screenshots and results are available under:

04-validation/


They include:
- Running Kubernetes workloads
- Successful AI queries
- Live Kubecost cost responses

---

## Roadmap 
Planned improvements:

- CI/CD pipeline to automate:
  - Docker image builds
  - ECR pushes
  - Kubernetes deployments
- Infrastructure automation enhancements
- Improved AI prompts and cost analysis
- Additional FinOps use cases and dashboards

This project is **actively evolving**.
Next planned step: **CI/CD pipeline implementation**.
---

## Open Source & Contributions
This project is **open source**, and contributions are welcome.

### Ways to contribute
- Improve documentation
- Enhance Kubecost parsing logic
- Add new FinOps use cases
- Improve AI prompt engineering
- Optimize performance and cost efficiency
- Add CI/CD automation

Feel free to open an issue or submit a pull request.

---

## License
This project is licensed under the **MIT License**.

You are free to use, modify, and distribute this project, provided that proper attribution to the original author is maintained.

---

## Author
Created by **Roberto Carlos Rodríguez Guzmán**  
GitHub: https://github.com/kuota1