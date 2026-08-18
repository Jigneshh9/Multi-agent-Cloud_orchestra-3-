"""Evaluation harness and ablation study tests."""

from __future__ import annotations

from cloud_orchestra.core.config import FeatureFlags
from cloud_orchestra.eval.ablations import ABLATIONS
from cloud_orchestra.eval.harness import EvaluationHarness
from cloud_orchestra.eval.metrics import compute_metrics


async def test_harness_produces_metrics(settings) -> None:
    harness = EvaluationHarness(settings=settings)
    results, metrics = await harness.run()
    assert metrics.n == len(results) == 6
    assert 0.0 <= metrics.tsr <= 1.0
    assert metrics.tsr == 1.0  # all scenarios resolve


async def test_ablation_red_team_lowers_sfr(settings) -> None:
    harness = EvaluationHarness(settings=settings)
    _, baseline = await harness.run(FeatureFlags())
    _, no_red = await harness.run(FeatureFlags(red_team=False))
    assert no_red.sfr < baseline.sfr


async def test_ablation_no_rl_lowers_cost_savings(settings) -> None:
    harness = EvaluationHarness(settings=settings)
    _, baseline = await harness.run(FeatureFlags())
    _, no_rl = await harness.run(FeatureFlags(fin_ops_rl=False))
    assert no_rl.cost_savings < baseline.cost_savings


async def test_all_ablations_run(settings) -> None:
    harness = EvaluationHarness(settings=settings)
    results = await harness.run_all_ablations()
    assert "baseline" in results
    assert len(results) == len(ABLATIONS)


async def test_compute_metrics_empty() -> None:
    metrics = compute_metrics([])
    assert metrics.n == 0
    assert metrics.tsr == 0.0
