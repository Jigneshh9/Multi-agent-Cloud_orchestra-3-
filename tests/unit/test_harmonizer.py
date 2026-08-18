"""Unit tests for the Cloud Harmonizer."""

from __future__ import annotations

from cloud_orchestra.schemas import Alert, AlertSeverity, AlertSource, CloudProvider


def _alert(resource_type: str = "ec2_instance", region: str = "us-east-1") -> Alert:
    return Alert(
        source=AlertSource.AWS_CLOUDWATCH,
        name="alert",
        severity=AlertSeverity.HIGH,
        resource_type=resource_type,
        resource_id="x",
        region=region,
    )


async def test_choose_returns_a_provider(agents) -> None:
    rec = await agents.harmonizer.choose(_alert())
    assert rec.provider in CloudProvider
    assert 0.0 <= rec.score <= 1.0
    assert rec.reasoning


async def test_choose_ranked_alternatives(agents) -> None:
    rec = await agents.harmonizer.choose(_alert(resource_type="rds_database"))
    assert len(rec.alternatives) == 2  # two non-selected providers


async def test_choose_reproducible(agents) -> None:
    alert = _alert()
    first = await agents.harmonizer.choose(alert)
    second = await agents.harmonizer.choose(alert)
    assert first.provider == second.provider
