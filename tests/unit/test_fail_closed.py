"""Tests for the fail-closed state machine (Improvements.docx Phase 2)."""

from __future__ import annotations

from cloud_orchestra.agents.devops import harden_plan
from cloud_orchestra.agents.registry import build_agents
from cloud_orchestra.db.repository import InMemoryRepository
from cloud_orchestra.orchestrator.workflow import Workflow
from cloud_orchestra.runtime import Runtime
from cloud_orchestra.schemas import (
    Alert,
    AlertSeverity,
    AlertSource,
    CloudProvider,
    FindingSeverity,
    RunStatus,
    SecurityFinding,
    TerraformPlan,
    TerraformResource,
)


def test_run_status_has_expanded_saga_states() -> None:
    for state in (
        RunStatus.RECEIVED,
        RunStatus.DIAGNOSED,
        RunStatus.PLANNED,
        RunStatus.GATED,
        RunStatus.SANDBOXED,
        RunStatus.PR_READY,
        RunStatus.APPROVED,
        RunStatus.DEPLOYED,
        RunStatus.VERIFIED,
        RunStatus.REJECTED,
        RunStatus.ROLLED_BACK,
    ):
        assert state in RunStatus
    # Backwards-compatible states remain.
    assert RunStatus.PENDING in RunStatus
    assert RunStatus.SUCCEEDED in RunStatus
    assert RunStatus.FAILED in RunStatus


def test_harden_plan_closes_security_findings() -> None:
    plan = TerraformPlan(
        provider=CloudProvider.AWS,
        resources=[
            TerraformResource(
                resource_type="aws_db_instance",
                name="app_db",
                provider=CloudProvider.AWS,
                attributes={"publicly_accessible": True, "password_rotation_enabled": False},
            ),
            TerraformResource(
                resource_type="aws_instance",
                name="web",
                provider=CloudProvider.AWS,
                attributes={"instance_type": "t3.medium"},
            ),
        ],
    )
    findings = [
        SecurityFinding(
            vulnerability_type="publicly_accessible_database",
            severity=FindingSeverity.HIGH,
            target="app_db",
            description="public",
        ),
        SecurityFinding(
            vulnerability_type="default_credentials",
            severity=FindingSeverity.CRITICAL,
            target="app_db",
            description="defaults",
        ),
        SecurityFinding(
            vulnerability_type="unpatched_os",
            severity=FindingSeverity.HIGH,
            target="web",
            description="unpatched",
        ),
    ]
    hardened = harden_plan(plan, findings)
    db = hardened.resources[0].attributes
    web = hardened.resources[1].attributes
    assert db["publicly_accessible"] is False
    assert db["password_rotation_enabled"] is True
    assert web["patch_management"] is True


async def test_workflow_rejects_unfixable_critical_finding(settings) -> None:
    runtime = Runtime(settings, persistent=False)
    ctx = runtime.make_context(InMemoryRepository())
    agents = build_agents(ctx)

    async def unfixable(_plan: TerraformPlan) -> list[SecurityFinding]:
        return [
            SecurityFinding(
                attack_module="backdoor",
                vulnerability_type="unfixable_backdoor",
                severity=FindingSeverity.CRITICAL,
                target="web",
                description="cannot be auto-remediated",
                found_by_red_team=True,
            )
        ]

    agents.red_team.findings = unfixable  # type: ignore[method-assign]

    workflow = Workflow(ctx, agents)
    alert = Alert(
        source=AlertSource.AWS_CLOUDWATCH,
        name="High CPU on web tier",
        severity=AlertSeverity.HIGH,
        resource_type="ec2_instance",
        resource_id="i-1",
        threshold=80.0,
        current_value=90.0,
    )
    result = await workflow.run(alert)
    assert result.run.status == RunStatus.REJECTED
    assert result.run.resolved is False
    await runtime.close()
