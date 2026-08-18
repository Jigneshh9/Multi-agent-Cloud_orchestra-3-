"""Unit tests for the Terraform renderer and dry-run provider."""

from __future__ import annotations

from cloud_orchestra.providers.terraform import DryRunTerraformProvider, render_hcl
from cloud_orchestra.schemas import CloudProvider, TerraformPlan, TerraformResource


def test_render_hcl_resource_and_attribute() -> None:
    plan = TerraformPlan(
        provider=CloudProvider.AWS,
        provider_config={"region": "us-east-1"},
        resources=[
            TerraformResource(
                resource_type="aws_instance",
                name="web",
                provider=CloudProvider.AWS,
                attributes={"instance_type": "t3.small", "count": 2},
            )
        ],
    )
    hcl = render_hcl(plan)
    assert 'provider "aws" {' in hcl
    assert 'resource "aws_instance" "web" {' in hcl
    assert 'instance_type = "t3.small"' in hcl
    assert "count = 2" in hcl


def test_render_hcl_variables_and_outputs() -> None:
    plan = TerraformPlan(
        provider=CloudProvider.GCP,
        variables={"env": "prod"},
        outputs={"id": "${aws_instance.web.id}"},
        resources=[],
    )
    hcl = render_hcl(plan)
    assert 'variable "env" {' in hcl
    assert 'output "id" {' in hcl


def test_render_hcl_booleans_and_lists() -> None:
    plan = TerraformPlan(
        provider=CloudProvider.AWS,
        resources=[
            TerraformResource(
                resource_type="aws_security_group",
                name="sg",
                provider=CloudProvider.AWS,
                attributes={"ingress": [{"from_port": 80, "to_port": 80}]},
            )
        ],
    )
    hcl = render_hcl(plan)
    assert "ingress = [" in hcl
    assert "from_port = 80" in hcl


async def test_dry_run_apply_extracts_addresses() -> None:
    provider = DryRunTerraformProvider()
    result = await provider.apply('resource "aws_instance" "web" {}\nresource "aws_db_instance" "db" {}')
    assert result.succeeded
    assert result.applied_resources == ["aws_instance.web", "aws_db_instance.db"]


async def test_dry_run_validate() -> None:
    provider = DryRunTerraformProvider()
    assert await provider.validate('provider "aws" {}') is True


async def test_dry_run_destroy() -> None:
    provider = DryRunTerraformProvider()
    result = await provider.destroy('resource "aws_instance" "web" {}')
    assert result.succeeded
