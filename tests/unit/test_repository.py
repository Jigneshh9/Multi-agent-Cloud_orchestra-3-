"""Integration-style tests for the SQLAlchemy repository (SQLite)."""

from __future__ import annotations

from uuid import uuid4

from cloud_orchestra.schemas import (
    Alert,
    AlertSeverity,
    AlertSource,
    CloudProvider,
    MemoryEntry,
    Run,
    RunStatus,
)


def _alert() -> Alert:
    return Alert(
        source=AlertSource.AWS_CLOUDWATCH,
        name="High CPU",
        severity=AlertSeverity.HIGH,
        resource_type="ec2_instance",
        resource_id="i-1",
        provider=CloudProvider.AWS,
        threshold=80.0,
        current_value=90.0,
    )


async def test_alert_roundtrip(repository) -> None:
    alert = _alert()
    await repository.save_alert(alert)
    got = await repository.get_alert(alert.id)
    assert got is not None
    assert got.name == "High CPU"
    assert got.provider == CloudProvider.AWS
    assert got.current_value == 90.0


async def test_run_roundtrip(repository) -> None:
    run = Run(alert_id=uuid4(), status=RunStatus.SUCCEEDED, resolved=True)
    await repository.save_run(run)
    got = await repository.get_run(run.id)
    assert got is not None
    assert got.status == RunStatus.SUCCEEDED
    assert got.resolved is True


async def test_run_update_persists(repository) -> None:
    run = Run(alert_id=uuid4(), status=RunStatus.PENDING)
    await repository.save_run(run)
    run.status = RunStatus.VERIFYING
    await repository.save_run(run)
    got = await repository.get_run(run.id)
    assert got is not None
    assert got.status == RunStatus.VERIFYING


async def test_list_runs_filters_by_status(repository) -> None:
    await repository.save_run(Run(alert_id=uuid4(), status=RunStatus.SUCCEEDED))
    await repository.save_run(Run(alert_id=uuid4(), status=RunStatus.FAILED))
    succeeded = await repository.list_runs(RunStatus.SUCCEEDED)
    assert len(succeeded) == 1


async def test_memory_roundtrip(repository) -> None:
    entry = MemoryEntry(
        problem_class="high_cpu",
        provider=CloudProvider.AWS,
        resource_type="ec2_instance",
        summary="scaled",
        resolved=True,
    )
    await repository.save_memory(entry)
    hits = await repository.query_memory("high_cpu")
    assert len(hits) == 1
    assert hits[0].problem_class == "high_cpu"
