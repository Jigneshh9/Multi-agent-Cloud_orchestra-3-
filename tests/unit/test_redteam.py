"""Unit tests for the Red Team attack modules and attack surface."""

from __future__ import annotations

from cloud_orchestra.agents.redteam import run_attack_modules
from cloud_orchestra.providers.sandbox import derive_attack_surface
from cloud_orchestra.schemas import CloudProvider, TerraformPlan, TerraformResource


def test_runtime_default_credentials_finding() -> None:
    surface = {
        "public_databases": [],
        "open_ports": [],
        "unencrypted_storage": [],
        "overly_permissive_iam": [],
        "runtime_flags": [{"resource": "app_db", "flag": "default_credentials"}],
    }
    findings = run_attack_modules(surface)
    assert any(f.vulnerability_type == "default_credentials" for f in findings)
    assert findings[0].cvss_score == 9.8


def test_runtime_unpatched_os_finding() -> None:
    surface = {
        "runtime_flags": [{"resource": "web", "flag": "unpatched_os"}],
        "public_databases": [],
        "open_ports": [],
        "unencrypted_storage": [],
        "overly_permissive_iam": [],
    }
    findings = run_attack_modules(surface)
    assert any(f.vulnerability_type == "unpatched_os" for f in findings)


def test_open_port_scan_finding() -> None:
    surface = {
        "runtime_flags": [],
        "public_databases": [],
        "open_ports": [{"resource": "sg", "port": 22}],
        "unencrypted_storage": [],
        "overly_permissive_iam": [],
    }
    findings = run_attack_modules(surface)
    assert any(f.attack_module == "open_port_scan" for f in findings)


def test_derive_attack_surface_seeded_runtime_flag() -> None:
    plan = TerraformPlan(
        provider=CloudProvider.AWS,
        resources=[
            TerraformResource(
                resource_type="aws_db_instance",
                name="app_db",
                provider=CloudProvider.AWS,
                attributes={"publicly_accessible": True, "password_rotation_enabled": False},
            )
        ],
    )
    surface = derive_attack_surface(plan)
    assert "app_db" in surface["public_databases"]
    assert any(flag["flag"] == "default_credentials" for flag in surface["runtime_flags"])


def test_derive_attack_surface_no_runtime_flag_when_patched() -> None:
    plan = TerraformPlan(
        provider=CloudProvider.AWS,
        resources=[
            TerraformResource(
                resource_type="aws_instance",
                name="web",
                provider=CloudProvider.AWS,
                attributes={"patch_management": True},
            )
        ],
    )
    surface = derive_attack_surface(plan)
    assert surface["runtime_flags"] == []
