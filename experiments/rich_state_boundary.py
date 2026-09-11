"""MorphoMatter Experiment 008: preregistered rich-state causality test.

The protocol was frozen before execution in docs/EXPERIMENT_008_PREREGISTRATION.md.
The only intended experimental change from Experiment 007 is the learned state
representation. Negative or mixed scientific outcomes are reported, not turned
into CI failures. Protocol/replay divergence does fail CI.
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

# Frozen Experiment 007 success counts, used only as protocol-integrity checks.
EXPECTED_COARSE = (49, 46, 42, 38, 32, 16)
EXPECTED_COOPERATIVE = (57, 49, 42, 38, 33, 16)
EXPECTED_BRUTE = (14, 1, 1, 0, 0, 0)
EXPECTED_RANDOM = (416, 371, 324, 263, 174, 69)


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


def learned_result_to_run(result) -> EvaluationRun:
    success = result.first_goal_tick is not None and result.replay_verified
    return EvaluationRun(
        success=success,
        effort_to_goal=result.control_effort if success else None,
        goal_tick=result.first_goal_tick if success else None,
        replay_verified=result.replay_verified,
    )


def summarize(runs: list[EvaluationRun]) -> dict[str, object]:
    successful = [run for run in runs if run.success]
    efforts = [float(run.effort_to_goal) for run in successful if run.effort_to_goal is not None]
    ticks = [float(run.goal_tick) for run in successful if run.goal_tick is not None]
    if len(efforts) != len(successful) or len(ticks) != len(successful):
        raise SystemExit("successful runs are missing effort or tick")
    ci = wilson_interval(len(successful), len(runs))
    return {
        "runs": len(runs),
        "successes": len(successful),
        "rate": len(successful) / len(runs),
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


def _shift_at_least_one_step(left: float | None, right: float | None) -> bool:
    if left is None:
        return False
    if right is None:
        return True
    return left - right >= 0.20 - 1e-12


def main() -> None:
    if LAMBDAS != (0.00, 0.20, 0.40, 0.60, 0.80, 1.00):
        raise SystemExit("preregistered lambda grid changed")
    if set(TRAINING_SEEDS) & set(HELD_OUT_SEEDS):
        raise SystemExit("train and held-out seeds overlap")
    if tuple(RECOVERY_ACTIONS) != ("renucleate", "cooperate", "balanced", "brute", "hold"):
        raise SystemExit("preregistered action set changed")
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

    rich_rates: dict[float, float] = {}
    coarse_rates: dict[float, float] = {}
    cooperative_rates: dict[float, float] = {}
    brute_rates: dict[float, float] = {}
    random_rates: dict[float, float] = {}
    point_summaries: dict[float, dict[str, dict[str, object]]] = {}
    rich_action_totals: Counter[str] = Counter()
    coarse_action_totals: Counter[str] = Counter()

    for lambda_index, lam in enumerate(LAMBDAS):
        config = interpolate_config(EASY_CONFIG, HARD_CONFIG, lam, seed=0)
        coarse_policy = train_policy_under_config(
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
        rich_policy = train_rich_policy_under_config(
            training_cases,
            config_template=config,
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

        rich_runs: list[EvaluationRun] = []
        coarse_runs: list[EvaluationRun] = []
        cooperative_runs: list[EvaluationRun] = []
        brute_runs: list[EvaluationRun] = []
        random_runs: list[EvaluationRun] = []
        rich_actions: Counter[str] = Counter()
        coarse_actions: Counter[str] = Counter()

        case_index = 0
        for _geometry_name, sites in held_out_geometries():
            initial = apply_damage(reference, sites).after
            for seed in HELD_OUT_SEEDS:
                rich = evaluate_rich_policy_under_config(
                    rich_policy,
                    initial,
                    config_template=config,
                    seed=seed,
                    max_steps=MAX_STEPS,
                    goal_fraction=GOAL,
                )
                coarse = evaluate_policy_under_config(
                    coarse_policy,
                    initial,
                    config_template=config,
                    seed=seed,
                    max_steps=MAX_STEPS,
                    goal_fraction=GOAL,
                )
                rich_actions.update(rich.actions)
                coarse_actions.update(coarse.actions)
                rich_runs.append(learned_result_to_run(rich))
                coarse_runs.append(learned_result_to_run(coarse))
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

        if len(rich_runs) != 64 or len(coarse_runs) != 64:
            raise SystemExit(f"learned case count changed at lambda={lam}")
        if len(cooperative_runs) != 64 or len(brute_runs) != 64:
            raise SystemExit(f"fixed comparator case count changed at lambda={lam}")
        if len(random_runs) != 512:
            raise SystemExit(f"random case count changed at lambda={lam}")

        summaries = {
            "rich": summarize(rich_runs),
            "coarse": summarize(coarse_runs),
            "cooperative": summarize(cooperative_runs),
            "brute_force": summarize(brute_runs),
            "random": summarize(random_runs),
        }
        point_summaries[lam] = summaries
        rich_rates[lam] = float(summaries["rich"]["rate"])
        coarse_rates[lam] = float(summaries["coarse"]["rate"])
        cooperative_rates[lam] = float(summaries["cooperative"]["rate"])
        brute_rates[lam] = float(summaries["brute_force"]["rate"])
        random_rates[lam] = float(summaries["random"]["rate"])
        rich_action_totals.update(rich_actions)
        coarse_action_totals.update(coarse_actions)

        expected_index = lambda_index
        observed_integrity = (
            int(summaries["coarse"]["successes"]),
            int(summaries["cooperative"]["successes"]),
            int(summaries["brute_force"]["successes"]),
            int(summaries["random"]["successes"]),
        )
        expected_integrity = (
            EXPECTED_COARSE[expected_index],
            EXPECTED_COOPERATIVE[expected_index],
            EXPECTED_BRUTE[expected_index],
            EXPECTED_RANDOM[expected_index],
        )
        if observed_integrity != expected_integrity:
            raise SystemExit(
                f"Experiment 007 reference curve diverged at lambda={lam}: "
                f"observed={observed_integrity} expected={expected_integrity}"
            )

        print(
            f"lambda={lam:.2f} config: spontaneous={config.spontaneous_rate:.4f} "
            f"frontier_base={config.frontier_base:.4f} "
            f"frontier_neighbor_gain={config.frontier_neighbor_gain:.4f} "
            f"barrier={config.barrier:.4f}"
        )
        print(f"lambda={lam:.2f} rich_action_counts={dict(sorted(rich_actions.items()))}")
        print(f"lambda={lam:.2f} coarse_action_counts={dict(sorted(coarse_actions.items()))}")
        for name in ("rich", "coarse", "cooperative", "brute_force", "random"):
            print_summary(lam, name, summaries[name])

    rich_l50 = lambda50(rich_rates)
    coarse_l50 = lambda50(coarse_rates)
    cooperative_l50 = lambda50(cooperative_rates)
    brute_l50 = lambda50(brute_rates)
    random_l50 = lambda50(random_rates)

    print(
        "lambda50: "
        f"rich={_fmt(rich_l50)} coarse={_fmt(coarse_l50)} "
        f"cooperative={_fmt(cooperative_l50)} brute_force={_fmt(brute_l50)} "
        f"random={_fmt(random_l50)}"
    )
    print("rich_action_totals=", dict(sorted(rich_action_totals.items())))
    print("coarse_action_totals=", dict(sorted(coarse_action_totals.items())))

    separation_exists = any(
        rich_rates[lam] >= 0.50
        and coarse_rates[lam] < 0.50
        and cooperative_rates[lam] < 0.50
        for lam in LAMBDAS
    )
    rich_replay_failures = sum(
        int(point_summaries[lam]["rich"]["replay_failures"])
        for lam in LAMBDAS
    )

    boundary_shift = (
        rich_replay_failures == 0
        and _shift_at_least_one_step(rich_l50, coarse_l50)
        and _shift_at_least_one_step(rich_l50, cooperative_l50)
        and separation_exists
    )

    effort_only = False
    if (
        not boundary_shift
        and rich_l50 is not None
        and rich_l50 == coarse_l50 == cooperative_l50
    ):
        shared = rich_l50
        rich_effort = point_summaries[shared]["rich"]["median_effort"]
        coarse_effort = point_summaries[shared]["coarse"]["median_effort"]
        cooperative_effort = point_summaries[shared]["cooperative"]["median_effort"]
        effort_only = (
            rich_effort is not None
            and coarse_effort is not None
            and cooperative_effort is not None
            and float(rich_effort) < float(coarse_effort)
            and float(rich_effort) < float(cooperative_effort)
        )

    if boundary_shift:
        label = "RICH_STATE_BOUNDARY_SHIFT"
    elif effort_only:
        label = "RICH_STATE_EFFORT_ONLY"
    else:
        label = "RICH_STATE_NO_SHIFT_OR_MIXED"

    print(f"separation_point_exists={separation_exists}")
    print(f"PREREGISTERED_RESULT={label}")

    # Scientific outcome may be negative; evidence integrity may not.
    if rich_replay_failures != 0:
        raise SystemExit("rich-policy replay failure")


if __name__ == "__main__":
    main()
