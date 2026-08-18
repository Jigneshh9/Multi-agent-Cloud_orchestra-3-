"""Unit tests for the FinOps RL environment and policies."""

from __future__ import annotations

from cloud_orchestra.rl.env import (
    TIER_FACTORS,
    FinOpsEnv,
    minimal_tier_for_demand,
    optimal_config,
)
from cloud_orchestra.rl.policy import FinOpsPolicy, GreedyPolicy


def test_minimal_tier_for_demand() -> None:
    assert minimal_tier_for_demand(1) == 0
    assert minimal_tier_for_demand(2) == 1
    assert minimal_tier_for_demand(4) == 2
    assert minimal_tier_for_demand(5) == 3
    assert minimal_tier_for_demand(8) == 3


def test_optimal_config() -> None:
    # demand 2: small x2 (0.04) beats medium x1 (0.05)
    assert optimal_config(2) == (0, 2)
    # demand 4: large x1 (0.10) vs medium x2 (0.10) vs small x4 (0.08)
    assert optimal_config(4) == (0, 4)


def test_env_reset_and_step() -> None:
    env = FinOpsEnv(demand=2, horizon=8, start_tier=3)
    state = env.reset()
    assert len(state) == 3
    assert env.tier == 3

    result = env.step(0)  # scale down
    assert env.tier == 2
    assert result.info["tier"] == 2
    assert result.state == env._state()


def test_env_terminal_reward_meets_demand() -> None:
    env = FinOpsEnv(demand=1, horizon=1, start_tier=3)
    env.reset()
    result = env.step(0)  # -> large (factor 4 >= 1)
    assert result.done
    assert result.reward > 0  # terminal bonus for meeting demand


def test_greedy_policy_select_config() -> None:
    policy = GreedyPolicy()
    assert policy.select_config(demand=2, current_tier=3, current_count=3) == (2, 3)


def test_greedy_policy_act() -> None:
    policy = GreedyPolicy()
    action, _ = policy.act([0.5, 1.0, 0.0])  # tier 3
    assert action == 0  # scale down


def test_finops_policy_falls_back_to_optimal() -> None:
    # Without torch installed, FinOpsPolicy falls back to the analytic optimum.
    policy = FinOpsPolicy()
    assert policy.select_config(demand=2, current_tier=3, current_count=3) == (0, 2)


def test_tier_factors_ordering() -> None:
    assert TIER_FACTORS == [1, 2, 4, 8]
