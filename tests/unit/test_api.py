"""Tests for the FastAPI control plane."""

from __future__ import annotations

from fastapi.testclient import TestClient

from cloud_orchestra.api.app import create_app
from cloud_orchestra.core.config import Settings
from cloud_orchestra.schemas import Alert, AlertSeverity, AlertSource


def _settings(tmp_path) -> Settings:
    return Settings(
        env="test",
        llm_provider="mock",
        memory_provider="memory",
        sandbox_provider="mock",
        github_repo_owner="",
        github_repo_name="",
        database_url=f"sqlite+aiosqlite:///{tmp_path / 'test.db'}",
    )


def test_health(tmp_path) -> None:
    with TestClient(create_app(_settings(tmp_path))) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


def test_ingest_alert_no_run(tmp_path) -> None:
    with TestClient(create_app(_settings(tmp_path))) as client:
        resp = client.post(
            "/alerts/ingest",
            json={
                "source": "aws_cloudwatch",
                "payload": {"AlarmName": "HighCPU", "NewStateValue": "ALARM"},
                "trigger_run": False,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["alert"]["name"] == "HighCPU"


def test_ingest_alert_with_run(tmp_path) -> None:
    with TestClient(create_app(_settings(tmp_path))) as client:
        resp = client.post(
            "/alerts/ingest",
            json={
                "source": "aws_cloudwatch",
                "payload": {
                    "AlarmName": "High CPU on web tier",
                    "NewStateValue": "ALARM",
                    "Trigger": {"MetricName": "CPUUtilization", "Threshold": 80.0},
                },
                "trigger_run": True,
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "run_id" in body
        assert body["resolved"] is True


def test_create_run(tmp_path) -> None:
    alert = Alert(
        source=AlertSource.AWS_CLOUDWATCH,
        name="High CPU on web tier",
        severity=AlertSeverity.HIGH,
        resource_type="ec2_instance",
        resource_id="i-1",
        threshold=80.0,
        current_value=90.0,
    )
    with TestClient(create_app(_settings(tmp_path))) as client:
        resp = client.post("/runs", json=alert.model_dump(mode="json"))
        assert resp.status_code == 200
        assert resp.json()["resolved"] is True


def test_metrics_endpoint(tmp_path) -> None:
    with TestClient(create_app(_settings(tmp_path))) as client:
        resp = client.get("/metrics")
        assert resp.status_code == 200
        assert "cloud_orchestra" not in resp.text  # plaintext prometheus format
