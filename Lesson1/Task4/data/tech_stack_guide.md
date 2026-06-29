# NeuraStack Technologies — Tech Stack Guide

## Overview
This document describes the internal technology stack used across all NeuraStack products. Engineers are expected to use the approved stack unless an exception is granted by the Architecture Review Board (ARB).

---

## Backend

### Primary Language
- **Python 3.12** is the primary backend language for all AI/ML services and data pipelines.
- **TypeScript (Node.js 20 LTS)** is used for API gateway services and real-time features.

### Web Framework
- **FastAPI** is the standard web framework for Python microservices (async, OpenAPI-native).
- **Express.js** is used for TypeScript/Node.js services.

### API Design
- All public APIs follow the **RESTful** design pattern.
- API versioning uses URL path versioning: `/api/v1/`, `/api/v2/`.
- All endpoints are documented via **OpenAPI 3.0** specs (auto-generated with FastAPI).
- Internal microservice communication uses **gRPC** for performance-critical paths.

---

## Frontend

### Framework
- **React 18** with **TypeScript** is the standard frontend framework.
- **Next.js 14** (App Router) is used for all customer-facing web applications.
- Internal tooling and admin dashboards use **Streamlit** (Python).

### Styling
- **Tailwind CSS** is the standard CSS framework.
- **shadcn/ui** is the component library built on top of Tailwind.
- Dark mode is supported on all customer-facing products.

### State Management
- **Zustand** for lightweight client-side state.
- **React Query (TanStack Query)** for server state and data fetching.

---

## Databases

### Primary Database
- **PostgreSQL 16** is the primary relational database for all transactional data.
- Managed on **Azure Database for PostgreSQL — Flexible Server**.
- Connection pooling is handled by **PgBouncer**.

### Caching Layer
- **Redis 7** is used for caching, session storage, and rate limiting.
- Managed on **Azure Cache for Redis**.
- Default cache TTL is 300 seconds (5 minutes) unless otherwise configured.

### Vector Database
- **ChromaDB** is used for vector storage in development and staging.
- **Azure AI Search** (with vector index) is used in production for scalability.
- NumPy-backed in-memory stores are used in local development and small-scale RAG prototypes.

### Search
- **Elasticsearch 8** is used for full-text search in NeuraSearch.
- Hosted on **Elastic Cloud** (Azure region: East US 2).

---

## Cloud Infrastructure

### Cloud Provider
- Primary: **Microsoft Azure** (East US 2 region).
- Disaster Recovery: **Azure West Europe** (hot standby).

### Compute
- Application services run on **Azure Kubernetes Service (AKS)**.
- Kubernetes version: **1.30 (LTS)**.
- Node pools use **Standard_D4s_v5** (4 vCPU, 16 GB RAM) for application workloads.
- GPU nodes use **Standard_NC6s_v3** for AI inference workloads.

### Networking
- Traffic enters via **Azure Application Gateway** (WAF enabled).
- Internal services communicate over a private **Azure Virtual Network (VNet)**.
- DNS managed by **Azure DNS**.
- CDN for static assets: **Azure Front Door**.

---

## AI / ML Stack

### LLM Providers (Supported)
- **Groq Cloud** — Primary LLM provider (LLaMA 3.3 70B, ultra-fast inference).
- **Azure OpenAI** — GPT-4o for enterprise customers (deployed in East US 2).
- **Anthropic Claude** — claude-sonnet-4-5 for high-quality reasoning tasks.
- **Ollama** — Local development and offline testing.

### Embedding Models
- **nomic-embed-text** (via Ollama) — local development.
- **text-embedding-3-small** (Azure OpenAI) — production.
- **all-MiniLM-L6-v2** (sentence-transformers) — fallback for offline environments.

### ML Frameworks
- **PyTorch 2.3** for model training and fine-tuning.
- **Hugging Face Transformers** for model loading and inference.
- **FAISS** for large-scale vector similarity search (>1M vectors).

---

## DevOps & CI/CD

### Version Control
- **GitHub** (github.com/neurastack) — all source code.
- Branch protection rules enforced on `main` and `develop`.

### CI/CD Platform
- **GitHub Actions** for all CI/CD pipelines.
- Pipeline stages: Lint → Test → Build → Scan → Deploy.

### Containerization
- All services are containerized using **Docker**.
- Base images: `python:3.12-slim` (Python), `node:20-alpine` (Node.js).
- Multi-stage builds are mandatory to minimize image size.
- Images are stored in **Azure Container Registry (ACR)**.

### Monitoring & Observability
- **Azure Monitor + Application Insights** for APM and logging.
- **Prometheus + Grafana** for infrastructure metrics.
- **PagerDuty** for on-call alerting and incident management.
- **Sentry** for frontend and backend error tracking.

### Secret Management
- All secrets are stored in **Azure Key Vault**.
- No secrets may be hardcoded in source code or committed to Git.
- Secrets are injected at runtime via Kubernetes Secrets (populated from Key Vault).

---

## Development Environment

### Required Tools
- Python 3.12 (via `pyenv`)
- Node.js 20 LTS (via `nvm`)
- Docker Desktop 4.x
- kubectl 1.30
- Azure CLI 2.x
- Git 2.x

### Local Setup
```bash
git clone git@github.com:neurastack/<repo>.git
cd <repo>
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in your local values
python ingest.py       # build the knowledge base index
streamlit run app.py   # launch the UI
```
