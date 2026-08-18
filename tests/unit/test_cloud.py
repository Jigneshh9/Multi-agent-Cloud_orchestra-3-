"""Unit tests for the cloud cost/latency models and mock client."""

from __future__ import annotations

from cloud_orchestra.providers.cloud import (
    MockCloudClient,
    capacity_scale,
    estimate_latency_ms,
    estimate_monthly_cost,
    storage_added_gb,
    tier_from_name,
)
from cloud_orchestra.schemas import (
    Alert,
    AlertSeverity,
    AlertSource,
    CloudProvider,
    TerraformPlan,
    TerraformResource,
)


def test_tier_from_name() -> None:
    assert tier_from_name("t3.small") == "small"
    assert tier_from_name("t3.medium") == "medium"
    assert tier_from_name("t3.large") == "large"
    assert tier_from_name("t3.xlarge") == "xlarge"
    assert tier_from_name("n1-standard-4") == "large"
    assert tier_from_name("n1-standard-2") == "medium"


def test_estimate_monthly_cost_instances() -> None:
    plan = TerraformPlan(
        provider=CloudProvider.AWS,
        resources=[
            TerraformResource(
                resource_type="aws_instance",
                name="i",
                provider=CloudProvider.AWS,
                attributes={"instance_type": "t3.medium", "count": 2},
            )
        ],
    )
    # medium = 0.05/hr * 730 * 2 = 73.0
    assert estimate_monthly_cost(plan) == 73.0


def test_estimate_monthly_cost_gcp_multiplier() -> None:
    plan = TerraformPlan(
        provider=CloudProvider.GCP,
        resources=[
            TerraformResource(
                resource_type="google_compute_instance",
                name="i",
                provider=CloudProvider.GCP,
                attributes={"machine_type": "n1-standard-1", "count": 1},
            )
        ],
    )
    # small 0.02 * 730 * 1 * 0.9 = 13.14
    assert estimate_monthly_cost(plan) == round(0.02 * 730 * 0.9, 2)


def test_capacity_scale() -> None:
    plan = TerraformPlan(
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
    assert capacity_scale(plan) == 3 * 2  # 3 x medium(factor 2)


def test_storage_added_gb() -> None:
    plan = TerraformPlan(
        provider=CloudProvider.AWS,
        resources=[
            TerraformResource(
                resource_type="aws_ebs_volume",
                name="vol",
                provider=CloudProvider.AWS,
                attributes={"size_gb": 100},
            )
        ],
    )
    assert storage_added_gb(plan) == 100.0


def test_estimate_latency_ms() -> None:
    assert estimate_latency_ms(CloudProvider.AWS, "us-east-1") == 8
    assert estimate_latency_ms(CloudProvider.GCP, "eu-west-1") == 24


async def test_mock_cloud_apply_effect_high_cpu() -> None:
    cloud = MockCloudClient()
    alert = Alert(
        source=AlertSource.AWS_CLOUDWATCH,
        name="High CPU",
        severity=AlertSeverity.HIGH,
        resource_type="ec2_instance",
        resource_id="i-1",
        threshold=80.0,
        current_value=90.0,
    )
    plan = TerraformPlan(
        provider=CloudProvider.AWS,
        resources=[
            TerraformResource(
                resource_type="aws_autoscaling_group",
                name="asg",
                provider=CloudProvider.AWS,
                attributes={"instance_type": "t3.small", "desired_capacity": 2},
            )
        ],
    )
    after = await cloud.apply_effect(alert, plan)
    assert after == 45.0  # 90 / 2


async def test_mock_cloud_query_metric() -> None:
    cloud = MockCloudClient()
    cloud.set_metric("i-1", "CPUUtilization", 55.0)
    assert await cloud.query_metric("i-1", "CPUUtilization") == 55.0
    assert await cloud.query_metric("i-1", "Memory") is None
