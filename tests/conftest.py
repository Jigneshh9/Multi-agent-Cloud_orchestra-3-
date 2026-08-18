"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from cloud_orchestra.core.config import FeatureFlags, Settings


def make_settings(**overrides: object) -> Settings:
    base: dict[str, object] = {
        "env": "test",
        "llm_provider": "mock",
        "memory_provider": "memory",
        "sandbox_provider": "mock",
        "github_repo_owner": "",
        "github_repo_name": "",
        "database_url": "sqlite+aiosqlite:///:memory:",
    }
    base.update(overrides)
    return Settings(**base)  # type: ignore[arg-type]


@pytest.fixture
def settings() -> Settings:
    return make_settings()


@pytest.fixture
def features() -> FeatureFlags:
    return FeatureFlags()


@pytest.fixture
async def runtime():
    from cloud_orchestra.runtime import Runtime

    rt = Runtime(make_settings(), persistent=False)
    yield rt
    await rt.close()


@pytest.fixture
async def repository(settings):
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from cloud_orchestra.db.repository import Repository
    from cloud_orchestra.db.session import create_engine, init_db

    engine = create_engine("sqlite+aiosqlite:///:memory:")
    await init_db(engine)
    sm = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with sm() as session:
        yield Repository(session)
    await engine.dispose()


@pytest.fixture
def agents(settings):
    from cloud_orchestra.agents.registry import build_agents
    from cloud_orchestra.db.repository import InMemoryRepository
    from cloud_orchestra.runtime import Runtime

    rt = Runtime(settings, persistent=False)
    ctx = rt.make_context(InMemoryRepository())
    return build_agents(ctx)
