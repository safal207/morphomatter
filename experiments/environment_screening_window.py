"""MorphoMatter Experiment 016: environment chemistry / screened interactions."""
from __future__ import annotations

from morphomatter.environment_screening import (
    B_ACCESS,
    IONIC_STRENGTH_GRID,
    W_TRAP,
    access_root,
    all_grid_metrics,
    crossing_is_consistent,
    interaction_metrics,
    trap_root,
)
from morphomatter.interface_chemistry import external_interface_c1
from morphomatter.nucleation import NucleationConfig


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


def _fmt(value: float | None) -> str:
    return "NONE" if value is None else f"{value:.9f}"


def _nonincreasing(values: list[float], tolerance: float = 1e-12) -> bool:
    return all(right <= left + tolerance for left, right in zip(values, values[1:]))


def _nondecreasing(values: list[float], tolerance: float = 1e-12) -> bool:
    return all(right + tolerance >= left for left, right in zip(values, values[1:]))


def main() -> None:
    if IONIC_STRENGTH_GRID != (0.01, 0.03, 0.10, 0.30, 1.00, 3.00, 10.00):
        raise SystemExit("preregistered ionic-strength grid changed")

    metrics = list(all_grid_metrics())
    barriers = [point.barrier_height for point in metrics]
    wells = [point.well_depth for point in metrics]

    barrier_monotonic = _nonincreasing(barriers)
    well_monotonic = _nondecreasing(wells)

    i_access = access_root()
    i_trap = trap_root()

    access_consistent = crossing_is_consistent(
        i_access,
        lambda strength: interaction_metrics(strength).barrier_height - B_ACCESS,
        increasing=False,
    )
    trap_consistent = crossing_is_consistent(
        i_trap,
        lambda strength: interaction_metrics(strength).well_depth - W_TRAP,
        increasing=True,
    )

    controls = [external_interface_c1(HARD_CONFIG, 180.0) for _ in IONIC_STRENGTH_GRID]
    control_failures = sum(abs(value - 0.700000000) > 1e-12 for value in controls)

    print(
        "environment_screening_map: I kappa lambdaD_like barrier well_depth "
        "barrier_h well_h regime IC_C1_control"
    )
    for point, control in zip(metrics, controls):
        print(
            f"I={point.ionic_strength_like:.2f} "
            f"kappa={point.kappa:.9f} lambdaD_like={point.screening_length_like:.9f} "
            f"barrier={point.barrier_height:.9f} well_depth={point.well_depth:.9f} "
            f"barrier_h={point.barrier_separation:.4f} well_h={point.well_separation:.4f} "
            f"regime={point.regime} IC_C1_control={control:.9f}"
        )

    reversible_strengths = [
        point.ionic_strength_like
        for point in metrics
        if point.regime == "REVERSIBLE_ASSEMBLY"
    ]
    trapped_strengths = [
        point.ionic_strength_like
        for point in metrics
        if point.regime == "KINETIC_TRAP_RISK"
    ]
    higher_trap_exists = bool(
        reversible_strengths
        and any(value > max(reversible_strengths) for value in trapped_strengths)
    )
    roots_ordered = (
        i_access is not None
        and i_trap is not None
        and float(i_access) < float(i_trap)
    )

    if not access_consistent or not trap_consistent:
        raise SystemExit(
            f"continuous crossing consistency failure: access={access_consistent} trap={trap_consistent}"
        )
    if control_failures:
        raise SystemExit(f"interface negative control changed: {control_failures}")

    positive = (
        barrier_monotonic
        and well_monotonic
        and roots_ordered
        and bool(reversible_strengths)
        and higher_trap_exists
        and control_failures == 0
    )
    label = (
        "SCREENING_CREATES_REVERSIBLE_ASSEMBLY_WINDOW"
        if positive
        else "SCREENING_WINDOW_NOT_RESOLVED"
    )

    print(f"barrier_monotonic={barrier_monotonic}")
    print(f"well_monotonic={well_monotonic}")
    print(
        f"I_access={_fmt(i_access)} I_trap={_fmt(i_trap)} "
        f"roots_ordered={roots_ordered} access_consistent={access_consistent} trap_consistent={trap_consistent}"
    )
    print(f"reversible_strengths={tuple(reversible_strengths)}")
    print(f"trapped_strengths={tuple(trapped_strengths)} higher_trap_exists={higher_trap_exists}")
    print(f"interface_control_failures={control_failures}")
    print(f"PREREGISTERED_RESULT={label}")


if __name__ == "__main__":
    main()
