"""MorphoMatter Experiment 006: preregistered hard transition regime.

Protocol was frozen before execution in docs/EXPERIMENT_006_PREREGISTRATION.md
and its deterministic-seed addendum. A negative or mixed scientific outcome is
reported, not converted into a CI failure. CI fails only on protocol/evidence
integrity problems such as wrong case counts or replay divergence.
"""
from __future__ import annotations

from collections import Counter
import random
from statistics import median

from morphomatter import Conditions, Phase
from morphomatter.generalization import (
    EvaluationRun,
    paired_median_advantage_interval,
    summarize_runs,
)
from morphomatter.hard_learning import (
    config_with_seed,
    evaluate_policy_under_config,
    train_policy_under_config,
)
from morphomatter.learning import RECOVERY_ACTIONS, TrainingCase
from morphomatter.nucleation import NucleationConfig, NucleationLattice
from morphomatter.recovery import apply_damage, declared_control_effort, rectangular_sites


ASSEMBLY = (
    [Conditions(drive=0.45, coupling_scale=1.0, threshold_scale=0.8)] * 2
    + [Conditions(drive=0.12, coupling_scale=1.5, threshold_scale=0.8)] * 22
)
GOAL = 0.92
MAX_STEPS = 7
TRAINING_SEEDS = (5, 13, 17, 61, 67, 71)
HELD_OUT_SEEDS = (73, 79, 83, 89, 97, 101, 103, 107)

HARD_CONFIG = NucleationConfig(
    width=9,
    height=9,
    seed=0,
    spontaneous_rate=0.002,
    nucleation_drive_gain=0.18,
    frontier_base=0.03,
    frontier_neighbor_gain=0.50,
    frontier_drive_gain=0.12,
    commit_base=0.14,
    commit_neighbor_gain=0.30,
    commit_drive_gain=0.25,
    barrier=0.16,
)


def build_reference_state() -> tuple[Phase, ...]:
    model = NucleationLattice(config=NucleationConfig(width=9, height=9, seed=26))
    model.run(ASSEMBLY)
    if sum(phase is Phase.ORDERED for phase in model.state) != 77:
        raise SystemExit("Experiment 002 reference state changed")
    return tuple(model.state)


def _union(*groups: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(set().union(*groups)))


def _cells(predicate) -> tuple[int, ...]:
    return tuple(
        row * 9 + col
        for row in range(9)
        for col in range(9)
        if predicate(row, col)
    )


def training_geometries() -> tuple[tuple[str, tuple[int, ...]], ...]:
    return (
        ("train_rect_a", rectangular_sites(width=9, height=9, top=1, left=1, rows=3, cols=5)),
        ("train_rect_b", rectangular_sites(width=9, height=9, top=1, left=5, rows=5, cols=3)),
        ("train_hband", rectangular_sites(width=9, height=9, top=5, left=1, rows=2, cols=7)),
        ("train_offcenter", rectangular_sites(width=9, height=9, top=3, left=1, rows=4, cols=4)),
        (
            "train_l",
            _union(
                rectangular_sites(width=9, height=9, top=1, left=2, rows=5, cols=1),
                rectangular_sites(width=9, height=9, top=5, left=2, rows=1, cols=5),
            ),
        ),
        (
            "train_two_islands",
            _union(
                rectangular_sites(width=9, height=9, top=1, left=1, rows=3, cols=3),
                rectangular_sites(width=9, height=9, top=5, left=5, rows=3, cols=3),
            ),
        ),
    )


def held_out_geometries() -> tuple[tuple[str, tuple[int, ...]], ...]:
    return (
        ("center_6x6", rectangular_sites(width=9, height=9, top=1, left=1, rows=6, cols=6)),
        (
            "wide_cross",
            _union(
                rectangular_sites(width=9, height=9, top=3, left=1, rows=3, cols=7),
                rectangular_sites(width=9, height=9, top=1, left=3, rows=7, cols=3),
            ),
        ),
        (
            "double_vertical",
            _union(
                rectangular_sites(width=9, height=9, top=1, left=1, rows=7, cols=2),
                rectangular_sites(width=9, height=9, top=1, left=6, rows=7, cols=2),
            ),
        ),
        (
            "double_horizontal",
            _union(
                rectangular_sites(width=9, height=9, top=1, left=1, rows=2, cols=7),
                rectangular_sites(width=9, height=9, top=6, left=1, rows=2, cols=7),
            ),
        ),
        (
            "hollow_7x7",
            _cells(
                lambda r, c: 1 <= r <= 7
                and 1 <= c <= 7
                and (r in {1, 7} or c in {1, 7})
            ),
        ),
        ("thick_diagonal", _cells(lambda r, c: abs(r - c) <= 1)),
        (
            "corner_blocks",
            _union(
                rectangular_sites(width=9, height=9, top=0, left=0, rows=4, cols=4),
                rectangular_sites(width=9, height=9, top=5, left=5, rows=4, cols=4),
            ),
        ),
        (
            "central_plus_ring",
            _union(
                rectangular_sites(width=9, height=9, top=3, left=3, rows=3, cols=3),
                _cells(
                    lambda r, c: 1 <= r <= 7
                    and 1 <= c <= 7
                    and (r in {1, 7} or c in {1, 7})
                ),
            ),
        ),
    )


def build_training_cases(reference: tuple[Phase, ...]) -> tuple[TrainingCase, ...]:
    cases: list[TrainingCase] = []
    for geometry_name, sites in training_geometries():
        damaged = apply_damage(reference, sites).after
        for seed in TRAINING_SEEDS:
            cases.append(
                TrainingCase(
                    name=f"{geometry_name}-seed-{seed}",
                    initial_state=damaged,
                    seed=seed,
                )
            )
    return tuple(cases)


def run_fixed_schedule(
    initial: tuple[Phase, ...],
    *,
    seed: int,
    schedule: tuple[Conditions, ...],
) -> EvaluationRun:
    model = NucleationLattice(initial, config=config_with_seed(HARD_CONFIG, seed))
    used: list[Conditions] = []
    goal_tick: int | None = 0 if model.ordered_fraction() >= GOAL else None
    for conditions in schedule[:MAX_STEPS]:
        if goal_tick is not None:
            break
        used.append(conditions)
        model.step(conditions)
        if model.ordered_fraction() >= GOAL:
            goal_tick = model.tick
    replay = model.replay() == tuple(model.state)
    return EvaluationRun(
        success=goal_tick is not None and replay,
        effort_to_goal=declared_control_effort(used) if goal_tick is not None else None,
        goal_tick=goal_tick,
        replay_verified=replay,
    )


def learned_run(policy, initial: tuple[Phase, ...], seed: int) -> EvaluationRun:
    result = evaluate_policy_under_config(
        policy,
        initial,
        config_template=HARD_CONFIG,
        seed=seed,
        max_steps=MAX_STEPS,
        goal_fraction=GOAL,
    )
    success = result.first_goal_tick is not None and result.replay_verified
    return EvaluationRun(
        success=success,
        effort_to_goal=result.control_effort if success else None,
        goal_tick=result.first_goal_tick if success else None,
        replay_verified=result.replay_verified,
    )


def print_summary(name: str, summary) -> None:
    effort = "NA" if summary.median_effort is None else f"{summary.median_effort:.3f}"
    effort_ci = (
        "NA"
        if summary.effort_ci95 is None
        else f"[{summary.effort_ci95[0]:.3f}, {summary.effort_ci95[1]:.3f}]"
    )
    tick = "NA" if summary.median_goal_tick is None else f"{summary.median_goal_tick:.3f}"
    print(
        f"{name}: success={summary.successes}/{summary.runs} "
        f"rate={summary.success_rate:.6f} "
        f"ci95=[{summary.success_ci95[0]:.3f}, {summary.success_ci95[1]:.3f}] "
        f"median_effort={effort} effort_ci95={effort_ci} "
        f"median_tick={tick} replay_failures={summary.replay_failures}"
    )


def main() -> None:
    reference = build_reference_state()
    cases = build_training_cases(reference)
    if len(cases) != 36:
        raise SystemExit("preregistered training case count changed")

    policy = train_policy_under_config(
        cases,
        config_template=HARD_CONFIG,
        episodes=3000,
        max_steps=MAX_STEPS,
        goal_fraction=GOAL,
        training_seed=6006,
        alpha=0.20,
        gamma=0.90,
        initial_epsilon=0.35,
        minimum_epsilon=0.03,
        effort_penalty=0.35,
    )

    cooperative_schedule = tuple(
        [RECOVERY_ACTIONS["renucleate"]] * 2
        + [RECOVERY_ACTIONS["cooperate"]] * 5
    )
    brute_schedule = tuple([RECOVERY_ACTIONS["brute"]] * 7)
    action_names = tuple(RECOVERY_ACTIONS)

    learned_runs: list[EvaluationRun] = []
    cooperative_runs: list[EvaluationRun] = []
    brute_runs: list[EvaluationRun] = []
    random_runs: list[EvaluationRun] = []
    removed_counts: dict[str, int] = {}
    learned_actions: Counter[str] = Counter()

    case_index = 0
    for geometry_name, sites in held_out_geometries():
        damage = apply_damage(reference, sites)
        removed_counts[geometry_name] = damage.ordered_sites_removed
        initial = damage.after
        for seed in HELD_OUT_SEEDS:
            learned = evaluate_policy_under_config(
                policy,
                initial,
                config_template=HARD_CONFIG,
                seed=seed,
                max_steps=MAX_STEPS,
                goal_fraction=GOAL,
            )
            learned_actions.update(learned.actions)
            learned_success = learned.first_goal_tick is not None and learned.replay_verified
            learned_runs.append(
                EvaluationRun(
                    success=learned_success,
                    effort_to_goal=learned.control_effort if learned_success else None,
                    goal_tick=learned.first_goal_tick if learned_success else None,
                    replay_verified=learned.replay_verified,
                )
            )
            cooperative_runs.append(
                run_fixed_schedule(
                    initial,
                    seed=seed,
                    schedule=cooperative_schedule,
                )
            )
            brute_runs.append(
                run_fixed_schedule(initial, seed=seed, schedule=brute_schedule)
            )

            for replicate in range(16):
                rng = random.Random(606000 + case_index * 100 + replicate)
                schedule = tuple(
                    RECOVERY_ACTIONS[rng.choice(action_names)]
                    for _ in range(MAX_STEPS)
                )
                random_runs.append(
                    run_fixed_schedule(initial, seed=seed, schedule=schedule)
                )
            case_index += 1

    if len(learned_runs) != 64 or len(cooperative_runs) != 64 or len(brute_runs) != 64:
        raise SystemExit("preregistered held-out case count changed")
    if len(random_runs) != 1024:
        raise SystemExit("preregistered random run count changed")

    learned_summary = summarize_runs(learned_runs, bootstrap_seed=6007)
    cooperative_summary = summarize_runs(cooperative_runs, bootstrap_seed=6008)
    brute_summary = summarize_runs(brute_runs, bootstrap_seed=6009)
    random_summary = summarize_runs(random_runs, bootstrap_seed=6010)

    paired = None
    try:
        paired = paired_median_advantage_interval(
            learned_runs,
            cooperative_runs,
            seed=6011,
        )
    except ValueError:
        paired = None

    print("preregistered_hard_matrix=8_geometries_x_8_seeds=64")
    print("held_out_seeds=", HELD_OUT_SEEDS)
    print("ordered_sites_removed=", dict(sorted(removed_counts.items())))
    print("learned_action_counts=", dict(sorted(learned_actions.items())))
    print_summary("learned", learned_summary)
    print_summary("cooperative", cooperative_summary)
    print_summary("brute_force", brute_summary)
    print_summary("random_16x64", random_summary)

    if paired is None:
        print("paired_cooperative_minus_learned=NA")
    else:
        print(
            f"paired_cooperative_minus_learned: n={paired[2]} "
            f"median={paired[0]:.6f} "
            f"ci95=[{paired[1][0]:.3f}, {paired[1][1]:.3f}]"
        )

    capability = (
        learned_summary.success_rate >= 0.70
        and learned_summary.success_rate - cooperative_summary.success_rate >= 0.10 - 1e-12
        and learned_summary.success_rate - random_summary.success_rate >= 0.10 - 1e-12
        and learned_summary.replay_failures == 0
    )

    effort_only = False
    if (
        learned_summary.success_rate >= 0.70
        and learned_summary.replay_failures == 0
        and learned_summary.median_effort is not None
        and cooperative_summary.median_effort is not None
        and learned_summary.median_effort < cooperative_summary.median_effort
        and paired is not None
        and paired[1][0] > 0.0
    ):
        effort_only = True

    if capability:
        label = "HARD_REGIME_CAPABILITY_SIGNAL"
    elif effort_only:
        label = "HARD_REGIME_EFFORT_ONLY"
    else:
        label = "HARD_REGIME_MIXED_OR_NEGATIVE"

    print(f"PREREGISTERED_RESULT={label}")

    # Evidence integrity is mandatory regardless of scientific outcome.
    if any(not run.replay_verified for run in learned_runs):
        raise SystemExit("learned replay failure")
    if any(not run.replay_verified for run in cooperative_runs):
        raise SystemExit("cooperative replay failure")
    if any(not run.replay_verified for run in brute_runs):
        raise SystemExit("brute-force replay failure")
    if any(not run.replay_verified for run in random_runs):
        raise SystemExit("random replay failure")


if __name__ == "__main__":
    main()
