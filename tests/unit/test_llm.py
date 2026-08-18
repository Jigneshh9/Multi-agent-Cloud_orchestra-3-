"""Unit tests for the LLM client abstraction."""

from __future__ import annotations

import pytest

from cloud_orchestra.core.errors import LLMError, LLMParseError
from cloud_orchestra.core.llm import MockLLMClient, build_llm_client
from cloud_orchestra.schemas import TerraformPlan


async def test_mock_complete_returns_content() -> None:
    client = MockLLMClient(default_content="hello")
    response = await client.complete([{"role": "user", "content": "hi"}])
    assert response.content == "hello"
    assert response.model == "mock-llm"


async def test_mock_structured_valid() -> None:
    client = MockLLMClient(default_content='{"provider": "aws", "resources": []}')
    plan = await client.complete_structured([{"role": "user", "content": "x"}], TerraformPlan)
    assert plan.provider.value == "aws"
    assert plan.resources == []


async def test_mock_structured_invalid_json_raises() -> None:
    client = MockLLMClient(default_content="not json at all")
    with pytest.raises(LLMParseError):
        await client.complete_structured([{"role": "user", "content": "x"}], TerraformPlan)


async def test_mock_structured_invalid_schema_raises() -> None:
    client = MockLLMClient(default_content='{"provider": "not-a-cloud"}')
    with pytest.raises(LLMParseError):
        await client.complete_structured([{"role": "user", "content": "x"}], TerraformPlan)


async def test_mock_dict_responder() -> None:
    client = MockLLMClient({"high_cpu": '{"provider": "gcp", "resources": []}'})
    plan = await client.complete_structured(
        [{"role": "user", "content": "high_cpu"}], TerraformPlan
    )
    assert plan.provider.value == "gcp"


def test_build_llm_client_unknown_provider() -> None:
    with pytest.raises(LLMError):
        build_llm_client("unknown", "", "", "model")


def test_build_llm_client_mock() -> None:
    client = build_llm_client("mock", "", "", "model")
    assert isinstance(client, MockLLMClient)
