"""MorphoMatter Experiment 005: preregistered held-out generalization matrix.

The preregistration lives in docs/EXPERIMENT_005_PREREGISTRATION.md and was
committed before this runner. Do not change held-out cases or pass/fail criteria
in response to observed outcomes.
"""
from __future__ import annotations

import random
from statistics import median

from morphomatter import Conditions, Phase
from morphomatter.generalization import (
    EvaluationRun,
    paired_median_advantage_interval,
    summarize_runs,
)
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
HELD_OUT_SEEDS = (29, 31, 37, 41, 43, 47, 53, 59)
RANDOM_REPLICATES = 16


def build_reference_state() -> tuple[Phase, ...]:
    model = NucleationLattice(config=NucleationConfig(width=9, height=9, seed=26))
    model.run(ASSEMBLY)
    if abs(model.ordered_fraction() - (77 / 81)) > 1e-12:
        raise SystemExit("Experiment 002 reference state changed")
    return tuple(model.state)


def training_cases(reference: tuple[Phase, ...]) -> tuple[TrainingCase, ...]:
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
            cases.append(
                TrainingCase(
                    name=f"rect-{pattern_index}-seed-{seed}",
                    initial_state=apply_damage(reference, sites).after,
                    seed=seed,
                )
            )
    return tuple(cases)


def held_out_patterns() -> tuple[tuple[str, tuple[int, ...]], ...]:
    center = rectangular_sites(width=9, height=9, top=2, left=2, rows=5, cols=5)
    horizontal = rectangular_sites(width=9, height=9, top=3, left=1, rows=2, cols=7)
    vertical = rectangular_sites(width=9, height=9, top=1, left=3, rows=7, cols=2)
    cross = tuple(sorted({4 * 9 + col for col in range(1, 8)} | {row * 9 + 4 for row in range(1, 8)}))
    l_shape = tuple(sorted({row * 9 + 2 for row in range(1, 7)} | {6 * 9 + col for col in range(2, 7)}))
    island_a = set(rectangular_sites(width=9, height=9, top=1, left=1, rows=3, cols=3))
    island_b = set(rectangular_sites(width=9, height=9, top=5, left=5, rows=3, cols=3))
    two_islands = tuple(sorted(island_a | island_b))
    diagonal = tuple(
        row * 9 + col
        for row in range(1, 8)
        for col in range(1, 8)
        if abs(row - col) <= 1
    )
    hollow_box = tuple(
        sorted(
            {
                row * 9 + col
                for row in range(2, 7)
                for col in range(2, 7)
                if row in {2, 6} or col in {2, 6}
            }
        )
    )
    return (
        ("center_5x5", center),
        ("horizontal_band", horizontal),
        ("vertical_band", vertical),
        ("cross", cross),
        ("l_shape", l_shape),
        ("two_islands", two_islands),
        ("diagonal_band", diagonal),
        ("hollow_box", hollow_box),
    )


def run_schedule_until_goal(
    initial: tuple[Phase, ...], seed: int, schedule: tuple[Conditions, ...] | list[Conditions]
) -> EvaluationRun:
    model = NucleationLattice(
        initial, config=NucleationConfig(width=9, height=9, seed=seed)
    )
    used: list[Conditions] = []
    goal_tick: int | None = 0 if model.ordered_fraction() >= GOAL else None
    for conditions in tuple(schedule)[:MAX_STEPS]:
        if goal_tick is not None:
            break
        used.append(conditions)
        model.step(conditions)
        if model.ordered_fraction() >= GOAL:
            goal_tick = model.tick
    return EvaluationRun(
        success=goal_tick is not None,
        effort_to_goal=declared_control_effort(used) if goal_tick is not None else None,
        goal_tick=goal_tick,
        replay_verified=model.replay() == tuple(model.state),
    )


def format_ci(interval: tuple[float, float] | None) -> str:
    if interval is None:
        return "n/a"
    return f"[{interval[0]:.3f}, {interval[1]:.3f}]"


def main() -> None:
    reference = build_reference_state()
    policy = train_tabular_policy(
        training_cases(reference), episodes=1200, training_seed=2026
    )
    patterns = held_out_patterns()
    if len(patterns) != 8 or len({sites for _, sites in patterns}) != 8:
        raise SystemExit("held-out geometry set changed or contains duplicates")

    learned_runs: list[EvaluationRun] = []
    cooperative_runs: list[EvaluationRun] = []
    brute_runs: list[EvaluationRun] = []
    random_runs: list[EvaluationRun] = []

    cooperative_schedule = tuple(
        [RECOVERY_ACTIONS["renucleate"]] * 2
        + [RECOVERY_ACTIONS["cooperate"]] * 10
    )
    brute_schedule = tuple([RECOVERY_ACTIONS["brute"]] * 12)
    action_names = tuple(RECOVERY_ACTIONS)

    case_index = 0
    damage_counts: dict[str, int] = {}
    for pattern_name, sites in patterns:
        damaged = apply_damage(reference, sites)
        damage_counts[pattern_name] = damaged.ordered_sites_removed
        if sum(phase is Phase.ORDERED for phase in damaged.after) / 81 >= GOAL:
            raise SystemExit(f"held-out damage {pattern_name} starts at or above goal")
        for material_seed in HELD_OUT_SEEDS:
            learned = evaluate_learned_policy(
                policy,
                damaged.after,
                seed=material_seed,
                max_steps=MAX_STEPS,
                goal_fraction=GOAL,
            )
            learned_runs.append(
                EvaluationRun(
                    success=learned.first_goal_tick is not None,
                    effort_to_goal=(
                        learned.control_effort
                        if learned.first_goal_tick is not None
                        else None
                    ),
                    goal_tick=learned.first_goal_tick,
                    replay_verified=learned.replay_verified,
                )
            )
            cooperative_runs.append(
                run_schedule_until_goal(damaged.after, material_seed, cooperative_schedule)
            )
            brute_runs.append(
                run_schedule_until_goal(damaged.after, material_seed, brute_schedule)
            )

            for replicate in range(RANDOM_REPLICATES):
                schedule_rng = random.Random(900000 + case_index * 100 + replicate)
                random_schedule = tuple(
                    RECOVERY_ACTIONS[schedule_rng.choice(action_names)]
                    for _ in range(MAX_STEPS)
                )
                random_runs.append(
                    run_schedule_until_goal(damaged.after, material_seed, random_schedule)
                )
            case_index += 1

    if case_index != 64:
        raise SystemExit("held-out matrix is not 64 cases")

    learned_summary = summarize_runs(learned_runs, bootstrap_seed=5005)
    cooperative_summary = summarize_runs(cooperative_runs, bootstrap_seed=5015)
    brute_summary = summarize_runs(brute_runs, bootstrap_seed=5025)
    random_summary = summarize_runs(random_runs, bootstrap_seed=5035)
    paired_median, paired_ci, paired_n = paired_median_advantage_interval(
        learned_runs, cooperative_runs, seed=5006
    )

    print("preregistered_matrix=8_geometries_x_8_seeds=64")
    print("held_out_seeds=", HELD_OUT_SEEDS)
    print("ordered_sites_removed=", dict(sorted(damage_counts.items())))
    for name, summary in (
        ("learned", learned_summary),
        ("cooperative", cooperative_summary),
        ("brute_force", brute_summary),
        ("random_16x64", random_summary),
    ):
        print(
            f"{name}: success={summary.successes}/{summary.runs} "
            f"rate={summary.success_rate:.6f} ci95={format_ci(summary.success_ci95)} "
            f"median_effort={summary.median_effort} effort_ci95={format_ci(summary.effort_ci95)} "
            f"median_tick={summary.median_goal_tick} tick_ci95={format_ci(summary.goal_tick_ci95)} "
            f"replay_failures={summary.replay_failures}"
        )
    print(
        f"paired_cooperative_minus_learned: n={paired_n} median={paired_median:.6f} "
        f"ci95={format_ci(paired_ci)}"
    )

    # Frozen preregistered interpretation boundary.
    failures: list[str] = []
    if learned_summary.success_rate < 0.90:
        failures.append("learned success rate < 0.90")
    if learned_summary.replay_failures != 0:
        failures.append("learned replay failures observed")
    if (
        learned_summary.median_effort is None
        or cooperative_summary.median_effort is None
        or learned_summary.median_effort >= cooperative_summary.median_effort
    ):
        failures.append("learned median effort did not beat cooperative")
    if paired_ci[0] <= 0.0:
        failures.append("paired effort-advantage CI lower bound <= 0")
    if (
        learned_summary.median_effort is None
        or random_summary.median_effort is None
        or learned_summary.median_effort >= random_summary.median_effort
    ):
        failures.append("learned median effort did not beat random")

    if failures:
        print("PREREGISTERED_RESULT=MIXED_OR_FAIL")
        raise SystemExit("; ".join(failures))
    print("PREREGISTERED_RESULT=BOUNDED_GENERALIZATION_SIGNAL")


if __name__ == "__main__":
    main()
