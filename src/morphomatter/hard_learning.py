"""Configurable Q-learning helpers for MorphoMatter Experiment 006.

This module preserves the Experiment 004 learner structure but allows recovery
under a frozen non-default NucleationConfig. It is simulation-only and carries
no physical interpretation.
"""
from __future__ import annotations

from dataclasses import replace
import random
from typing import Mapping, Sequence

from .core import Conditions, Phase
from .learning import (
    RECOVERY_ACTIONS,
    LearnedRecoveryResult,
    TabularRecoveryPolicy,
    TrainingCase,
    state_key,
)
from .nucleation import NucleationConfig, NucleationLattice
from .recovery import declared_control_effort


def config_with_seed(template: NucleationConfig, seed: int) -> NucleationConfig:
    """Clone a frozen recovery law while changing only its stochastic seed."""

    return replace(template, seed=int(seed))


def train_policy_under_config(
    cases: Sequence[TrainingCase],
    *,
    config_template: NucleationConfig,
    actions: Mapping[str, Conditions] | None = None,
    episodes: int = 3000,
    max_steps: int = 7,
    goal_fraction: float = 0.92,
    training_seed: int = 6006,
    alpha: float = 0.20,
    gamma: float = 0.90,
    initial_epsilon: float = 0.35,
    minimum_epsilon: float = 0.03,
    effort_penalty: float = 0.35,
) -> TabularRecoveryPolicy:
    """Train the existing coarse-state Q-policy under a declared recovery law."""

    cases = tuple(cases)
    if not cases:
        raise ValueError("at least one training case is required")
    if episodes <= 0 or max_steps <= 0:
        raise ValueError("episodes and max_steps must be positive")
    if not 0.0 <= goal_fraction <= 1.0:
        raise ValueError("goal_fraction must be in [0, 1]")
    if not 0.0 < alpha <= 1.0 or not 0.0 <= gamma <= 1.0:
        raise ValueError("invalid learning rate or discount")

    action_map = dict(actions or RECOVERY_ACTIONS)
    if not action_map:
        raise ValueError("at least one action is required")
    action_order = tuple(action_map)
    fallback = "cooperate" if "cooperate" in action_map else action_order[0]
    rng = random.Random(training_seed)
    q_values: dict[tuple[int, int, int], dict[str, float]] = {}

    def ensure(key: tuple[int, int, int]) -> dict[str, float]:
        return q_values.setdefault(key, {name: 0.0 for name in action_order})

    for episode in range(episodes):
        case = cases[episode % len(cases)]
        model = NucleationLattice(
            case.initial_state,
            config=config_with_seed(config_template, case.seed),
        )
        epsilon = max(
            minimum_epsilon,
            initial_epsilon * (1.0 - episode / episodes),
        )

        for step_index in range(max_steps):
            key = state_key(model)
            values = ensure(key)
            if rng.random() < epsilon:
                action_name = rng.choice(action_order)
            else:
                action_name = max(
                    action_order,
                    key=lambda name: (values[name], -action_order.index(name)),
                )

            conditions = action_map[action_name]
            before_ordered = model.ordered_fraction()
            before_metastable = model.metastable_fraction()
            model.step(conditions)
            after_ordered = model.ordered_fraction()
            after_metastable = model.metastable_fraction()
            reached_goal = after_ordered >= goal_fraction

            reward = (
                10.0 * (after_ordered - before_ordered)
                + 1.5 * (after_metastable - before_metastable)
                - effort_penalty * declared_control_effort((conditions,))
                + (2.0 if reached_goal else 0.0)
            )

            next_key = state_key(model)
            next_values = ensure(next_key)
            terminal = reached_goal or step_index + 1 >= max_steps
            target = reward if terminal else reward + gamma * max(next_values.values())
            values[action_name] += alpha * (target - values[action_name])

            if reached_goal:
                break

    return TabularRecoveryPolicy(
        actions=action_map,
        q_values=q_values,
        action_order=action_order,
        fallback_action=fallback,
    )


def evaluate_policy_under_config(
    policy: TabularRecoveryPolicy,
    initial: Sequence[Phase | int],
    *,
    config_template: NucleationConfig,
    seed: int,
    max_steps: int = 7,
    goal_fraction: float = 0.92,
) -> LearnedRecoveryResult:
    """Evaluate the learned greedy policy under a frozen recovery law."""

    model = NucleationLattice(
        initial,
        config=config_with_seed(config_template, seed),
    )
    actions: list[str] = []
    schedule: list[Conditions] = []
    first_goal_tick: int | None = 0 if model.ordered_fraction() >= goal_fraction else None

    while model.tick < max_steps and first_goal_tick is None:
        action_name = policy.choose_name(model)
        conditions = policy.actions[action_name]
        actions.append(action_name)
        schedule.append(conditions)
        model.step(conditions)
        if model.ordered_fraction() >= goal_fraction:
            first_goal_tick = model.tick

    return LearnedRecoveryResult(
        actions=tuple(actions),
        schedule=tuple(schedule),
        final_ordered_fraction=model.ordered_fraction(),
        first_goal_tick=first_goal_tick,
        control_effort=declared_control_effort(schedule),
        replay_verified=model.replay() == tuple(model.state),
    )
