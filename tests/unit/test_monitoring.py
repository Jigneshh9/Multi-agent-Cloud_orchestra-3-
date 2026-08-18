"""Unit tests for the Monitoring Agent and alert parsing."""

from __future__ import annotations

from cloud_orchestra.agents.monitoring import parse_alert, parse_cloudwatch, parse_gcp
from cloud_orchestra.schemas import AlertSource, CloudProvider


def test_parse_cloudwatch() -> None:
    payload = {
        "AlarmName": "CPUUtilizationTooHigh",
        "NewStateValue": "ALARM",
        "Region": "us-east-1",
        "Trigger": {
            "MetricName": "CPUUtilization",
            "Threshold": 80.0,
            "Dimensions": [{"name": "InstanceId", "value": "i-1234"}],
        },
    }
    alert = parse_cloudwatch(payload)
    assert alert.source == AlertSource.AWS_CLOUDWATCH
    assert alert.provider == CloudProvider.AWS
    assert alert.metric_name == "CPUUtilization"
    assert alert.threshold == 80.0
    assert alert.resource_id == "i-1234"


def test_parse_gcp() -> None:
    payload = {
        "incident": {
            "policy_name": "High CPU",
            "resource_name": "instance-1",
            "region": "us-central1",
            "metric": {"type": "compute.googleapis.com/instance/cpu/utilization"},
        }
    }
    alert = parse_gcp(payload)
    assert alert.source == AlertSource.GCP_MONITORING
    assert alert.provider == CloudProvider.GCP


def test_parse_alert_dispatch() -> None:
    alert = parse_alert(AlertSource.AWS_CLOUDWATCH, {"AlarmName": "X", "NewStateValue": "ALARM"})
    assert alert.name == "X"


async def test_ingest_publishes_event(agents) -> None:
    from cloud_orchestra.schemas import Alert, AlertSeverity, AlertSource

    alert = Alert(
        source=AlertSource.AWS_CLOUDWATCH,
        name="test",
        severity=AlertSeverity.HIGH,
        resource_type="ec2_instance",
        resource_id="i-1",
    )
    result = await agents.monitoring.ingest(alert)
    assert result.name == "test"
