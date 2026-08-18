# Cloud-Orchestra — Deployment Guide

## 1. Local development (single process)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -e ".[api,dev]"

# run the API
uvicorn cloud_orchestra.api.app:app --reload --port 8000

# or run a single remediation
cloud-orchestra run --problem high_cpu

# evaluate
cloud-orchestra eval
cloud-orchestra ablation
```

## 2. Docker Compose (Postgres + Redis + Chroma + API + workers)

```bash
cp .env.example .env             # fill in LLM_API_KEY, GITHUB_TOKEN
docker compose up -d --build
curl http://localhost:8000/health
```

Services:

* `postgres` — system of record.
* `redis` — event bus.
* `chroma` — vector memory.
* `api` — FastAPI control plane.
* `orchestrator-worker` — replicated agent workers.

## 3. Kubernetes

```bash
kubectl apply -f k8s/
kubectl -n cloud-orchestra get pods
```

The manifests deploy Postgres, Redis, Chroma, the orchestrator API, and a
horizontally-autoscaled agent-worker Deployment. Update `LLM_API_KEY` and
`GITHUB_TOKEN` in `k8s/10-config.yaml` (or use a sealed-secret solution).

## 4. Environment variables (key ones)

| Variable | Purpose |
|----------|---------|
| `CLOUD_ORCHESTRA_DATABASE_URL` | `sqlite+aiosqlite:///...` or `postgresql+asyncpg://...` |
| `CLOUD_ORCHESTRA_REDIS_URL` | Redis URL (event bus) |
| `LLM_PROVIDER` / `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` | DeepSeek V4 / GPT-4o |
| `GITHUB_TOKEN` / `GITHUB_REPO_OWNER` / `GITHUB_REPO_NAME` | PR target |
| `MEMORY_PROVIDER` | `memory` (in-mem) or `chroma` |
| `SANDBOX_PROVIDER` | `mock` or `docker` |
| `FEATURE_*` | novelty-vector feature flags |

## 5. Training the FinOps policy (optional, needs PyTorch)

```bash
pip install -e ".[rl]"
cloud-orchestra train-finops --iterations 200 --output models/finops_ppo.pt
```

## 6. Connecting real clouds / GitHub / Terraform

* Real AWS/GCP/Azure metric queries: implement `providers/cloud.py` SDK clients
  (credentials via env). The deterministic `MockCloudClient` is the default.
* Real GitHub PRs: set `GITHUB_*` and use the `RESTGitHubClient` (pass
  `use_rest=True` in `build_github_client`).
* Real Terraform: `build_terraform_provider(local=True)` uses the `terraform`
  CLI from `PATH`.
