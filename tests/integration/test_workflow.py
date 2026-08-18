"""End-to-end workflow integration tests."""

from __future__ import annotations

from cloud_orchestra.eval.scenarios import build_scenarios
from cloud_orchestra.schemas import RunStatus

SCENARIOS = {s.id: s for s in build_scenarios()}


async def test_high_cpu_resolves_and_detects_findings(runtime) -> None:
    result = await runtime.run_alert(SCENARIOS["high_cpu"].alert)
    assert result.run.resolved is True
    assert result.run.status == RunStatus.SUCCEEDED
    assert len(result.findings) >= 2
    assert result.run.cost_after < result.run.cost_before


async def test_db_capacity_resolves(runtime) -> None:
    result = await runtime.run_alert(SCENARIOS["db_capacity"].alert)
    assert result.run.resolved is True
    assert any(f.found_by_red_team for f in result.findings)


async def test_storage_full_resolves(runtime) -> None:
    result = await runtime.run_alert(SCENARIOS["storage_full"].alert)
    assert result.run.resolved is True
    assert len(result.findings) >= 1


async def test_high_memory_clean_plan(runtime) -> None:
    result = await runtime.run_alert(SCENARIOS["high_memory"].alert)
    assert result.run.resolved is True
    assert result.findings == []


async def test_high_latency_resolves(runtime) -> None:
    result = await runtime.run_alert(SCENARIOS["high_latency"].alert)
    assert result.run.resolved is True


async def test_cost_anomaly_resolves_under_budget(runtime) -> None:
    result = await runtime.run_alert(SCENARIOS["cost_anomaly"].alert)
    assert result.run.resolved is True


async def test_provider_selected_and_plan_rendered(runtime) -> None:
    result = await runtime.run_alert(SCENARIOS["high_cpu"].alert)
    assert result.run.provider is not None
    assert result.run.terraform_plan is not None
    assert result.run.terraform_code.startswith('provider "')
