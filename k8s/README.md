# Kubernetes manifests for Cloud-Orchestra.
#
# Layout:
#   00-namespace.yaml           — namespace
#   10-config.yaml              — ConfigMap + Secret (non-prod values)
#   20-stateful.yaml            — Postgres, Redis, Chroma
#   30-orchestrator.yaml        — API deployment + service + ingress
#   40-agents.yaml              — agent worker deployment + HPA
#
# Apply:  kubectl apply -f k8s/

