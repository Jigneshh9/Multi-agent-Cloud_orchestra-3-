"""Unit tests for the vector memory store."""

from __future__ import annotations

from cloud_orchestra.memory.store import InMemoryMemoryStore
from cloud_orchestra.schemas import CloudProvider, MemoryEntry


async def test_add_and_search() -> None:
    store = InMemoryMemoryStore()
    entry = MemoryEntry(
        problem_class="high_cpu",
        provider=CloudProvider.AWS,
        resource_type="ec2_instance",
        summary="scaled up ec2 for high cpu",
    )
    await store.add(entry, "high cpu scaling on ec2 instance")
    hits = await store.search("high cpu ec2", top_k=3)
    assert len(hits) == 1
    assert hits[0][0].id == entry.id


async def test_search_empty_store() -> None:
    store = InMemoryMemoryStore()
    assert await store.search("anything") == []


async def test_search_relevance_order() -> None:
    store = InMemoryMemoryStore()
    cpu = MemoryEntry(problem_class="high_cpu", provider=CloudProvider.AWS,
                      resource_type="ec2_instance", summary="cpu")
    db = MemoryEntry(problem_class="db_capacity", provider=CloudProvider.AWS,
                     resource_type="rds_database", summary="database")
    await store.add(cpu, "high cpu utilization on ec2")
    await store.add(db, "database connection pool exhausted")
    hits = await store.search("cpu ec2", top_k=2)
    assert hits[0][0].id == cpu.id
    assert hits[1][0].id == db.id
