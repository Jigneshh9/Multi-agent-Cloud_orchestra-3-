# Cloud-Orchestra — Architecture

This document describes the system design, the ten agents, the communication
protocols, and the six novelty vectors. It is the reference for the research
paper's *System Design* section.

## 1. Design goals

1. **Closed-loop self-healing** — verify that a remediation actually resolved
   the alert, and roll back if it did not.
2. **Adversarial security validation** — deploy proposed infrastructure into an
   isolated sandbox and run penetration tests, not just static scans.
3. **RL-powered FinOps** — learn progressively cheaper configurations with PPO.
4. **Persistent memory with evolution** — store past deployments in a vector DB
   and retrieve them with RAG.
5. **Observability & explainability** — log every decision trace and generate
   human-readable explanations for every action.
6. **Multi-cloud orchestration** — choose the best provider per task.

## 2. Architecture style

Cloud-Orchestra is an **event-driven microservices system coordinated by a saga
Orchestrator**, packaged so it also runs as a **modular monolith** for
development, evaluation, and the single-binary demo.

* Agents are **independent, stateless, horizontally-scalable services**.
* They communicate **only through a message bus** (Redis Streams with consumer
  groups in production; an in-process bus for tests/eval). Every message is an
  immutable `Event`.
* The **Orchestrator** owns the healing *saga* — a deterministic state machine
  (`RunStatus`) that sequences the agents and implements retry/compensation
  (harden → rollback).
* System state lives in **PostgreSQL** (SQLAlchemy 2.0 async; SQLite fallback
  for tests). Long-term memory lives in **ChromaDB** (in-memory fallback).

This gives three deployment modes:

| Mode | Bus | DB | Agents | Use |
|------|-----|----|--------|-----|
| In-process | `InMemoryEventBus` | `InMemoryRepository` | same process | tests, eval, ablation |
| Single binary | `InMemoryEventBus` | SQLite/Postgres | same process | local demo |
| Distributed | `RedisStreamBus` | Postgres | separate pods | production |

## 3. The agents

| Agent | Responsibility | Novelty vector |
|-------|----------------|----------------|
| **Monitoring** | Ingest CloudWatch/GCP/Azure alerts, normalise to `Alert` | — |
| **Cloud Harmonizer** | Score AWS/GCP/Azure on cost/latency/compliance | #6 |
| **DevOps** | Generate a typed `TerraformPlan` (rule-based or LLM + RAG) | — |
| **Review** | Static security/cost audit → findings + comments | — |
| **Red Team** | Deploy to sandbox, run attack modules → dynamic findings | #2 |
| **FinOps** | PPO-learned cost optimisation (greedy baseline) | #3 |
| **Verifier** | Check the applied plan resolved the alert | #1 |
| **Rollback** | Revert a failed remediation | #1 |
| **Memory Curator** | Store/retrieve deployments in the vector DB | #4 |
| **Explainer** | Generate human-readable Markdown explanations | #5 |

## 4. The saga workflow

```
Alert ─► Harmonize provider ─► Retrieve memory (RAG)
      ─► DevOps generates TerraformPlan
      ─► Review (static) + Red Team (sandbox pentest)
      ─► Harden loop (remediate findings, re-review)   [≤ 3 iterations]
      ─► FinOps cost-optimise (PPO)
      ─► Open GitHub PR + review comments
      ─► Apply Terraform (dry-run or real CLI)
      ─► Verify resolution ── resolved? ──► Store memory ──► Explain
                                    └── no ──► Rollback ──► Store memory ──► Explain
```

Each step publishes an event and records a `DecisionTrace` with an ambient
trace context, so every run is fully replayable and attributable.

## 5. Terraform intermediate representation (key design decision)

The DevOps Agent emits a **typed `TerraformPlan`** (Pydantic) rather than raw
HCL. A deterministic renderer (`render_hcl`) serialises it to HCL. This makes
plans machine-checkable: the Review Agent runs static rules over the IR, the
Red Team derives an *attack surface* from it, and FinOps rewrites tiers/counts
safely. It also reduces LLM hallucination (only the IR is generated, the HCL is
deterministic).

## 6. Communication & data contracts

* **Event bus topics** (`core/events.py`): `alert_received`, `run_started`,
  `provider_selected`, `terraform_generated`, `review_completed`,
  `red_team_completed`, `cost_optimized`, `pr_opened`, `applied`, `verified`,
  `rolled_back`, `memory_stored`, `run_completed`, `run_failed`.
* **Database tables** (`db/models.py`): `alerts`, `runs`, `decision_traces`,
  `review_comments`, `security_findings`, `memory_entries`, `evaluation_runs`.
* **Domain contracts** (`schemas/__init__.py`): `Alert`, `TerraformPlan`,
  `SecurityFinding`, `ReviewResult`, `VerificationResult`, `MemoryEntry`,
  `Run`, `PullRequest`, `ProviderRecommendation`.

## 7. Novelty vectors in detail

### 7.1 Closed-loop self-healing (Verifier + Rollback)
After `apply`, the **Verifier** queries the (simulated or real) post-apply
metric and compares it to the alert threshold (`resolved` / `partial` /
`degraded`). If unresolved and rollback is enabled, the **Rollback** agent
destroys the applied resources. Feature flags: `FEATURE_VERIFIER`,
`FEATURE_ROLLBACK`.

### 7.2 Adversarial validation (Red Team)
The Red Team **deploys the plan into a sandbox** and runs attack modules
(`exposed_database`, `open_port_scan`, `data_at_rest_check`,
`privilege_escalation`, `default_credential_check`, `vulnerability_scan`).
The sandbox's `attack_surface` includes **runtime-only** signals (default
credentials, unpatched OS) that static scanning cannot see. Every finding is
marked `found_by_red_team` for attribution.

### 7.3 RL-powered FinOps
A small PPO agent (`rl/ppo.py`) learns, in the `FinOpsEnv`, to reach the
cheapest `(tier, count)` that still satisfies capacity demand. The greedy
baseline ("downsize one tier") is the ablation comparator. Without PyTorch the
agent falls back to the analytic optimum.

### 7.4 Persistent memory
The Memory Curator writes a summary of every deployment into the vector store;
the DevOps Agent retrieves similar past deployments (RAG) and **reuses proven
cheaper configurations**. Validated by unit tests (`test_devops.py`) and the
LLM-in-the-loop path.

### 7.5 Observability & explainability
`Tracer` records a `DecisionTrace` per agent step (agent, step, rationale,
tokens, latency) under a contextvar-propagated run context. The Explainer
renders the full trace into Markdown. The metrics registry exports Prometheus
text.

### 7.6 Multi-cloud harmonization
The Harmonizer scores providers on cost index, latency and compliance
constraints and returns a ranked, explainable `ProviderRecommendation`.

## 8. Failure handling

* The saga catches any agent failure, marks the run `FAILED`, records the error
  and emits `run_failed`.
* The harden loop caps remediation at 3 iterations.
* Rollback runs only after a failed verification.
* Every external call (LLM, GitHub, Terraform, cloud) is behind a typed
  interface with a deterministic mock, so failures are reproducible in tests.

## 9. Evaluation & ablations

See `docs/paper-outline.md` and `src/cloud_orchestra/eval/`. The four KPIs are
TSR, SFR, Cost Savings and MTTR; the five ablation studies disable
closed-loop, adversarial, RL, memory and harmonization respectively.
