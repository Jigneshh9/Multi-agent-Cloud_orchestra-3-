"""Tests for the GitHub mock client and PR flow."""

from __future__ import annotations

from cloud_orchestra.providers.github import MockGitHubClient


async def test_mock_create_pr() -> None:
    client = MockGitHubClient()
    pr = await client.create_pull_request(
        repo_owner="org",
        repo_name="repo",
        branch="feature/x",
        title="fix",
        body="body",
        files={"main.tf": 'provider "aws" {}'},
    )
    assert pr.status == "simulated"
    assert pr.pr_number == 1
    assert pr.pr_url.endswith("/pull/1")


async def test_mock_add_comment() -> None:
    client = MockGitHubClient()
    await client.add_comment(1, "hello")
    assert client.comments == [(1, "hello")]


async def test_mock_pr_counter_increments() -> None:
    client = MockGitHubClient()
    first = await client.create_pull_request(
        repo_owner="o", repo_name="r", branch="b1", title="t", body="b", files={}
    )
    second = await client.create_pull_request(
        repo_owner="o", repo_name="r", branch="b2", title="t", body="b", files={}
    )
    assert first.pr_number == 1
    assert second.pr_number == 2
