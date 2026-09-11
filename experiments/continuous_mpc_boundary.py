"""MorphoMatter Experiment 010: preregistered continuous MPC reachability probe.

Protocol is frozen in docs/EXPERIMENT_010_PREREGISTRATION.md. A negative
scientific result is reported rather than turned into CI failure. CI fails on
protocol drift, comparator drift, case-count drift, or replay failure.
"""
from __future__ import annotations

from statistics import median

from morphomatter import Conditions, Phase
from morphomatter.action_space import EXPANDED_RECOVERY_ACTIONS, validate_expanded_action_space
from morphomatter.boundary import config_signature, interpolate_config, lambda50
from morphomatter.continuous_mpc import (
    COUPLING_BOUNDS,
    DRIVE_BOUNDS,
    THRESHOLD_BOUNDS,
    run_continuous_mpc,
    validate_planner_protocol,
)
from morphomatter.generalization import EvaluationRun, wilson_interval
from morphomatter.hard_learning import config_with_seed
from morphomatter.learning import TrainingCase
from morphomatter.nucleation import NucleationConfig, NucleationLattice
from morphomatter.recovery import apply_damage, rectangular_sites
from morphomatter.rich_learning import (
    evaluate_rich_policy_under_config,
    train_rich_policy_under_config,
)


ASSEMBLY = (
    [Conditions(drive=0.45, coupling_scale=1.0, threshold_scale=0.8)] * 2
    + [Conditions(drive=0.12, coupling_scale=1.5, threshold_scale=0.8)] * 22
)
LAMBDAS = (0.00, 0.20, 0.40, 0.60, 0.80, 1.00)
GOAL = 0.90
MAX_STEPS = 9
TRAINING_SEEDS = (109, 113, 127, 131, 137, 139)
HELD_OUT_SEEDS = (149, 151, 157, 163, 167, 173, 179, 181)
EXPECTED_EXPANDED = (49, 45, 42, 40, 35, 19)
EXPECTED_COOPERATIVE = (57, 49, 42, 38, 33, 16)

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


def summarize(runs: list[EvaluationRun]) -> dict[str, object]:
    successful = [run for run in runs if run.success]
    efforts = [float(run.effort_to_goal) for run in successful if run.effort_to_goal is not None]
    ticks = [float(run.goal_tick) for run in successful if run.goal_tick is not None]
    if len(efforts) != len(successful) or len(ticks) != len(successful):
        raise SystemExit("successful runs are missing effort or tick")
    return {
        "runs": len(runs),
        "successes": len(successful),
        "rate": len(successful) / len(runs),
        "ci": wilson_interval(len(successful), len(runs)),
        "median_effort": median(efforts) if efforts else None,
        "median_tick": median(ticks) if ticks else None,
        "replay_failures": sum(not run.replay_verified for run in runs),
    }


def to_evaluation(result) -> EvaluationRun:
    success = result.first_goal_tick is not None and result.replay_verified
    return EvaluationRun(
        success=success,
        effort_to_goal=result.control_effort if success else None,
        goal_tick=result.first_goal_tick if success else None,
        replay_verified=result.replay_verified,
    )


def print_summary(lam: float, name: str, summary: dict[str, object]) -> None:
    ci = summary["ci"]
    assert isinstance(ci, tuple)
    effort = summary["median_effort"]
    tick = summary["median_tick"]
    print(
        f"lambda={lam:.2f} {name}: "
        f"success={summary['successes']}/{summary['runs']} "
        f"rate={summary['rate']:.6f} "
        f"ci95=[{ci[0]:.3f}, {ci[1]:.3f}] "
        f"median_effort={'NA' if effort is None else f'{effort:.3f}'} "
        f"median_tick={'NA' if tick is None else f'{tick:.3f}'} "
        f"replay_failures={summary['replay_failures']}"
    )


def main() -> None:
    validate_planner_protocol()
    validate_expanded_action_space()
    if LAMBDAS != (0.00, 0.20, 0.40, 0.60, 0.80, 1.00):
        raise SystemExit("Experiment 010 lambda grid changed")
    if DRIVE_BOUNDS != (0.02, 0.80):
        raise SystemExit("Experiment 010 drive envelope changed")
    if COUPLING_BOUNDS != (0.00, 1.80):
        raise SystemExit("Experiment 010 coupling envelope changed")
    if THRESHOLD_BOUNDS != (0.70, 0.90):
        raise SystemExit("Experiment 010 threshold envelope changed")
    if set(TRAINING_SEEDS) & set(HELD_OUT_SEEDS):
        raise SystemExit("train and held-out seed sets overlap")
    if config_signature(interpolate_config(EASY_CONFIG, HARD_CONFIG, 0.0)) != config_signature(EASY_CONFIG):
        raise SystemExit("easy endpoint interpolation mismatch")
    if config_signature(interpolate_config(EASY_CONFIG, HARD_CONFIG, 1.0)) != config_signature(HARD_CONFIG):
        raise SystemExit("hard endpoint interpolation mismatch")

    reference = build_reference_state()
    training_cases = build_training_cases(reference)
    if len(training_cases) != 36:
        raise SystemExit("Experiment 010 training case count changed")

    planner_rates: dict[float, float] = {}
    expanded_rates: dict[float, float] = {}
    point_summaries: dict[float, dict[str, dict[str, object]]] = {}

    for lambda_index, lam in enumerate(LAMBDAS):
        config = interpolate_config(EASY_CONFIG, HARD_CONFIG, lam, seed=0)
        expanded_policy = train_rich_policy_under_config(
            training_cases,
            config_template=config,
            actions=EXPANDED_RECOVERY_ACTIONS,
            episodes=2400,
            max_steps=MAX_STEPS,
            goal_fraction=GOAL,
            training_seed=8008 + int(lam * 100),
            alpha=0.20,
            gamma=0.90,
            initial_epsilon=0.35,
            minimum_epsilon=0.03,
            effort_penalty=0.35,
        )

        planner_runs: list[EvaluationRun] = []
        expanded_runs: list[EvaluationRun] = []
        case_index = 0
        for _geometry_name, sites in held_out_geometries():
            initial = apply_damage(reference, sites).after
            for seed in HELD_OUT_SEEDS:
                case_config = config_with_seed(config, seed)
                planner = run_continuous_mpc(
                    initial,
                    config=case_config,
                    lambda_index=lambda_index,
                    case_index=case_index,
                    max_steps=MAX_STEPS,
                    goal_fraction=GOAL,
                )
                expanded = evaluate_rich_policy_under_config(
                    expanded_policy,
                    initial,
                    config_template=config,
                    seed=seed,
                    max_steps=MAX_STEPS,
                    goal_fraction=GOAL,
                )
                planner_runs.append(to_evaluation(planner))
                expanded_runs.append(to_evaluation(expanded))
                case_index += 1

        if len(planner_runs) != 64 or len(expanded_runs) != 64:
            raise SystemExit(f"held-out case count changed at lambda={lam}")

        planner_summary = summarize(planner_runs)
        expanded_summary = summarize(expanded_runs)
        point_summaries[lam] = {
            "planner": planner_summary,
            "expanded": expanded_summary,
        }
        planner_rates[lam] = float(planner_summary["rate"])
        expanded_rates[lam] = float(expanded_summary["rate"])

        if int(expanded_summary["successes"]) != EXPECTED_EXPANDED[lambda_index]:
            raise SystemExit(
                f"Experiment 009 comparator drift at lambda={lam}: "
                f"expected {EXPECTED_EXPANDED[lambda_index]}, "
                f"got {expanded_summary['successes']}"
            )

        print_summary(lam, "continuous_mpc", planner_summary)
        print_summary(lam, "expanded_rich", expanded_summary)
        print(
            f"lambda={lam:.2f} frozen_cooperative_success="
            f"{EXPECTED_COOPERATIVE[lambda_index]}/64"
        )

    planner_boundary = lambda50(planner_rates)
    expanded_boundary = lambda50(expanded_rates)
    cooperative_boundary = 0.80
    print(
        "lambda50: "
        f"continuous_mpc={'NONE' if planner_boundary is None else f'{planner_boundary:.2f}'} "
        f"expanded_rich={'NONE' if expanded_boundary is None else f'{expanded_boundary:.2f}'} "
        f"cooperative={cooperative_boundary:.2f}"
    )

    if any(int(point_summaries[lam]["planner"]["replay_failures"]) for lam in LAMBDAS):
        raise SystemExit("Experiment 010 planner replay failure")

    lambda_one_planner = int(point_summaries[1.00]["planner"]["successes"])
    lambda_eight_planner = point_summaries[0.80]["planner"]

    boundary_shift = (
        planner_boundary == 1.00
        and expanded_boundary == 0.80
        and cooperative_boundary == 0.80
        and lambda_one_planner >= 32
        and EXPECTED_EXPANDED[-1] < 32
        and EXPECTED_COOPERATIVE[-1] < 32
    )

    effort_only = (
        planner_boundary == 0.80
        and int(lambda_eight_planner["successes"]) >= EXPECTED_EXPANDED[4]
        and lambda_eight_planner["median_effort"] is not None
        and float(lambda_eight_planner["median_effort"]) < 1.700
    )

    if boundary_shift:
        label = "CONTINUOUS_MPC_BOUNDARY_SHIFT"
    elif effort_only:
        label = "CONTINUOUS_MPC_EFFORT_ONLY"
    else:
        label = "CONTINUOUS_MPC_NO_GAIN_OR_MIXED"

    print(f"PREREGISTERED_RESULT={label}")


if __name__ == "__main__":
    main()
