"""Tests for evaluation reporting utilities and session helpers."""

from __future__ import annotations

from cloud_orchestra.eval.ablations import ABLATIONS, compute_deltas, format_report
from cloud_orchestra.eval.metrics import EvalMetrics, metrics_table


def test_metrics_table_format() -> None:
    rows = [("baseline", EvalMetrics(tsr=1.0, sfr=2.0, cost_savings=0.3, mttr=1.5))]
    text = metrics_table(rows)
    assert "baseline" in text
    assert "TSR" in text


def test_format_report() -> None:
    report = format_report({"baseline": EvalMetrics(), "ablate_memory": EvalMetrics()})
    assert "baseline" in report
    assert "ablate_memory" in report


def test_compute_deltas() -> None:
    results = {
        "baseline": EvalMetrics(tsr=1.0, sfr=3.0),
        "ablate_adversarial": EvalMetrics(tsr=1.0, sfr=1.0),
    }
    deltas = compute_deltas(results)
    assert deltas["ablate_adversarial"]["sfr_delta"] == -2.0
    assert deltas["ablate_adversarial"]["tsr_delta"] == 0.0


def test_ablations_have_five_studies() -> None:
    assert len(ABLATIONS) == 6  # baseline + 5 ablations
    assert "ablate_closed_loop" in ABLATIONS
    assert "ablate_adversarial" in ABLATIONS


async def test_drop_db() -> None:
    from cloud_orchestra.db.session import create_engine, drop_db, init_db

    engine = create_engine("sqlite+aiosqlite:///:memory:")
    await init_db(engine)
    await drop_db(engine)
    await engine.dispose()
