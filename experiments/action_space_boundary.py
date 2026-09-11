"""MorphoMatter Experiment 009: preregistered action-space ablation.

The protocol was frozen before execution in
`docs/EXPERIMENT_009_PREREGISTRATION.md` and its training-seed addendum.
The intended experimental variable is only the global action map available to
the already-frozen Experiment 008 rich-state learner.

Scientific overlap or failure is preserved as a result. CI fails only on
protocol/evidence integrity violations.
"""
from __future__ import annotations

from collections import Counter
from statistics import median

from morphomatter.action_space import (
    EXPANDED_RECOVERY_ACTIONS,
    validate_expanded_action_space,
)
from morphomatter.boundary import interpolate_config, lambda50
from morphomatter.generalization import EvaluationRun, wilson_interval
from morphomatter.learning import RECOVERY_ACTIONS
from morphomatter.recovery import apply_damage
from morphomatter.rich_learning import (
    evaluate_rich_policy_under_config,
    train_rich_policy_under_config,
)

# Reuse the exact frozen Experiment 008 protocol helpers. This script is run
# from the `experiments/` directory by Python, so that directory is on sys.path.
from rich_state_boundary import (  # type: ignore
    EASY_CONFIG,
    HARD_CONFIG,
    GOAL,
    HELD_OUT_SEEDS,
    LAMBDAS,
    MAX_STEPS,
    build_reference_state,
    build_training_cases,
    held_out_geometries,
    learned_result_to_run,
    run_fixed_schedule,
)


# Frozen Experiment 008 rich-state and cooperative success counts.
EXPECTED_ORIGINAL_RICH = (49, 45, 42, 39, 32, 16)
EXPECTED_COOPERATIVE = (57, 49, 42, 38, 33, 16)


def summarize(runs: list[EvaluationRun]) -> dict[str, object]:
    successful = [run for run in runs if run.success]
    efforts = [
        float(run.effort_to_goal)
        for run in successful
        if run.effort_to_goal is not None
    ]
    ticks = [
        float(run.goal_tick)
        for run in successful
        if run.goal_tick is not None
    ]
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
    validate_expanded_action_space()
    if LAMBDAS != (0.00, 0.20, 0.40, 0.60, 0.80, 1.00):
        raise SystemExit("preregistered lambda grid changed")
    if tuple(RECOVERY_ACTIONS) != (
        "renucleate",
        "cooperate",
        "balanced",
        "brute",
        "hold",
    ):
        raise SystemExit("original recovery action set changed")
    if len(EXPANDED_RECOVERY_ACTIONS) != 11:
        raise SystemExit("expanded recovery action count changed")

    reference = build_reference_state()
    training_cases = build_training_cases(reference)
    if len(training_cases) != 36:
        raise SystemExit("preregistered training case count changed")

    cooperative_schedule = tuple(
        [RECOVERY_ACTIONS["renucleate"]] * 2
        + [RECOVERY_ACTIONS["cooperate"]] * 7
    )

    original_rates: dict[float, float] = {}
    expanded_rates: dict[float, float] = {}
    cooperative_rates: dict[float, float] = {}
    point_summaries: dict[float, dict[str, dict[str, object]]] = {}
    original_action_totals: Counter[str] = Counter()
    expanded_action_totals: Counter[str] = Counter()

    for lambda_index, lam in enumerate(LAMBDAS):
        config = interpolate_config(EASY_CONFIG, HARD_CONFIG, lam, seed=0)
        training_seed = 8008 + int(lam * 100)

        original_policy = train_rich_policy_under_config(
            training_cases,
            config_template=config,
            actions=RECOVERY_ACTIONS,
            episodes=2400,
            max_steps=MAX_STEPS,
            goal_fraction=GOAL,
            training_seed=training_seed,
            alpha=0.20,
            gamma=0.90,
            initial_epsilon=0.35,
            minimum_epsilon=0.03,
            effort_penalty=0.35,
        )
        expanded_policy = train_rich_policy_under_config(
            training_cases,
            config_template=config,
            actions=EXPANDED_RECOVERY_ACTIONS,
            episodes=2400,
            max_steps=MAX_STEPS,
            goal_fraction=GOAL,
            training_seed=training_seed,
            alpha=0.20,
            gamma=0.90,
            initial_epsilon=0.35,
            minimum_epsilon=0.03,
            effort_penalty=0.35,
        )

        original_runs: list[EvaluationRun] = []
        expanded_runs: list[EvaluationRun] = []
        cooperative_runs: list[EvaluationRun] = []
        original_actions: Counter[str] = Counter()
        expanded_actions: Counter[str] = Counter()

        for _geometry_name, sites in held_out_geometries():
            initial = apply_damage(reference, sites).after
            for seed in HELD_OUT_SEEDS:
                original = evaluate_rich_policy_under_config(
                    original_policy,
                    initial,
                    config_template=config,
                    seed=seed,
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
                original_actions.update(original.actions)
                expanded_actions.update(expanded.actions)
                original_runs.append(learned_result_to_run(original))
                expanded_runs.append(learned_result_to_run(expanded))
                cooperative_runs.append(
                    run_fixed_schedule(
                        initial,
                        config_template=config,
                        seed=seed,
                        schedule=cooperative_schedule,
                    )
                )

        if len(original_runs) != 64 or len(expanded_runs) != 64:
            raise SystemExit(f"held-out learned case count changed at lambda={lam}")
        if len(cooperative_runs) != 64:
            raise SystemExit(f"cooperative case count changed at lambda={lam}")

        original_summary = summarize(original_runs)
        expanded_summary = summarize(expanded_runs)
        cooperative_summary = summarize(cooperative_runs)

        if int(original_summary["successes"]) != EXPECTED_ORIGINAL_RICH[lambda_index]:
            raise SystemExit(
                f"Experiment 008 original-rich curve drifted at lambda={lam}"
            )
        if int(cooperative_summary["successes"]) != EXPECTED_COOPERATIVE[lambda_index]:
            raise SystemExit(
                f"Experiment 007 cooperative curve drifted at lambda={lam}"
            )

        original_rates[lam] = float(original_summary["rate"])
        expanded_rates[lam] = float(expanded_summary["rate"])
        cooperative_rates[lam] = float(cooperative_summary["rate"])
        point_summaries[lam] = {
            "original": original_summary,
            "expanded": expanded_summary,
            "cooperative": cooperative_summary,
        }
        original_action_totals.update(original_actions)
        expanded_action_totals.update(expanded_actions)

        print(
            f"lambda={lam:.2f} expanded_action_counts={dict(sorted(expanded_actions.items()))}"
        )
        print(
            f"lambda={lam:.2f} original_action_counts={dict(sorted(original_actions.items()))}"
        )
        print_summary(lam, "rich_original", original_summary)
        print_summary(lam, "rich_expanded", expanded_summary)
        print_summary(lam, "cooperative", cooperative_summary)

    original_boundary = lambda50(original_rates)
    expanded_boundary = lambda50(expanded_rates)
    cooperative_boundary = lambda50(cooperative_rates)

    separation_exists = any(
        expanded_rates[lam] >= 0.50
        and original_rates[lam] < 0.50
        and cooperative_rates[lam] < 0.50
        for lam in LAMBDAS
    )

    capability_shift = (
        _shift_at_least_one_step(expanded_boundary, original_boundary)
        and expanded_boundary is not None
        and cooperative_boundary is not None
        and expanded_boundary > cooperative_boundary
        and separation_exists
        and all(
            int(point_summaries[lam]["expanded"]["replay_failures"]) == 0
            for lam in LAMBDAS
        )
    )

    effort_only = False
    if (
        not capability_shift
        and expanded_boundary is not None
        and original_boundary is not None
        and expanded_boundary == original_boundary
    ):
        boundary = expanded_boundary
        expanded_summary = point_summaries[boundary]["expanded"]
        original_summary = point_summaries[boundary]["original"]
        expanded_effort = expanded_summary["median_effort"]
        original_effort = original_summary["median_effort"]
        if (
            int(expanded_summary["successes"])
            >= int(original_summary["successes"])
            and expanded_effort is not None
            and original_effort is not None
            and float(expanded_effort) < float(original_effort)
        ):
            effort_only = True

    if capability_shift:
        label = "EXPANDED_ACTION_CAPABILITY_SHIFT"
    elif effort_only:
        label = "EXPANDED_ACTION_EFFORT_ONLY"
    else:
        label = "EXPANDED_ACTION_NO_GAIN_OR_MIXED"

    def fmt_boundary(value: float | None) -> str:
        return "NONE" if value is None else f"{value:.2f}"

    print(
        "lambda50: "
        f"expanded={fmt_boundary(expanded_boundary)} "
        f"original={fmt_boundary(original_boundary)} "
        f"cooperative={fmt_boundary(cooperative_boundary)}"
    )
    print("expanded_action_totals=", dict(sorted(expanded_action_totals.items())))
    print("original_action_totals=", dict(sorted(original_action_totals.items())))
    print(f"separation_point_exists={separation_exists}")
    print(f"PREREGISTERED_RESULT={label}")

    if any(
        int(point_summaries[lam][name]["replay_failures"]) != 0
        for lam in LAMBDAS
        for name in ("original", "expanded", "cooperative")
    ):
        raise SystemExit("Experiment 009 replay failure")


if __name__ == "__main__":
    main()
