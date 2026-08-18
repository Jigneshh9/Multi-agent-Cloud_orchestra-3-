<div align="center">
  <h1>☁️ CLOUD-ORCHESTRA</h1>
  <p><b>An Autonomous Multi-Agent Cloud DevOps Orchestrator</b></p>
  
  <p>
    <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-0.100+-green.svg" alt="FastAPI">
    <img src="https://img.shields.io/badge/Coverage-82%25-success.svg" alt="Coverage">
    <img src="https://img.shields.io/badge/License-MIT-purple.svg" alt="License">
    <img src="https://img.shields.io/badge/Docker-Supported-blue.svg" alt="Docker">
  </p>
  
  <p>
    <em>A final-year Computer Engineering research project designed to surpass existing systems like MACOG and InfraGenie.</em>
  </p>
</div>

<hr />

## 📖 Overview

**CLOUD-ORCHESTRA** is a state-of-the-art Multi-Agent system that fully automates Cloud DevOps. When an alert fires (e.g., High CPU, Cost Anomaly), the system orchestrates 10 specialized AI agents to diagnose the issue, write remediation Terraform code, review it for security and cost, securely test it in an adversarial sandbox, and finally apply and verify the fix.

It is built with a deterministic **Saga Workflow Orchestrator**, ensuring every decision is strictly event-driven, logged, and replayable, making it ideal for rigorous empirical ablation studies.

## ✨ The 6 Novelty Vectors

To achieve research-grade novelty, CLOUD-ORCHESTRA implements six advanced capabilities not found in standard automated DevOps pipelines:

| # | Novelty Vector | Description | Primary Agents |
|---|----------------|-------------|----------------|
| 1 | **Closed-Loop Self-Healing** | Instead of fire-and-forget, the system actively checks if applied fixes resolved the alert. If not, it executes a clean rollback. | *Verifier*, *Rollback* |
| 2 | **Adversarial Validation** | Proposed infrastructure is deployed to a live sandbox where a Red Team agent runs active penetration tests to find runtime exploits. | *Red Team* |
| 3 | **RL-Powered FinOps** | Uses a Proximal Policy Optimization (PPO) reinforcement learning agent to learn from past deployments and suggest progressively cheaper configurations. | *FinOps* |
| 4 | **Persistent Shared Memory** | Stores past deployments, failures, and cost metrics in a Vector DB, allowing agents to evolve and use RAG to get smarter over time. | *Memory Curator* |
| 5 | **Full Observability** | Captures complete decision traces via an event bus and synthesizes them into human-readable explanations for GitHub PR comments. | *Explainer* |
| 6 | **Multi-Cloud Harmonization** | Intelligently routes tasks to the most optimal cloud provider (AWS, GCP, Azure) based on real-time cost and latency profiles. | *Cloud Harmonizer* |

## 🏗️ Architecture

The system utilizes an event-driven architecture orchestrated by a central Saga Workflow.

```mermaid
graph TD
    Alert[🚨 CloudWatch/GCP Alert] --> CH[☁️ Cloud Harmonizer]
    CH --> MC[🧠 Retrieve Memory RAG]
    MC --> DevOps[⚙️ DevOps Agent <br> Generates Terraform]
    
    DevOps --> Review[🛡️ Static Security Review]
    DevOps --> RT[⚔️ Red Team <br> Sandbox Pentest]
    
    Review --> Harden{Secure?}
    RT --> Harden
    
    Harden -- No --> DevOps
    Harden -- Yes --> FinOps[💰 FinOps Agent <br> RL Cost Optimization]
    
    FinOps --> PR[🐙 GitHub PR Opened]
    PR --> Apply[🚀 Apply Terraform]
    
    Apply --> Verify[✅ Verifier Agent]
    Verify -- Success --> Store[💾 Store in Vector DB]
    Verify -- Failed --> Rollback[⏪ Rollback Agent]
    Rollback --> Store
    
    Store --> Explain[🗣️ Explainer Agent <br> Generates Trace Report]
```

*For an in-depth look at the architecture, please see [`docs/architecture.md`](docs/architecture.md).*

## 🛠️ Technology Stack

- **Core:** Python 3.11+, asyncio, FastAPI
- **AI/LLM:** DeepSeek V4 / GPT-4o (OpenAI-compatible endpoints)
- **Data & State:** PostgreSQL/SQLite, Redis Streams, ChromaDB (Vector Search)
- **Machine Learning:** PyTorch (for FinOps PPO Reinforcement Learning)
- **Infrastructure:** Terraform, Docker, Kubernetes

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- Make
- Optional: Docker & Kubernetes (for cluster deployment)

### Local Installation

1. **Clone the repository and set up a virtual environment:**
   ```bash
   git clone https://github.com/Jigneshh9/Multi-Agent-Cloud-Orchestrator-Design.git
   cd Multi-Agent-Cloud-Orchestrator-Design
   python -m venv .venv
   
   # Linux/macOS
   source .venv/bin/activate
   # Windows
   .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   # Installs the API, dev tools, and RL dependencies (PyTorch)
   pip install -e ".[api,dev,rl]"
   ```

3. **Verify the installation (Testing, Linting, Type-checking):**
   ```bash
   make test
   make lint
   make typecheck
   ```

## 💻 Usage & CLI

CLOUD-ORCHESTRA provides a powerful command-line interface to interact with the system.

**1. Run a Remediation Workflow**  
Execute a single, end-to-end remediation (default is the `high_cpu` scenario):
```bash
cloud-orchestra run --problem high_cpu
```

**2. Start the Control Plane API**  
Launch the FastAPI backend. You can access the interactive Swagger UI at `http://localhost:8000/docs`:
```bash
cloud-orchestra api
```

**3. Train the FinOps RL Agent**  
Train the Proximal Policy Optimization (PPO) model for cost optimization:
```bash
cloud-orchestra train-finops --iterations 100 --output ./models/finops_ppo.pt
```

**4. Run Evaluations & Ablation Studies**  
The core of the research project is proving the efficacy of the novelty vectors. The system includes a built-in evaluation harness:
```bash
# Run the evaluation harness (Success Rate, Security Finding Rate, Cost Savings, MTTR)
cloud-orchestra eval

# Run the 5 ablation studies to generate comparison deltas vs. baseline
cloud-orchestra ablation
```

## 📂 Project Structure

```text
cloud-orchestra/
├── docs/                 # Documentation (Architecture, API, Deployment, Paper Outline)
├── k8s/                  # Kubernetes deployment manifests
├── src/cloud_orchestra/
│   ├── agents/           # The 10 specialized AI Agents
│   ├── api/              # FastAPI endpoints
│   ├── core/             # Configuration, Logging, Event Bus
│   ├── db/               # Database schemas and repositories
│   ├── eval/             # Ablation and evaluation harness
│   ├── memory/           # RAG and Vector DB integration
│   ├── orchestrator/     # Saga workflow state machine
│   ├── providers/        # AWS, GCP, Azure integrations
│   ├── rl/               # PyTorch PPO Reinforcement Learning models
│   ├── schemas/          # Pydantic data contracts
│   ├── main.py           # CLI entrypoint
│   └── runtime.py        # Core application runtime
├── tests/                # Unit and Integration tests
├── Dockerfile            # Container definition
├── docker-compose.yml    # Local multi-container deployment
└── Makefile              # Development scripts
```

## 📚 Documentation Directory
* [`docs/architecture.md`](docs/architecture.md) — Detailed system design and novelty vectors.
* [`docs/api.md`](docs/api.md) — HTTP API reference.
* [`docs/deployment.md`](docs/deployment.md) — Guides for local, Docker, and Kubernetes deployment.
* [`docs/development.md`](docs/development.md) — Repository layout, conventions, and contributing.
* [`docs/paper-outline.md`](docs/paper-outline.md) — **Research paper structure and evaluation methodology.**

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
