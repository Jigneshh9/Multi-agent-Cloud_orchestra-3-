"""Tests for logging and tracing helpers."""

from __future__ import annotations

import logging

from cloud_orchestra.core.logging import configure_logging, get_logger
from cloud_orchestra.core.tracing import Tracer


def test_configure_logging_sets_level() -> None:
    configure_logging("DEBUG")
    assert logging.getLogger().level == logging.DEBUG
    configure_logging("INFO")


def test_get_logger_returns_logger() -> None:
    logger = get_logger("cloud_orchestra.test")
    assert logger.name == "cloud_orchestra.test"


def test_tracer_records_and_filters() -> None:
    from uuid import uuid4

    tracer = Tracer()
    run_id = uuid4()
    tracer.record(agent="devops", step="plan", run_id=run_id)
    tracer.record(agent="review", step="scan", run_id=run_id)
    assert len(tracer.all()) == 2
    assert len(tracer.for_run(run_id)) == 2
    assert tracer.for_run(uuid4()) == []
