"""Unit tests for the DevOps Agent's plan generation and memory reuse."""

from __future__ import annotations

from cloud_orchestra.agents.devops import RuleBasedPlanGenerator
from cloud_orchestra.providers.cloud import estimate_monthly_cost
from cloud_orchestra.schemas import (
    Alert,
    AlertSeverity,
    AlertSource,
    CloudProvider,
    MemoryEntry,
    TerraformPlan,
    TerraformResource,
)


def _alert() -> Alert:
    return Alert(
        source=AlertSource.AWS_CLOUDWATCH,
        name="High CPU on web tier",
        severity=AlertSeverity.HIGH,
        resource_type="ec2_instance",
        resource_id="i-1",
        threshold=80.0,
        current_value=90.0,
    )


def test_generate_naive_plan() -> None:
    plan = RuleBasedPlanGenerator().generate(_alert(), CloudProvider.AWS, [])
    assert plan.resources
    assert plan.estimated_monthly_cost_usd > 0


def test_generate_reuses_cheaper_resolved_memory() -> None:
    alert = _alert()
    generator = RuleBasedPlanGenerator()
    naive = generator.generate(alert, CloudProvider.AWS, [])

    cheaper = TerraformPlan(
        provider=CloudProvider.AWS,
        resources=[
            TerraformResource(
                resource_type="aws_autoscaling_group",
                name="web_asg",
                provider=CloudProvider.AWS,
                attributes={"instance_type": "t3.small", "desired_capacity": 2},
            )
        ],
    )
    cheaper.estimated_monthly_cost_usd = estimate_monthly_cost(cheaper)
    assert cheaper.estimated_monthly_cost_usd < naive.estimated_monthly_cost_usd

    memory = MemoryEntry(
        problem_class=alert.problem_class,
        provider=CloudProvider.AWS,
        resource_type=alert.resource_type,
        summary="cheaper fix",
        terraform_plan=cheaper,
        resolved=True,
    )
    reused = generator.generate(alert, CloudProvider.AWS, [memory])
    assert reused.estimated_monthly_cost_usd == cheaper.estimated_monthly_cost_usd


def test_generate_ignores_unresolved_memory() -> None:
    alert = _alert()
    generator = RuleBasedPlanGenerator()
    naive = generator.generate(alert, CloudProvider.AWS, [])

    bad = TerraformPlan(
        provider=CloudProvider.AWS,
        resources=[
            TerraformResource(
                resource_type="aws_instance",
                name="i",
                provider=CloudProvider.AWS,
                attributes={"instance_type": "t3.small"},
            )
        ],
    )
    bad.estimated_monthly_cost_usd = 1.0
    memory = MemoryEntry(
        problem_class=alert.problem_class,
        provider=CloudProvider.AWS,
        resource_type=alert.resource_type,
        summary="failed",
        terraform_plan=bad,
        resolved=False,
    )
    result = generator.generate(alert, CloudProvider.AWS, [memory])
    assert result.estimated_monthly_cost_usd == naive.estimated_monthly_cost_usd
