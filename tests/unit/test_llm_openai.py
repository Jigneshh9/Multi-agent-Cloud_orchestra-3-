"""Tests for the OpenAI-compatible LLM client (mocked transport)."""

from __future__ import annotations

import httpx

from cloud_orchestra.core.llm import OpenAICompatibleLLMClient
from cloud_orchestra.schemas import TerraformPlan


class _FakeResponse:
    def __init__(self, data: dict) -> None:
        self._data = data
        self.text = str(data)

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._data


class _FakeClient:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs

    async def __aenter__(self) -> _FakeClient:
        return self

    async def __aexit__(self, *args) -> None:
        return None

    async def post(self, url: str, headers: dict, json: dict) -> _FakeResponse:
        self.last_body = json
        return _FakeResponse(
            {
                "choices": [{"message": {"content": '{"provider": "aws", "resources": []}'}}],
                "model": "deepseek-v4",
                "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            }
        )


async def test_complete(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "AsyncClient", _FakeClient)
    client = OpenAICompatibleLLMClient("https://api.example.com/v1", "key", "deepseek-v4")
    resp = await client.complete([{"role": "user", "content": "hi"}], json_mode=True)
    assert resp.content.startswith('{"provider"')
    assert resp.model == "deepseek-v4"
    assert resp.input_tokens == 10


async def test_complete_structured(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "AsyncClient", _FakeClient)
    client = OpenAICompatibleLLMClient("https://api.example.com/v1", "key", "deepseek-v4")
    plan = await client.complete_structured([{"role": "user", "content": "x"}], TerraformPlan)
    assert plan.provider.value == "aws"
