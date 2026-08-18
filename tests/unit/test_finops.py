"""Unit tests for the FinOps agent's cost optimization."""

from __future__ import annotations

from cloud_orchestra.agents.finops import (
    capacity_demand,
    current_count,
    current_tier_index,
    rewrite_plan,
)
from cloud_orchestra.providers.cloud import estimate_monthly_cost
from cloud_orchestra.schemas import (
    Alert,
    AlertSeverity,
    AlertSource,
    CloudProvider,
    TerraformPlan,
    TerraformResource,
)


def _alert(problem: str, current: float, threshold: float) -> Alert:
    return Alert(
        source=AlertSource.AWS_CLOUDWATCH,
        name=f"alert-{problem}",
        severity=AlertSeverity.HIGH,
        resource_type="ec2_instance",
        resource_id="i-1",
        threshold=threshold,
        current_value=current,
    )


def _overprovisioned_plan() -> TerraformPlan:
    return TerraformPlan(
        provider=CloudProvider.AWS,
        resources=[
            TerraformResource(
                resource_type="aws_autoscaling_group",
                name="asg",
                provider=CloudProvider.AWS,
                attributes={"instance_type": "t3.medium", "desired_capacity": 3},
            )
        ],
    )


def test_capacity_demand() -> None:
    assert capacity_demand(_alert("high_cpu", 90.0, 80.0)) == 2
    assert capacity_demand(_alert("cost_anomaly", 2500.0, 1500.0)) == 1


def test_current_tier_and_count() -> None:
    plan = _overprovisioned_plan()
    assert current_tier_index(plan) == 1  # medium
    assert current_count(plan) == 3


def test_rewrite_plan_reduces_cost() -> None:
    plan = _overprovisioned_plan()
    before = estimate_monthly_cost(plan)
    rewritten = rewrite_plan(plan, demand=2, target_tier=0, target_count=2)
    after = estimate_monthly_cost(rewritten)
    assert after < before
    assert rewritten.resources[0].attributes["desired_capacity"] == 2
    assert rewritten.resources[0].attributes["instance_type"] == "t3.small"


def test_rewrite_plan_db_uses_demand_tier() -> None:
    plan = TerraformPlan(
        provider=CloudProvider.AWS,
        resources=[
            TerraformResource(
                resource_type="aws_db_instance",
                name="db",
                provider=CloudProvider.AWS,
                attributes={"instance_class": "t3.large"},
            )
        ],
    )
    rewritten = rewrite_plan(plan, demand=2, target_tier=0, target_count=2)
    # db tier should meet demand (medium factor 2), not the instance-optimal small
    assert rewritten.resources[0].attributes["instance_class"] == "t3.medium"
