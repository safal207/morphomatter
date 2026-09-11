"""MorphoMatter Experiment 004: learned recovery on unseen damage.

A small tabular Q-learning policy is trained on multiple rectangular damage
patterns and seeds, then evaluated on a held-out 5x5 central damage pattern and
a held-out stochastic seed. This is a simulation-only ML baseline, not evidence
of physical AI-controlled matter.
"""
from __future__ import annotations

import random
from statistics import median

from morphomatter import Conditions
from morphomatter.learning import (
    RECOVERY_ACTIONS,
    TrainingCase,
    evaluate_learned_policy,
    train_tabular_policy,
)
from morphomatter.nucleation import NucleationConfig, NucleationLattice
from morphomatter.recovery import apply_damage, declared_control_effort, rectangular_sites


ASSEMBLY = (
    [Conditions(drive=0.45, coupling_scale=1.0, threshold_scale=0.8)] * 2
    + [Conditions(drive=0.12, coupling_scale=1.5, threshold_scale=0.8)] * 22
)
GOAL = 0.90
MAX_STEPS = 12


def build_reference_state() -> tuple:
    model = NucleationLattice(config=NucleationConfig(width=9, height=9, seed=26))
    model.run(ASSEMBLY)
    if abs(model.ordered_fraction() - (77 / 81)) > 1e-12:
        raise SystemExit("Experiment 002 reference state changed")
    return tuple(model.state)


def training_cases(reference: tuple) -> tuple[TrainingCase, ...]:
    patterns = (
        rectangular_sites(width=9, height=9, top=1, left=1, rows=3, cols=4),
        rectangular_sites(width=9, height=9, top=1, left=4, rows=4, cols=3),
        rectangular_sites(width=9, height=9, top=3, left=1, rows=3, cols=5),
        rectangular_sites(width=9, height=9, top=4, left=3, rows=3, cols=4),
    )
    seeds = (3, 7, 11, 19, 23)
    cases: list[TrainingCase] = []
    for seed in seeds:
        for pattern_index, sites in enumerate(patterns):
            damaged = apply_damage(reference, sites).after
            cases.append(
                TrainingCase(
                    name=f"rect-{pattern_index}-seed-{seed}",
                    initial_state=damaged,
                    seed=seed,
                )
            )
    return tuple(cases)


def run_schedule_until_goal(initial: tuple, seed: int, schedule: list[Conditions]) -> tuple[float, int | None, float, bool]:
    model = NucleationLattice(initial, config=NucleationConfig(width=9, height=9, seed=seed))
    used: list[Conditions] = []
    first_goal_tick: int | None = 0 if model.ordered_fraction() >= GOAL else None
    for conditions in schedule[:MAX_STEPS]:
        if first_goal_tick is not None:
            break
        used.append(conditions)
        model.step(conditions)
        if model.ordered_fraction() >= GOAL:
            first_goal_tick = model.tick
    return (
        model.ordered_fraction(),
        first_goal_tick,
        declared_control_effort(used),
        model.replay() == tuple(model.state),
    )


def main() -> None:
    reference = build_reference_state()
    cases = training_cases(reference)
    policy = train_tabular_policy(cases, episodes=1200, training_seed=2026)

    held_out_sites = rectangular_sites(
        width=9,
        height=9,
        top=2,
        left=2,
        rows=5,
        cols=5,
    )
    held_out = apply_damage(reference, held_out_sites)
    test_seed = 37

    learned = evaluate_learned_policy(
        policy,
        held_out.after,
        seed=test_seed,
        max_steps=MAX_STEPS,
        goal_fraction=GOAL,
    )

    cooperative_schedule = (
        [RECOVERY_ACTIONS["renucleate"]] * 2
        + [RECOVERY_ACTIONS["cooperate"]] * 10
    )
    brute_schedule = [RECOVERY_ACTIONS["brute"]] * 12
    cooperative = run_schedule_until_goal(held_out.after, test_seed, cooperative_schedule)
    brute = run_schedule_until_goal(held_out.after, test_seed, brute_schedule)

    random_efforts: list[float] = []
    random_ticks: list[int] = []
    random_successes = 0
    action_names = tuple(RECOVERY_ACTIONS)
    for random_index in range(32):
        rng = random.Random(1000 + random_index)
        schedule = [
            RECOVERY_ACTIONS[rng.choice(action_names)]
            for _ in range(MAX_STEPS)
        ]
        final_fraction, goal_tick, effort, replay_ok = run_schedule_until_goal(
            held_out.after,
            test_seed,
            schedule,
        )
        if not replay_ok:
            raise SystemExit("random baseline replay failed")
        if goal_tick is not None:
            random_successes += 1
            random_efforts.append(effort)
            random_ticks.append(goal_tick)

    print(
        f"held_out_damage=central_5x5 ordered_removed={held_out.ordered_sites_removed} "
        f"start_ordered={sum(p.value == 2 for p in held_out.after)}/81 seed={test_seed}"
    )
    print(
        f"learned: actions={list(learned.actions)} final={learned.final_ordered_fraction:.6f} "
        f"goal_tick={learned.first_goal_tick} effort={learned.control_effort:.3f} "
        f"replay={learned.replay_verified}"
    )
    print(
        f"cooperative: final={cooperative[0]:.6f} goal_tick={cooperative[1]} "
        f"effort_to_goal={cooperative[2]:.3f} replay={cooperative[3]}"
    )
    print(
        f"brute_force: final={brute[0]:.6f} goal_tick={brute[1]} "
        f"effort_to_goal={brute[2]:.3f} replay={brute[3]}"
    )
    print(
        f"random_32: successes={random_successes}/32 "
        f"median_goal_tick={median(random_ticks):.3f} "
        f"median_effort_to_goal={median(random_efforts):.3f}"
    )

    if held_out.ordered_sites_removed != 25:
        raise SystemExit("held-out damage intervention changed")
    if learned.first_goal_tick is None or learned.final_ordered_fraction < GOAL:
        raise SystemExit("learned policy did not recover held-out damage")
    if not learned.replay_verified:
        raise SystemExit("learned recovery replay failed")
    if learned.control_effort >= cooperative[2]:
        raise SystemExit("learned policy did not beat cooperative effort-to-goal")
    if learned.control_effort >= brute[2]:
        raise SystemExit("learned policy did not beat brute-force effort-to-goal")
    if learned.control_effort >= median(random_efforts):
        raise SystemExit("learned policy did not beat median random effort-to-goal")


if __name__ == "__main__":
    main()
