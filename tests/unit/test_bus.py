"""Unit tests for the event bus."""

from __future__ import annotations

from cloud_orchestra.core.bus import InMemoryEventBus
from cloud_orchestra.core.events import Event, EventType


async def test_publish_fanout() -> None:
    bus = InMemoryEventBus()
    received: list[Event] = []

    async def handler(event: Event) -> None:
        received.append(event)

    await bus.subscribe(EventType.ALERT_RECEIVED, handler)
    await bus.publish(Event(type=EventType.ALERT_RECEIVED))
    assert len(received) == 1
    assert received[0].type == EventType.ALERT_RECEIVED


async def test_publish_no_subscribers() -> None:
    bus = InMemoryEventBus()
    await bus.publish(Event(type=EventType.RUN_STARTED))
    assert len(bus.published) == 1


async def test_multiple_handlers() -> None:
    bus = InMemoryEventBus()
    seen: list[str] = []

    async def one(event: Event) -> None:
        seen.append("one")

    async def two(event: Event) -> None:
        seen.append("two")

    await bus.subscribe(EventType.VERIFIED, one)
    await bus.subscribe(EventType.VERIFIED, two)
    await bus.publish(Event(type=EventType.VERIFIED))
    assert set(seen) == {"one", "two"}
