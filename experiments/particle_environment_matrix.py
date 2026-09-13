"""MorphoMatter Experiment 017: particle property × environment matrix."""
from __future__ import annotations

from morphomatter.environment_screening import IONIC_STRENGTH_GRID, attractive_potential
from morphomatter.interface_chemistry import interface_nucleation_point
from morphomatter.nucleation import NucleationConfig
from morphomatter.particle_environment import (
    EXP016_ACCESS_ROOT,
    EXP016_TRAP_ROOT,
    Q_REL_GRID,
    baseline_roots_reproduce_exp016,
    particle_access_root,
    particle_attractive_potential,
    particle_environment_metrics,
    particle_trap_root,
    root_crossing_consistent,
)

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

EXPECTED_INTERFACE_CONTROL = 0.700000000
ROOT_ORDER_TOL = 1e-12
MEANINGFUL_ACCESS_RATIO = 1.50


def _monotonic_non_decreasing(values: tuple[float, ...]) -> bool:
    return all(b + ROOT_ORDER_TOL >= a for a, b in zip(values, values[1:]))


def main() -> None:
    if Q_REL_GRID != (0.60, 0.80, 1.00, 1.20, 1.40):
        raise SystemExit("preregistered particle grid changed")
    if IONIC_STRENGTH_GRID != (0.01, 0.03, 0.10, 0.30, 1.00, 3.00, 10.00):
        raise SystemExit("preregistered environment grid changed")
    if abs(MEANINGFUL_ACCESS_RATIO - 1.50) > 1e-12:
        raise SystemExit("preregistered effect threshold changed")

    interface_control = interface_nucleation_point(HARD_CONFIG, 180.0).external_root
    interface_control_failures = 0
    attraction_invariance_failures = 0
    screening_invariance_failures = 0
    matrix_points = 0

    regime_by_i: dict[float, set[str]] = {value: set() for value in IONIC_STRENGTH_GRID}

    print(
        "particle_environment_matrix: q_rel I kappa lambdaD_like "
        "barrier well_depth barrier_h well_h regime IC_C1_control"
    )

    for q_rel in Q_REL_GRID:
        for strength in IONIC_STRENGTH_GRID:
            metrics = particle_environment_metrics(q_rel, strength)
            matrix_points += 1
            regime_by_i[strength].add(metrics.regime)

            if abs(interface_control - EXPECTED_INTERFACE_CONTROL) > 1e-12:
                interface_control_failures += 1

            # Exact attraction negative control at representative separations.
            for h in (0.0, 0.18, 0.50, 1.0, 3.0):
                if particle_attractive_potential(h) != attractive_potential(h):
                    attraction_invariance_failures += 1

            # Screening coordinates must be particle-independent at fixed I.
            reference = particle_environment_metrics(1.0, strength)
            if (
                abs(metrics.kappa - reference.kappa) > 1e-15
                or abs(metrics.screening_length_like - reference.screening_length_like) > 1e-15
            ):
                screening_invariance_failures += 1

            print(
                f"q_rel={q_rel:.2f} I={strength:.2f} "
                f"kappa={metrics.kappa:.9f} lambdaD_like={metrics.screening_length_like:.9f} "
                f"barrier={metrics.barrier_height:.9f} well_depth={metrics.well_depth:.9f} "
                f"barrier_h={metrics.barrier_separation:.4f} well_h={metrics.well_separation:.4f} "
                f"regime={metrics.regime} IC_C1_control={interface_control:.9f}"
            )

    if matrix_points != 35:
        raise SystemExit(f"preregistered matrix point count changed: {matrix_points}")
    if not baseline_roots_reproduce_exp016():
        raise SystemExit("q_rel=1.0 no longer reproduces Experiment 016 roots")
    if interface_control_failures:
        raise SystemExit(f"interface control changed: {interface_control_failures}")
    if attraction_invariance_failures:
        raise SystemExit(f"attraction negative control changed: {attraction_invariance_failures}")
    if screening_invariance_failures:
        raise SystemExit(f"screening became particle-dependent: {screening_invariance_failures}")

    access_roots: list[float] = []
    trap_roots: list[float] = []
    valid_windows = 0
    root_consistency_failures = 0

    print("particle_roots: q_rel I_access I_trap valid_window access_consistent trap_consistent")
    for q_rel in Q_REL_GRID:
        access = particle_access_root(q_rel)
        trap = particle_trap_root(q_rel)
        if access is None or trap is None:
            print(
                f"q_rel={q_rel:.2f} I_access={access} I_trap={trap} "
                "valid_window=False access_consistent=False trap_consistent=False"
            )
            continue

        access_ok = root_crossing_consistent(access, q_rel, mechanism="access")
        trap_ok = root_crossing_consistent(trap, q_rel, mechanism="trap")
        root_consistency_failures += int(not access_ok) + int(not trap_ok)
        valid = access < trap
        valid_windows += int(valid)
        access_roots.append(access)
        trap_roots.append(trap)

        print(
            f"q_rel={q_rel:.2f} I_access={access:.9f} I_trap={trap:.9f} "
            f"valid_window={valid} access_consistent={access_ok} trap_consistent={trap_ok}"
        )

    if root_consistency_failures:
        raise SystemExit(f"particle-root sign checks failed: {root_consistency_failures}")

    finite_all = len(access_roots) == len(Q_REL_GRID) and len(trap_roots) == len(Q_REL_GRID)
    access_monotonic = finite_all and _monotonic_non_decreasing(tuple(access_roots))
    trap_monotonic = finite_all and _monotonic_non_decreasing(tuple(trap_roots))
    access_ratio = (
        access_roots[-1] / access_roots[0]
        if finite_all and access_roots[0] > 0.0
        else 0.0
    )

    selective_strengths = tuple(
        strength
        for strength in IONIC_STRENGTH_GRID
        if len(regime_by_i[strength]) >= 2
    )

    # Explicit baseline root reporting against the frozen Exp016 result.
    baseline_access = particle_access_root(1.0)
    baseline_trap = particle_trap_root(1.0)
    print(
        f"baseline_exp016 access_expected={EXP016_ACCESS_ROOT:.9f} "
        f"access_observed={baseline_access:.9f} trap_expected={EXP016_TRAP_ROOT:.9f} "
        f"trap_observed={baseline_trap:.9f}"
    )
    print(f"valid_windows={valid_windows}/5 finite_all={finite_all}")
    print(f"access_monotonic={access_monotonic} trap_monotonic={trap_monotonic}")
    print(f"access_ratio_high_to_low={access_ratio:.9f}")
    print(f"selective_environment_strengths={selective_strengths}")
    print(f"interface_control_failures={interface_control_failures}")
    print(f"attraction_invariance_failures={attraction_invariance_failures}")
    print(f"screening_invariance_failures={screening_invariance_failures}")
    print(f"root_consistency_failures={root_consistency_failures}")

    positive = (
        finite_all
        and valid_windows >= 4
        and access_monotonic
        and trap_monotonic
        and access_ratio >= MEANINGFUL_ACCESS_RATIO
        and bool(selective_strengths)
    )
    label = (
        "PARTICLE_PROPERTY_RESHAPES_ENVIRONMENT_WINDOW"
        if positive
        else "PARTICLE_PROPERTY_EFFECT_SMALL_OR_MIXED"
    )
    print(f"PREREGISTERED_RESULT={label}")


if __name__ == "__main__":
    main()
