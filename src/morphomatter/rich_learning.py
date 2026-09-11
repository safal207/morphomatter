"""Rich-state tabular recovery learner for MorphoMatter Experiment 008.

Experiment 008 changes only the observation/state representation relative to
Experiment 007. The transition law, action set, reward, learning budget,
training/held-out cases, goal, and horizon remain frozen by preregistration.

This is a software ablation. The state features do not imply physical sensors.
"""
from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Mapping, Sequence

from .core import Conditions, Phase
from .hard_learning import config_with_seed
from .learning import RECOVERY_ACTIONS, LearnedRecoveryResult, TrainingCase
from .nucleation import NucleationConfig, NucleationLattice
from .recovery import declared_control_effort


RichStateKey = tuple[int, int, int, int, int, int, int, int]


def _fraction_bin(value: float, bins: int = 10) -> int:
    return max(0, min(bins, int(float(value) * bins + 1e-12)))


def _neighbors(model: NucleationLattice, site: int) -> tuple[int, ...]:
    width = model.config.width
    height = model.config.height
    row, col = divmod(site, width)
    result: list[int] = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        rr, cc = row + dr, col + dc
        if 0 <= rr < height and 0 <= cc < width:
            result.append(rr * width + cc)
    return tuple(result)


def _component_summary(model: NucleationLattice) -> tuple[int, float]:
    """Return non-ordered component count and largest-component fraction."""

    non_ordered = {
        site
        for site, phase in enumerate(model.state)
        if phase is not Phase.ORDERED
    }
    if not non_ordered:
        return 0, 0.0

    unseen = set(non_ordered)
    component_sizes: list[int] = []
    while unseen:
        start = unseen.pop()
        stack = [start]
        size = 0
        while stack:
            site = stack.pop()
            size += 1
            for neighbor in _neighbors(model, site):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
        component_sizes.append(size)

    cells = len(model.state)
    return len(component_sizes), max(component_sizes) / cells


def _mean_frontier_support(model: NucleationLattice) -> float:
    frontier = model.frontier_sites()
    if not frontier:
        return 0.0

    support = 0.0
    for site in frontier:
        neighbors = _neighbors(model, site)
        if neighbors:
            support += sum(
                model.state[neighbor] is Phase.ORDERED
                for neighbor in neighbors
            ) / len(neighbors)
    return support / len(frontier)


def _recent_commit_category(model: NucleationLattice) -> int:
    """Categorize ORDERED commits emitted on the immediately preceding tick."""

    if model.tick <= 0:
        return 0
    commits = sum(
        event.tick == model.tick and event.after is Phase.ORDERED
        for event in model.trace
    )
    if commits == 0:
        return 0
    if commits <= 3:
        return 1
    return 2


def _remaining_horizon_bucket(model: NucleationLattice, max_steps: int) -> int:
    remaining = max(0, max_steps - model.tick)
    if remaining <= 3:
        return 0
    if remaining <= 6:
        return 1
    return 2


def rich_state_key(model: NucleationLattice, *, max_steps: int) -> RichStateKey:
    """Frozen Experiment 008 observation without case labels or future draws."""

    if max_steps <= 0:
        raise ValueError("max_steps must be positive")
    cells = len(model.state)
    frontier_fraction = len(model.frontier_sites()) / cells
    component_count, largest_component_fraction = _component_summary(model)
    mean_support = _mean_frontier_support(model)

    return (
        _fraction_bin(model.ordered_fraction()),
        _fraction_bin(model.metastable_fraction()),
        _fraction_bin(frontier_fraction),
        _fraction_bin(largest_component_fraction, bins=4),
        min(component_count, 3),
        _fraction_bin(mean_support, bins=4),
        _recent_commit_category(model),
        _remaining_horizon_bucket(model, max_steps),
    )


@dataclass
class RichTabularRecoveryPolicy:
    actions: Mapping[str, Conditions]
    q_values: dict[RichStateKey, dict[str, float]]
    action_order: tuple[str, ...]
    max_steps: int
    fallback_action: str = "cooperate"

    def choose_name(self, model: NucleationLattice) -> str:
        values = self.q_values.get(rich_state_key(model, max_steps=self.max_steps))
        if not values:
            return self.fallback_action
        return max(
            self.action_order,
            key=lambda name: (
                values.get(name, float("-inf")),
                -self.action_order.index(name),
            ),
        )

    def choose(self, model: NucleationLattice) -> Conditions:
        return self.actions[self.choose_name(model)]


def train_rich_policy_under_config(
    cases: Sequence[TrainingCase],
    *,
    config_template: NucleationConfig,
    actions: Mapping[str, Conditions] | None = None,
    episodes: int = 2400,
    max_steps: int = 9,
    goal_fraction: float = 0.90,
    training_seed: int = 8008,
    alpha: float = 0.20,
    gamma: float = 0.90,
    initial_epsilon: float = 0.35,
    minimum_epsilon: float = 0.03,
    effort_penalty: float = 0.35,
) -> RichTabularRecoveryPolicy:
    """Train the preregistered rich-state Q learner under a frozen law."""

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
    q_values: dict[RichStateKey, dict[str, float]] = {}

    def ensure(key: RichStateKey) -> dict[str, float]:
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
            key = rich_state_key(model, max_steps=max_steps)
            values = ensure(key)
            if rng.random() < epsilon:
                action_name = rng.choice(action_order)
            else:
                action_name = max(
                    action_order,
                    key=lambda name: (
                        values[name],
                        -action_order.index(name),
                    ),
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

            next_key = rich_state_key(model, max_steps=max_steps)
            next_values = ensure(next_key)
            terminal = reached_goal or step_index + 1 >= max_steps
            target = reward if terminal else reward + gamma * max(next_values.values())
            values[action_name] += alpha * (target - values[action_name])

            if reached_goal:
                break

    return RichTabularRecoveryPolicy(
        actions=action_map,
        q_values=q_values,
        action_order=action_order,
        max_steps=max_steps,
        fallback_action=fallback,
    )


def evaluate_rich_policy_under_config(
    policy: RichTabularRecoveryPolicy,
    initial: Sequence[Phase | int],
    *,
    config_template: NucleationConfig,
    seed: int,
    max_steps: int = 9,
    goal_fraction: float = 0.90,
) -> LearnedRecoveryResult:
    """Greedy held-out evaluation with exact transition replay."""

    if max_steps != policy.max_steps:
        raise ValueError("evaluation horizon must match trained policy horizon")
    model = NucleationLattice(
        initial,
        config=config_with_seed(config_template, seed),
    )
    action_names: list[str] = []
    schedule: list[Conditions] = []
    first_goal_tick: int | None = 0 if model.ordered_fraction() >= goal_fraction else None

    while model.tick < max_steps and first_goal_tick is None:
        action_name = policy.choose_name(model)
        conditions = policy.actions[action_name]
        action_names.append(action_name)
        schedule.append(conditions)
        model.step(conditions)
        if model.ordered_fraction() >= goal_fraction:
            first_goal_tick = model.tick

    return LearnedRecoveryResult(
        actions=tuple(action_names),
        schedule=tuple(schedule),
        final_ordered_fraction=model.ordered_fraction(),
        first_goal_tick=first_goal_tick,
        control_effort=declared_control_effort(schedule),
        replay_verified=model.replay() == tuple(model.state),
    )
