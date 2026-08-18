# Cloud-Orchestra — Research Paper Outline

**Working title:** *Cloud-Orchestra: A Multi-Agent, Self-Healing, Adversarially
Validated and RL-Optimised Cloud DevOps Orchestrator with Persistent Memory*

**Target venue:** IEEE/ACM — e.g. ICSE-SEIP, SoCC, EuroSys (industry track), or
a dedicated autonomous-cloud-operations workshop.

---

## Abstract (draft)

Cloud operations teams react to thousands of alerts daily, and existing
LLM-based "InfraOps" assistants (MACOG, InfraGenie, The Kernel) stop at
*generating* a fix — they do not verify it, defend it, or learn from it. We
present **Cloud-Orchestra**, an event-driven multi-agent system that closes the
loop end-to-end. Ten specialised agents ingest multi-cloud alerts, generate a
*typed* Terraform intermediate representation, statically review **and**
adversarially penetration-test the fix in an isolated sandbox, optimise cost
with Proximal Policy Optimisation, open a GitHub PR, **verify** the deployment
resolved the alert, and **roll back** if it did not — all while accumulating
reusable memory in a vector database and emitting human-readable explanations.
Across six representative incident classes we report a Task Success Rate of
100%, a mean Security Finding Rate of 1.67 findings/run, ~47% mean monthly cost
savings, and sub-second Mean Time To Remediation. Five ablation studies isolate
the contribution of each novelty vector.

---

## 1. Introduction

* Background: cloud incidents, alert fatigue, the rise of LLM-based DevOps
  assistants.
* Problem: existing systems (cite MACOG, InfraGenie, The Kernel) are
  **open-loop** — they propose, they do not close the loop (no verification,
  no rollback, no learning, shallow security).
* Contributions (map 1:1 to the six novelty vectors):
  1. Closed-loop self-healing (Verifier + Rollback).
  2. Adversarial validation via sandbox penetration testing (Red Team).
  3. RL-based FinOps (PPO) for progressive cost reduction.
  4. Persistent shared memory (vector DB + RAG) for organisational learning.
  5. Full observability + explainability (decision traces + explanations).
  6. Multi-cloud harmonization.
* Key design insight: a **typed Terraform IR** makes plans machine-checkable
  and deterministic to render, reducing LLM hallucination and enabling static
  analysis.

## 2. Related Work

* **LLM agents for infra**: MACOG, InfraGenie, The Kernel, Devin-style coding
  agents — position and limitations (single-cloud, no closed loop, static-only
  security).
* **Self-healing / autonomic computing**: MAPE-K loop; Kubernetes controllers;
  PagerDuty/RunDeck automation.
* **AI for security**: static IaC scanners (Checkov, tfsec); adversarial
  testing; red-teaming of code agents.
* **RL for systems**: resource autoscaling with DRL; FinOps cost optimisers.
* **Agent memory**: RAG, retrieval-augmented agents, MemGPT-style memory.
* **Multi-agent orchestration**: LangGraph, AutoGen, CrewAI — contrast with our
  event-driven saga + typed contracts.

## 3. System Design

Mirror `docs/architecture.md`:

* 3.1 Architecture (event-driven microservices + saga orchestrator).
* 3.2 The ten agents and their contracts.
* 3.3 Terraform IR and deterministic HCL rendering.
* 3.4 Event bus & database schema (include a figure of the workflow).
* 3.5 The six novelty vectors, with pseudocode for:
  - verification/rollback policy,
  - sandbox attack-surface derivation,
  - PPO objective & reward shaping,
  - memory RAG retrieval + reuse,
  - explainability trace model.

## 4. Implementation

* 4.1 Tech stack (Python 3.11, FastAPI, SQLAlchemy async, Redis Streams,
  ChromaDB, PyTorch PPO, Terraform).
* 4.2 Deployment (single binary, Docker Compose, Kubernetes).
* 4.3 Determinism & the mock boundary (why reproducible eval matters).

## 5. Evaluation

* 5.1 Experimental setup: six incident classes (high CPU, DB capacity,
  storage full, high memory, high latency, cost anomaly), deterministic mock
  harness.
* 5.2 Metrics:
  - **TSR** (Task Success Rate),
  - **SFR** (Security Finding Rate),
  - **Cost Savings** (relative monthly-cost reduction),
  - **MTTR** (Mean Time To Remediation).
* 5.3 Results (baseline table).
* 5.4 **Five ablation studies** (isolate each vector):

| Ablation | Expectation |
|----------|-------------|
| `ablate_closed_loop` | TSR drops (unresolved fixes not caught/rolled back) |
| `ablate_adversarial` | SFR drops (runtime exploits missed) |
| `ablate_rl_finops` | Cost savings drop to the greedy heuristic |
| `ablate_memory` | no cross-deployment learning (reuse of proven fixes) |
| `ablate_harmonizer` | provider selection degrades (cost/latency penalty) |

* 5.5 Qualitative study: sample explanations & decision traces.
* 5.6 Threats to validity (mock fidelity, LLM nondeterminism, cost-model
  accuracy).

## 6. Discussion

* LLM hallucination mitigation via typed IR.
* Safety of autonomous rollback; human-in-the-loop hooks.
* Scalability of the event-driven design.
* Ethical/security considerations of an autonomous red-teaming agent.

## 7. Conclusion & Future Work

* Recap contributions; open problems: multi-step incident resolution, causal
  verification, cross-tenant memory privacy, larger RL action spaces.

## Appendix

* Reproduction instructions (Docker/K8s), scenario definitions, full ablation
  tables.

---

## Paper-writing checklist

- [ ] Add architecture/workflow figures (Mermaid or TikZ).
- [ ] Replace mock cost/latency tables with cited public pricing where possible.
- [ ] Run ablations N≥5 times and report mean ± std (currently deterministic
      single runs).
- [ ] Add an LLM-in-the-loop experiment with DeepSeek V4 vs GPT-4o for the
      DevOps/Review agents.
- [ ] Report token/latency costs per run for a real cost analysis.
