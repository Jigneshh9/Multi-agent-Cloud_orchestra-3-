# Cloud-Orchestra — Development Guide

## Repository layout

```
src/cloud_orchestra/
  core/        config, errors, events, bus, llm, tracing, metrics, logging
  schemas/     Pydantic domain contracts
  db/          SQLAlchemy models, session, repository
  providers/   cloud, github, sandbox, terraform adapters
  agents/      the ten agents + registry
  orchestrator/ saga workflow
  rl/          FinOpsEnv, PPO, policies
  memory/      vector store (in-memory + Chroma)
  eval/        metrics, scenarios, harness, ablations
  api/         FastAPI control plane
  runtime.py   wiring (services -> agents -> orchestrator)
  main.py      CLI entrypoint
tests/
  unit/        pure functions and adapters
  integration/ workflow + evaluation end-to-end
docs/          architecture, api, deployment, development, paper outline
k8s/           Kubernetes manifests
```

## Quality gates

```bash
make test          # pytest (82%+ coverage enforced)
make lint          # ruff
make typecheck     # mypy --strict
make test-cov      # coverage report with 80% fail-under
```

All three must pass. CI-friendly ordering:

```bash
ruff check src tests && mypy src && pytest --cov=cloud_orchestra --cov-fail-under=80
```

## Adding an agent

1. Create `src/cloud_orchestra/agents/my_agent.py` with a class extending
   `BaseAgent` (set `name`).
2. Inject dependencies via `AgentContext`; record decisions with
   `self.timed(...)` / `self.trace(...)`.
3. Register it in `agents/registry.py` (dataclass + `build_agents`).
4. Wire the step into `orchestrator/workflow.py` behind a `FEATURE_*` flag.
5. Add unit tests (mock every external dependency) + an integration scenario.

## Adding a novelty vector

1. Add a `FeatureFlags` field in `core/config.py`.
2. Gate the behaviour in the orchestrator.
3. Add an ablation entry in `eval/ablations.py`.
4. Add a KPI assertion in `tests/integration/test_eval.py`.

## Determinism & testability

Every external boundary has a deterministic mock:

| Boundary | Real | Mock |
|----------|------|------|
| LLM | `OpenAICompatibleLLMClient` | `MockLLMClient` |
| Event bus | `RedisStreamBus` | `InMemoryEventBus` |
| Memory | `ChromaMemoryStore` | `InMemoryMemoryStore` |
| Sandbox | `DockerSandboxProvider` | `MockSandboxProvider` |
| GitHub | `RESTGitHubClient` | `MockGitHubClient` |
| Terraform | `LocalTerraformProvider` | `DryRunTerraformProvider` |
| Cloud | SDK clients | `MockCloudClient` |

The whole pipeline therefore runs offline and deterministically — a requirement
for reproducible research evaluation.

## Conventions

* Python 3.11+, `from __future__ import annotations`.
* Type-hint everything; `mypy --strict` clean.
* Enums are `enum.StrEnum`.
* Async where I/O is involved; pure functions stay sync.
* `zip(..., strict=True)`.
* No wildcard imports; `ruff` clean.
