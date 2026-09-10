"""Minimal learned recovery controller for MorphoMatter Experiment 004.

This module implements a small tabular Q-learning baseline over coarse global
state features. It is intentionally simple: the purpose is to test whether a
policy learned from multiple simulated damage cases can select condition
trajectories on an unseen case. It is not evidence of physical intelligence,
material autonomy, or AI superiority in the real world.
"""
from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Mapping, Sequence

from .core import Conditions, Phase
from .nucleation import NucleationConfig, NucleationLattice
from .recovery import declared_control_effort


RECOVERY_ACTIONS: dict[str, Conditions] = {
    "renucleate": Conditions(drive=0.55, coupling_scale=1.0, threshold_scale=0.8),
    "cooperate": Conditions(drive=0.12, coupling_scale=1.5, threshold_scale=0.8),
    "balanced": Conditions(drive=0.25, coupling_scale=1.25, threshold_scale=0.8),
    "brute": Conditions(drive=0.80, coupling_scale=0.0, threshold_scale=0.8),
    "hold": Conditions(drive=0.02, coupling_scale=1.5, threshold_scale=0.8),
}


@dataclass(frozen=True)
class TrainingCase:
    name: str
    initial_state: tuple[Phase, ...]
    seed: int


@dataclass(frozen=True)
class LearnedRecoveryResult:
    actions: tuple[str, ...]
    schedule: tuple[Conditions, ...]
    final_ordered_fraction: float
    first_goal_tick: int | None
    control_effort: float
    replay_verified: bool


StateKey = tuple[int, int, int]


def _fraction_bin(value: float, bins: int = 10) -> int:
    return max(0, min(bins, int(value * bins + 1e-12)))


def state_key(model: NucleationLattice) -> StateKey:
    """Coarse global state: ordered, metastable, and frontier fractions."""

    cells = len(model.state)
    frontier_fraction = len(model.frontier_sites()) / cells
    return (
        _fraction_bin(model.ordered_fraction()),
        _fraction_bin(model.metastable_fraction()),
        _fraction_bin(frontier_fraction),
    )


@dataclass
class TabularRecoveryPolicy:
    """Deterministic greedy policy over Q-values learned in simulation."""

    actions: Mapping[str, Conditions]
    q_values: dict[StateKey, dict[str, float]]
    action_order: tuple[str, ...]
    fallback_action: str = "cooperate"

    def choose_name(self, model: NucleationLattice) -> str:
        values = self.q_values.get(state_key(model))
        if not values:
            return self.fallback_action
        return max(
            self.action_order,
            key=lambda name: (values.get(name, float("-inf")), -self.action_order.index(name)),
        )

    def choose(self, model: NucleationLattice) -> Conditions:
        return self.actions[self.choose_name(model)]


def train_tabular_policy(
    cases: Sequence[TrainingCase],
    *,
    actions: Mapping[str, Conditions] | None = None,
    episodes: int = 1200,
    max_steps: int = 12,
    goal_fraction: float = 0.90,
    training_seed: int = 2026,
    alpha: float = 0.20,
    gamma: float = 0.90,
    initial_epsilon: float = 0.35,
    minimum_epsilon: float = 0.03,
    effort_penalty: float = 0.35,
) -> TabularRecoveryPolicy:
    """Train a small Q-table on declared simulated recovery cases.

    Reward favors increase in ordered fraction, gives smaller credit for
    metastable progress, penalizes declared control effort, and gives a terminal
    bonus for crossing the goal. All terms are algorithmic and dimensionless.
    """

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
    q_values: dict[StateKey, dict[str, float]] = {}

    def ensure(key: StateKey) -> dict[str, float]:
        return q_values.setdefault(key, {name: 0.0 for name in action_order})

    for episode in range(episodes):
        case = cases[episode % len(cases)]
        model = NucleationLattice(
            case.initial_state,
            config=NucleationConfig(width=9, height=9, seed=case.seed),
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


def evaluate_learned_policy(
    policy: TabularRecoveryPolicy,
    initial: Sequence[Phase | int],
    *,
    seed: int,
    max_steps: int = 12,
    goal_fraction: float = 0.90,
) -> LearnedRecoveryResult:
    """Evaluate greedily and stop once the declared recovery goal is reached."""

    model = NucleationLattice(
        initial,
        config=NucleationConfig(width=9, height=9, seed=seed),
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
