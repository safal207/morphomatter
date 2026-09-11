"""MorphoMatter Experiment 007: preregistered controllability boundary search.

The protocol was frozen before execution in docs/EXPERIMENT_007_PREREGISTRATION.md
and its NONE-semantics addendum. Scientific overlap or failure is reported as a
result, not converted into a CI failure. CI fails only on protocol or evidence
integrity violations.
"""
from __future__ import annotations

from collections import Counter
from statistics import median
import random

from morphomatter import Conditions, Phase
from morphomatter.boundary import config_signature, interpolate_config, lambda50
from morphomatter.generalization import EvaluationRun, wilson_interval
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

LAMBDAS = (0.00, 0.20, 0.40, 0.60, 0.80, 1.00)
GOAL = 0.90
MAX_STEPS = 9
TRAINING_SEEDS = (109, 113, 127, 131, 137, 139)
HELD_OUT_SEEDS = (149, 151, 157, 163, 167, 173, 179, 181)

EASY_CONFIG = NucleationConfig(width=9, height=9, seed=0)
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
    """Frozen Experiment 006 training geometries reused by preregistration."""

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
    """Frozen Experiment 006 held-out geometries reused by preregistration."""

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
    config_template: NucleationConfig,
    seed: int,
    schedule: tuple[Conditions, ...],
) -> EvaluationRun:
    model = NucleationLattice(initial, config=config_with_seed(config_template, seed))
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


def summarize(runs: list[EvaluationRun]) -> dict[str, object]:
    successes = [run for run in runs if run.success]
    efforts = [float(run.effort_to_goal) for run in successes if run.effort_to_goal is not None]
    ticks = [float(run.goal_tick) for run in successes if run.goal_tick is not None]
    if len(efforts) != len(successes) or len(ticks) != len(successes):
        raise SystemExit("successful runs are missing effort or tick")
    ci = wilson_interval(len(successes), len(runs))
    return {
        "runs": len(runs),
        "successes": len(successes),
        "rate": len(successes) / len(runs),
        "ci": ci,
        "median_effort": median(efforts) if efforts else None,
        "median_tick": median(ticks) if ticks else None,
        "replay_failures": sum(not run.replay_verified for run in runs),
    }


def _fmt(value: object) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def print_summary(lam: float, name: str, summary: dict[str, object]) -> None:
    ci = summary["ci"]
    assert isinstance(ci, tuple)
    print(
        f"lambda={lam:.2f} {name}: "
        f"success={summary['successes']}/{summary['runs']} "
        f"rate={summary['rate']:.6f} "
        f"ci95=[{ci[0]:.3f}, {ci[1]:.3f}] "
        f"median_effort={_fmt(summary['median_effort'])} "
        f"median_tick={_fmt(summary['median_tick'])} "
        f"replay_failures={summary['replay_failures']}"
    )


def _boundary_shift_at_least_one_step(
    learned_boundary: float | None,
    other_boundary: float | None,
) -> bool:
    if learned_boundary is None:
        return False
    if other_boundary is None:
        return True
    return learned_boundary - other_boundary >= 0.20 - 1e-12


def main() -> None:
    if LAMBDAS != (0.00, 0.20, 0.40, 0.60, 0.80, 1.00):
        raise SystemExit("preregistered lambda grid changed")
    if set(TRAINING_SEEDS) & set(HELD_OUT_SEEDS):
        raise SystemExit("train and held-out seed sets overlap")

    if config_signature(interpolate_config(EASY_CONFIG, HARD_CONFIG, 0.0)) != config_signature(EASY_CONFIG):
        raise SystemExit("easy endpoint interpolation mismatch")
    if config_signature(interpolate_config(EASY_CONFIG, HARD_CONFIG, 1.0)) != config_signature(HARD_CONFIG):
        raise SystemExit("hard endpoint interpolation mismatch")

    reference = build_reference_state()
    training_cases = build_training_cases(reference)
    if len(training_cases) != 36:
        raise SystemExit("preregistered training case count changed")

    cooperative_schedule = tuple(
        [RECOVERY_ACTIONS["renucleate"]] * 2
        + [RECOVERY_ACTIONS["cooperate"]] * 7
    )
    brute_schedule = tuple([RECOVERY_ACTIONS["brute"]] * 9)
    action_names = tuple(RECOVERY_ACTIONS)

    learned_rates: dict[float, float] = {}
    cooperative_rates: dict[float, float] = {}
    brute_rates: dict[float, float] = {}
    random_rates: dict[float, float] = {}
    all_learned_replay_failures = 0
    point_summaries: dict[float, dict[str, dict[str, object]]] = {}

    for lambda_index, lam in enumerate(LAMBDAS):
        config = interpolate_config(EASY_CONFIG, HARD_CONFIG, lam, seed=0)
        policy = train_policy_under_config(
            training_cases,
            config_template=config,
            episodes=2400,
            max_steps=MAX_STEPS,
            goal_fraction=GOAL,
            training_seed=7007 + int(lam * 100),
            alpha=0.20,
            gamma=0.90,
            initial_epsilon=0.35,
            minimum_epsilon=0.03,
            effort_penalty=0.35,
        )

        learned_runs: list[EvaluationRun] = []
        cooperative_runs: list[EvaluationRun] = []
        brute_runs: list[EvaluationRun] = []
        random_runs: list[EvaluationRun] = []
        learned_action_counts: Counter[str] = Counter()
        removed_counts: dict[str, int] = {}

        case_index = 0
        for geometry_name, sites in held_out_geometries():
            damage = apply_damage(reference, sites)
            removed_counts[geometry_name] = damage.ordered_sites_removed
            initial = damage.after

            for seed in HELD_OUT_SEEDS:
                learned = evaluate_policy_under_config(
                    policy,
                    initial,
                    config_template=config,
                    seed=seed,
                    max_steps=MAX_STEPS,
                    goal_fraction=GOAL,
                )
                learned_action_counts.update(learned.actions)
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
                        config_template=config,
                        seed=seed,
                        schedule=cooperative_schedule,
                    )
                )
                brute_runs.append(
                    run_fixed_schedule(
                        initial,
                        config_template=config,
                        seed=seed,
                        schedule=brute_schedule,
                    )
                )

                for replicate_index in range(8):
                    rng = random.Random(
                        707000
                        + lambda_index * 100000
                        + case_index * 100
                        + replicate_index
                    )
                    schedule = tuple(
                        RECOVERY_ACTIONS[rng.choice(action_names)]
                        for _ in range(MAX_STEPS)
                    )
                    random_runs.append(
                        run_fixed_schedule(
                            initial,
                            config_template=config,
                            seed=seed,
                            schedule=schedule,
                        )
                    )
                case_index += 1

        if len(learned_runs) != 64 or len(cooperative_runs) != 64 or len(brute_runs) != 64:
            raise SystemExit(f"held-out case count changed at lambda={lam}")
        if len(random_runs) != 512:
            raise SystemExit(f"random run count changed at lambda={lam}")

        learned_summary = summarize(learned_runs)
        cooperative_summary = summarize(cooperative_runs)
        brute_summary = summarize(brute_runs)
        random_summary = summarize(random_runs)
        point_summaries[lam] = {
            "learned": learned_summary,
            "cooperative": cooperative_summary,
            "brute_force": brute_summary,
            "random": random_summary,
        }

        learned_rates[lam] = float(learned_summary["rate"])
        cooperative_rates[lam] = float(cooperative_summary["rate"])
        brute_rates[lam] = float(brute_summary["rate"])
        random_rates[lam] = float(random_summary["rate"])
        all_learned_replay_failures += int(learned_summary["replay_failures"])

        print(
            f"lambda={lam:.2f} config: spontaneous={config.spontaneous_rate:.4f} "
            f"frontier_base={config.frontier_base:.4f} "
            f"frontier_neighbor_gain={config.frontier_neighbor_gain:.4f} "
            f"barrier={config.barrier:.4f}"
        )
        print(
            f"lambda={lam:.2f} ordered_sites_removed={dict(sorted(removed_counts.items()))}"
        )
        print(
            f"lambda={lam:.2f} learned_action_counts={dict(sorted(learned_action_counts.items()))}"
        )
        print_summary(lam, "learned", learned_summary)
        print_summary(lam, "cooperative", cooperative_summary)
        print_summary(lam, "brute_force", brute_summary)
        print_summary(lam, "random_8x64", random_summary)

    learned_boundary = lambda50(learned_rates)
    cooperative_boundary = lambda50(cooperative_rates)
    brute_boundary = lambda50(brute_rates)
    random_boundary = lambda50(random_rates)

    exists_separation_point = any(
        learned_rates[lam] >= 0.50
        and cooperative_rates[lam] < 0.50
        and random_rates[lam] < 0.50
        for lam in LAMBDAS
    )

    shift_signal = (
        all_learned_replay_failures == 0
        and learned_boundary is not None
        and _boundary_shift_at_least_one_step(learned_boundary, cooperative_boundary)
        and _boundary_shift_at_least_one_step(learned_boundary, random_boundary)
        and exists_separation_point
    )

    if learned_boundary is None:
        label = "CONTROLLABILITY_BOUNDARY_NOT_FOUND"
    elif shift_signal:
        label = "CONTROLLABILITY_BOUNDARY_SHIFT_SIGNAL"
    else:
        label = "CONTROLLABILITY_BOUNDARY_OVERLAP"

    def show_boundary(value: float | None) -> str:
        return "NONE" if value is None else f"{value:.2f}"

    print(
        "lambda50: "
        f"learned={show_boundary(learned_boundary)} "
        f"cooperative={show_boundary(cooperative_boundary)} "
        f"brute_force={show_boundary(brute_boundary)} "
        f"random={show_boundary(random_boundary)}"
    )
    print(f"separation_point_exists={exists_separation_point}")
    print(f"PREREGISTERED_RESULT={label}")

    # Evidence integrity is mandatory regardless of the scientific label.
    for lam, summaries in point_summaries.items():
        for name, summary in summaries.items():
            if int(summary["replay_failures"]) != 0:
                raise SystemExit(f"replay failure at lambda={lam} strategy={name}")


if __name__ == "__main__":
    main()
