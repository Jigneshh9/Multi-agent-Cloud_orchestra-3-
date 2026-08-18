"""Unit tests for the Review Agent's static rules."""

from __future__ import annotations

from cloud_orchestra.agents.review import merge_review, static_scan
from cloud_orchestra.schemas import (
    CloudProvider,
    FindingSeverity,
    ReviewResult,
    ReviewVerdict,
    SecurityFinding,
    TerraformPlan,
    TerraformResource,
)


def _plan(attrs: dict) -> TerraformPlan:
    return TerraformPlan(
        provider=CloudProvider.AWS,
        resources=[
            TerraformResource(
                resource_type="aws_db_instance",
                name="app_db",
                provider=CloudProvider.AWS,
                attributes=attrs,
            )
        ],
    )


def test_static_scan_public_database() -> None:
    findings = static_scan(_plan({"publicly_accessible": True}))
    assert any(f.vulnerability_type == "publicly_accessible_database" for f in findings)


def test_static_scan_open_ingress() -> None:
    plan = TerraformPlan(
        provider=CloudProvider.AWS,
        resources=[
            TerraformResource(
                resource_type="aws_security_group",
                name="sg",
                provider=CloudProvider.AWS,
                attributes={"ingress": [{"from_port": 22, "cidr_blocks": ["0.0.0.0/0"]}]},
            )
        ],
    )
    findings = static_scan(plan)
    assert any(f.vulnerability_type == "open_ingress" for f in findings)


def test_static_scan_clean_plan_has_no_findings() -> None:
    findings = static_scan(_plan({"publicly_accessible": False, "storage_encrypted": True}))
    assert findings == []


def test_merge_review_blocks_on_critical() -> None:
    static = ReviewResult(verdict=ReviewVerdict.APPROVED, findings=[])
    dynamic = [
        SecurityFinding(
            attack_module="default_credential_check",
            vulnerability_type="default_credentials",
            severity=FindingSeverity.CRITICAL,
            target="app_db",
            description="default creds",
            found_by_red_team=True,
        )
    ]
    merged = merge_review(static, dynamic)
    assert merged.verdict == ReviewVerdict.CHANGES_REQUESTED
    assert not merged.security_acceptable


def test_merge_review_approves_clean() -> None:
    static = ReviewResult(verdict=ReviewVerdict.APPROVED, findings=[])
    merged = merge_review(static, [])
    assert merged.verdict == ReviewVerdict.APPROVED


async def test_review_agent_budget_check(agents) -> None:
    plan = TerraformPlan(
        provider=CloudProvider.AWS,
        resources=[
            TerraformResource(
                resource_type="aws_instance",
                name="i",
                provider=CloudProvider.AWS,
                attributes={"instance_type": "t3.large", "count": 4},
            )
        ],
    )
    plan.estimated_monthly_cost_usd = 1000.0
    result = await agents.review.review(plan, budget_usd=100.0)
    assert not result.cost_acceptable
    assert any(c.category.value == "cost" for c in result.comments)
