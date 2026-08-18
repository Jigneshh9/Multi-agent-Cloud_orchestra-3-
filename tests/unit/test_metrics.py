"""Unit tests for the metrics registry."""

from __future__ import annotations

from cloud_orchestra.core.metrics import MetricsRegistry


def test_counter() -> None:
    registry = MetricsRegistry()
    registry.incr("alerts_total")
    registry.incr("alerts_total", 2)
    assert registry.counter("alerts_total") == 3


def test_counter_with_labels() -> None:
    registry = MetricsRegistry()
    registry.incr("runs", labels={"status": "ok"})
    assert registry.counter("runs", labels={"status": "ok"}) == 1
    assert registry.counter("runs") == 0


def test_gauge() -> None:
    registry = MetricsRegistry()
    registry.set_gauge("queue_depth", 42)
    assert registry.gauge("queue_depth") == 42


def test_histogram() -> None:
    registry = MetricsRegistry()
    registry.observe("latency_ms", 10.0)
    registry.observe("latency_ms", 20.0)
    assert registry.histogram_values("latency_ms") == [10.0, 20.0]


def test_prometheus_export() -> None:
    registry = MetricsRegistry()
    registry.incr("alerts_total")
    text = registry.to_prometheus_text()
    assert "# TYPE alerts_total counter" in text
    assert "alerts_total 1.0" in text
