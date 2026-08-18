# Cloud-Orchestra — API Reference

The control plane is a FastAPI application (`cloud_orchestra.api.app`). The
default base URL is `http://localhost:8000`.

## Endpoints

### `GET /health`
Liveness/readiness probe.

```json
{"status": "ok", "service": "cloud-orchestra"}
```

### `POST /alerts/ingest`
Ingest a raw cloud alert, normalise it, and optionally trigger a remediation
run.

Request body:

```json
{
  "source": "aws_cloudwatch | gcp_monitoring | azure_monitor",
  "payload": { "...": "raw alert payload" },
  "trigger_run": false
}
```

Response (when `trigger_run=false`):

```json
{
  "alert": {
    "id": "uuid",
    "source": "aws_cloudwatch",
    "name": "High CPU",
    "severity": "high",
    "resource_type": "ec2_instance",
    "resource_id": "i-1234",
    "metric_name": "CPUUtilization",
    "threshold": 80.0,
    "...": "..."
  }
}
```

Response (when `trigger_run=true`):

```json
{
  "alert": { "...": "..." },
  "run_id": "uuid",
  "status": "succeeded",
  "resolved": true
}
```

### `POST /runs`
Start a remediation run from a canonical `Alert` object.

Request body: a full `Alert` JSON (see `schemas.Alert`).

```json
{
  "source": "aws_cloudwatch",
  "name": "High CPU on web tier",
  "severity": "high",
  "resource_type": "ec2_instance",
  "resource_id": "i-1",
  "threshold": 80.0,
  "current_value": 90.0
}
```

Response:

```json
{
  "run_id": "uuid",
  "status": "succeeded",
  "resolved": true,
  "provider": "gcp"
}
```

### `GET /runs`
List all runs.

```json
[
  {
    "run_id": "uuid",
    "status": "succeeded",
    "provider": "gcp",
    "resolved": true
  }
]
```

### `GET /runs/{run_id}`
Get a single run's detail, including cost before/after and the generated
explanation.

```json
{
  "run_id": "uuid",
  "status": "succeeded",
  "provider": "gcp",
  "resolved": true,
  "cost_before": 98.55,
  "cost_after": 26.28,
  "explanation": "# Remediation Explanation ..."
}
```

### `GET /runs/{run_id}/explanation`
Return just the Markdown explanation.

### `GET /metrics`
Prometheus text exposition of the metrics registry.

## Alert normalisation rules

* **CloudWatch** (`aws_cloudwatch`): `AlarmName`, `NewStateValue`, `Trigger`
  (`MetricName`, `Threshold`, `Dimensions`), `Region`.
* **GCP** (`gcp_monitoring`): `incident` (`policy_name`, `resource_name`,
  `metric.type`, `region`).
* **Azure** (`azure_monitor`): `essentials` (`alertRule`, `severity`,
  `monitorCondition`, `alertTargetIDs`).

The `problem_class` is derived from the alert name: `high_cpu`, `high_memory`,
`storage_full`, `db_capacity`, `high_latency`, `cost_anomaly`, else `generic`.

## Configuration

See `.env.example` for every variable. Feature flags (`FEATURE_*`) enable/disable
the six novelty vectors and drive the ablation studies.
