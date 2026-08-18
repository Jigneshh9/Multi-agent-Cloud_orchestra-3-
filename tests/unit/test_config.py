"""Unit tests for configuration and feature flags."""

from __future__ import annotations

import pytest

from cloud_orchestra.core.config import FeatureFlags, Settings


def test_feature_flags_default_all_true() -> None:
    flags = FeatureFlags()
    assert flags.verifier
    assert flags.rollback
    assert flags.red_team
    assert flags.fin_ops_rl
    assert flags.memory
    assert flags.cloud_harmonizer
    assert flags.explainer


def test_disable_single_flag() -> None:
    flags = FeatureFlags().disable("red_team")
    assert not flags.red_team
    assert flags.verifier
    assert flags.memory


def test_disable_unknown_flag_raises() -> None:
    with pytest.raises(ValueError):
        FeatureFlags().disable("does_not_exist")


def test_settings_with_features() -> None:
    settings = Settings().with_features(FeatureFlags(verifier=False))
    assert not settings.features.verifier
    assert settings.features.red_team


def test_settings_defaults() -> None:
    settings = Settings()
    assert settings.env == "development"
    assert settings.database_url.startswith("sqlite")
