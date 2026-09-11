"""MorphoMatter Experiment 012: preregistered geometry-shaped transition landscape.

Geometry changes only the delivered global conditions through a frozen
transport/confinement surrogate. The local transition law is unchanged.
"""
from __future__ import annotations

from morphomatter.boundary import config_signature, interpolate_config
from morphomatter.geometry_transport import (
    GEOMETRY_MASKS,
    THRESHOLD_SCALE,
    all_geometry_metrics,
    geometry_frontier_surface_point,
    geometry_nucleation_surface_point,
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
    return "NONE" if value is None else f"{value:.3f}"


def main() -> None:
    if LAMBDAS != (0.00, 0.20, 0.40, 0.60, 0.80, 1.00):
        raise SystemExit("preregistered lambda grid changed")
    if abs(THRESHOLD_SCALE - 0.80) > 1e-12:
        raise SystemExit("preregistered threshold slice changed")
    if tuple(GEOMETRY_MASKS) != (
        "slab",
        "cylinder_like",
        "pyramid_like",
        "concave_hourglass",
        "meandering_channel",
    ):
        raise SystemExit("preregistered geometry set changed")
    if config_signature(interpolate_config(EASY_CONFIG, HARD_CONFIG, 0.0)) != config_signature(EASY_CONFIG):
        raise SystemExit("easy endpoint interpolation mismatch")
    if config_signature(interpolate_config(EASY_CONFIG, HARD_CONFIG, 1.0)) != config_signature(HARD_CONFIG):
        raise SystemExit("hard endpoint interpolation mismatch")

    metrics_list = all_geometry_metrics()
    metrics_by_name = {metrics.name: metrics for metrics in metrics_list}
    print("geometry_metrics: name area boundary mean_wall_distance mean_connectivity drive_gain coupling_gain")
    for metrics in metrics_list:
        print(
            f"geometry={metrics.name} area={metrics.area} boundary={metrics.boundary_cells} "
            f"mean_wall_distance={metrics.mean_wall_distance:.6f} "
            f"mean_connectivity={metrics.mean_connectivity:.6f} "
            f"drive_gain={metrics.drive_gain:.6f} coupling_gain={metrics.coupling_gain:.6f}"
        )

    total_points = 0
    inconsistent = 0
    hard_points: dict[str, tuple[object, object]] = {}

    print("geometry_surface_map: lambda geometry C1_root C1_class C1_scan C2_root C2_class C2_scan")
    for lam in LAMBDAS:
        config = interpolate_config(EASY_CONFIG, HARD_CONFIG, lam, seed=0)
        for metrics in metrics_list:
            c1 = geometry_nucleation_surface_point(config, metrics)
            c2 = geometry_frontier_surface_point(config, metrics)
            total_points += 2
            inconsistent += int(not c1.consistent) + int(not c2.consistent)
            print(
                f"lambda={lam:.2f} geometry={metrics.name} "
                f"C1_root={c1.critical_external_value:.6f} C1_class={c1.classification} C1_scan={_fmt(c1.scan_value)} "
                f"C2_root={c2.critical_external_value:.6f} C2_class={c2.classification} C2_scan={_fmt(c2.scan_value)}"
            )
            if abs(lam - 1.0) < 1e-12:
                hard_points[metrics.name] = (c1, c2)

    if total_points != 60:
        raise SystemExit(f"preregistered geometry surface count changed: {total_points}")
    if inconsistent:
        raise SystemExit(f"geometry surface analytic/scan mismatch: {inconsistent}")

    slab_c1, slab_c2 = hard_points["slab"]
    shifted: list[str] = []
    reachability_changes: list[str] = []
    for name in GEOMETRY_MASKS:
        if name == "slab":
            continue
        c1, c2 = hard_points[name]
        c1_shift = c1.critical_external_value - slab_c1.critical_external_value
        c2_shift = c2.critical_external_value - slab_c2.critical_external_value
        if abs(c1_shift) >= 0.05 - 1e-12 or abs(c2_shift) >= 0.05 - 1e-12:
            shifted.append(name)
        if c1.classification != slab_c1.classification or c2.classification != slab_c2.classification:
            reachability_changes.append(name)
        print(
            f"hard_shift geometry={name} C1_delta={c1_shift:.6f} C2_delta={c2_shift:.6f} "
            f"C1_class={c1.classification} C2_class={c2.classification}"
        )

    label = (
        "GEOMETRY_SHIFTS_TRANSITION_SURFACES"
        if len(shifted) >= 2
        else "GEOMETRY_EFFECT_SMALL_IN_SURROGATE"
    )
    print(f"surface_points={total_points} inconsistent_points={inconsistent}")
    print(f"shifted_geometries={','.join(shifted) if shifted else 'NONE'}")
    print(
        "reachability_changes="
        + (",".join(reachability_changes) if reachability_changes else "NONE")
    )
    print(f"PREREGISTERED_RESULT={label}")


if __name__ == "__main__":
    main()
