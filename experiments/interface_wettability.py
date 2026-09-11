"""MorphoMatter Experiment 015: interface chemistry / wettability surrogate."""
from __future__ import annotations

from math import isfinite

from morphomatter.boundary import config_signature, interpolate_config
from morphomatter.equal_flux_transport import solve_equal_flux_field
from morphomatter.interface_wettability import (
    BULK_INVARIANCE_TOLERANCE,
    CONTACT_ANGLES_DEG,
    bulk_c1_point,
    heterogeneous_shape_factor,
    interface_c1_point,
    interface_c2_point,
    slab_interface_partition,
)
from morphomatter.nucleation import NucleationConfig


LAMBDAS = (0.00, 0.20, 0.40, 0.60, 0.80, 1.00)
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


def _fmt(value: float | None) -> str:
    return "NONE" if value is None else f"{value:.6f}"


def main() -> None:
    if LAMBDAS != (0.00, 0.20, 0.40, 0.60, 0.80, 1.00):
        raise SystemExit("preregistered lambda grid changed")
    if CONTACT_ANGLES_DEG != (30, 60, 90, 120, 150, 180):
        raise SystemExit("preregistered contact-angle grid changed")
    if config_signature(interpolate_config(EASY_CONFIG, HARD_CONFIG, 0.0)) != config_signature(EASY_CONFIG):
        raise SystemExit("easy endpoint interpolation mismatch")
    if config_signature(interpolate_config(EASY_CONFIG, HARD_CONFIG, 1.0)) != config_signature(HARD_CONFIG):
        raise SystemExit("hard endpoint interpolation mismatch")

    field = solve_equal_flux_field("slab")
    partition = slab_interface_partition()
    if set(partition.interface_cells) & set(partition.bulk_cells):
        raise SystemExit("interface/bulk partition overlaps")
    if set(partition.interface_cells) | set(partition.bulk_cells) != set(field.evaluation_cells):
        raise SystemExit("interface/bulk partition does not cover evaluation cells")

    print(
        "interface_protocol: "
        f"geometry=slab interface_cells={len(partition.interface_cells)} "
        f"bulk_cells={len(partition.bulk_cells)} source_cells={len(field.source_cells)} "
        f"field_mean={field.mean_evaluation:.9f} field_median={field.median_evaluation:.9f}"
    )
    print("shape_factors: theta factor")
    for theta in CONTACT_ANGLES_DEG:
        print(f"theta={theta} factor={heterogeneous_shape_factor(theta):.9f}")

    total_points = 0
    inconsistent = 0
    hard_c1: dict[int, float] = {}
    hard_c2: dict[int, float] = {}
    hard_bulk: dict[int, float] = {}

    print(
        "interface_surface_map: lambda theta factor "
        "IC_C1_analytic IC_C1_numeric IC_C2_analytic IC_C2_numeric "
        "BULK_C1_analytic BULK_C1_numeric"
    )
    for lam in LAMBDAS:
        config = interpolate_config(EASY_CONFIG, HARD_CONFIG, lam, seed=0)
        for theta in CONTACT_ANGLES_DEG:
            c1 = interface_c1_point(config, field, partition, theta)
            c2 = interface_c2_point(config, field, partition, theta)
            bulk = bulk_c1_point(config, field, partition, theta)
            total_points += 3
            inconsistent += int(not c1.consistent) + int(not c2.consistent) + int(not bulk.consistent)
            print(
                f"lambda={lam:.2f} theta={theta} "
                f"factor={heterogeneous_shape_factor(theta):.9f} "
                f"IC_C1_analytic={c1.analytic_root:.6f} IC_C1_numeric={_fmt(c1.numerical_root)} "
                f"IC_C2_analytic={c2.analytic_root:.6f} IC_C2_numeric={_fmt(c2.numerical_root)} "
                f"BULK_C1_analytic={bulk.analytic_root:.6f} BULK_C1_numeric={_fmt(bulk.numerical_root)}"
            )
            if abs(lam - 1.0) < 1e-12:
                hard_c1[theta] = c1.analytic_root
                hard_c2[theta] = c2.analytic_root
                hard_bulk[theta] = bulk.analytic_root

    if total_points != 108:
        raise SystemExit(f"preregistered surface count changed: {total_points}")
    if inconsistent:
        raise SystemExit(f"interface analytic/numerical mismatch: {inconsistent}")

    c1_values = [hard_c1[theta] for theta in CONTACT_ANGLES_DEG]
    c2_values = [hard_c2[theta] for theta in CONTACT_ANGLES_DEG]
    bulk_values = [hard_bulk[theta] for theta in CONTACT_ANGLES_DEG]

    if not all(isfinite(value) for value in c1_values + c2_values + bulk_values):
        raise SystemExit("hard endpoint unexpectedly produced non-finite root")

    c1_180 = hard_c1[180]
    c1_30 = hard_c1[30]
    reduction = 1.0 if c1_180 == 0.0 and c1_30 == 0.0 else (
        (c1_180 - c1_30) / c1_180 if c1_180 > 0.0 else 0.0
    )
    monotonic = all(a <= b + 1e-12 for a, b in zip(c1_values, c1_values[1:]))
    bulk_span = max(bulk_values) - min(bulk_values)

    print("hard_endpoint: theta IC_C1 IC_C2 BULK_C1")
    for theta in CONTACT_ANGLES_DEG:
        print(
            f"theta={theta} IC_C1={hard_c1[theta]:.6f} "
            f"IC_C2={hard_c2[theta]:.6f} BULK_C1={hard_bulk[theta]:.6f}"
        )
    print(f"hard_c1_reduction_30_vs_180={reduction:.9f}")
    print(f"hard_c1_monotonic={monotonic}")
    print(f"hard_bulk_c1_span={bulk_span:.12f}")
    print(f"surface_points={total_points} inconsistent_points={inconsistent}")

    positive = (
        reduction >= 0.20 - 1e-12
        and monotonic
        and bulk_span <= BULK_INVARIANCE_TOLERANCE
    )
    label = (
        "INTERFACE_WETTABILITY_SHIFTS_NUCLEATION"
        if positive
        else "INTERFACE_WETTABILITY_EFFECT_SMALL_OR_NONMONOTONIC"
    )
    print(f"PREREGISTERED_RESULT={label}")


if __name__ == "__main__":
    main()
