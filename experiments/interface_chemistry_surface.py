"""MorphoMatter Experiment 015: interface-affinity nucleation surface."""
from __future__ import annotations

from morphomatter.boundary import interpolate_config
from morphomatter.critical_surfaces import (
    critical_frontier_coupling,
    scan_frontier_onset,
)
from morphomatter.interface_chemistry import (
    CONTACT_ANGLES_DEG,
    THRESHOLD_SCALE,
    interface_nucleation_point,
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
    if CONTACT_ANGLES_DEG != (30.0, 60.0, 90.0, 120.0, 150.0, 180.0):
        raise SystemExit("preregistered interface-angle grid changed")
    if abs(THRESHOLD_SCALE - 0.80) > 1e-12:
        raise SystemExit("preregistered threshold scale changed")

    total_points = 0
    inconsistent = 0
    monotonic_failures = 0
    frontier_invariance_failures = 0
    hard_roots: dict[float, float] = {}

    print("interface_surface_map: lambda theta factor C1_raw C1_external C1_class C1_scan C2_root C2_scan")

    for lam in LAMBDAS:
        config = interpolate_config(EASY_CONFIG, HARD_CONFIG, lam, seed=0)
        c1_points = [
            interface_nucleation_point(config, theta)
            for theta in CONTACT_ANGLES_DEG
        ]
        roots = [point.external_root for point in c1_points]
        if roots != sorted(roots):
            monotonic_failures += 1

        c2_root = critical_frontier_coupling(config, THRESHOLD_SCALE)
        c2_scan = scan_frontier_onset(config, THRESHOLD_SCALE)
        repeated_c2 = [
            critical_frontier_coupling(config, THRESHOLD_SCALE)
            for _theta in CONTACT_ANGLES_DEG
        ]
        if not all(abs(value - c2_root) <= 1e-12 for value in repeated_c2):
            frontier_invariance_failures += 1

        for point in c1_points:
            total_points += 1
            inconsistent += int(not point.consistent)
            print(
                f"lambda={lam:.2f} theta={point.theta_deg:.0f} "
                f"factor={point.shape_factor:.9f} "
                f"C1_raw={point.raw_root:.9f} C1_external={point.external_root:.9f} "
                f"C1_class={point.classification} C1_scan={_fmt(point.scan_value)} "
                f"C2_root={c2_root:.9f} C2_scan={_fmt(c2_scan)}"
            )
            if abs(lam - 1.0) < 1e-12:
                hard_roots[point.theta_deg] = point.external_root

    if total_points != 36:
        raise SystemExit(f"preregistered interface point count changed: {total_points}")
    if inconsistent:
        raise SystemExit(f"interface analytic/scan mismatch: {inconsistent}")
    if frontier_invariance_failures:
        raise SystemExit(f"frontier negative control changed: {frontier_invariance_failures}")

    hard_90 = hard_roots[90.0]
    hard_180 = hard_roots[180.0]
    hard_ratio = 0.0 if hard_180 <= 0.0 else hard_90 / hard_180
    meaningful_shift = hard_90 <= 0.75 * hard_180 + 1e-12

    label = (
        "INTERFACE_AFFINITY_SHIFTS_NUCLEATION_SURFACE"
        if monotonic_failures == 0
        and meaningful_shift
        and frontier_invariance_failures == 0
        else "INTERFACE_AFFINITY_EFFECT_SMALL_OR_MIXED"
    )

    print(f"surface_points={total_points} inconsistent_points={inconsistent}")
    print(f"monotonic_failures={monotonic_failures}")
    print(f"frontier_invariance_failures={frontier_invariance_failures}")
    print(
        f"hard_endpoint theta90_C1={hard_90:.9f} theta180_C1={hard_180:.9f} "
        f"ratio_90_to_180={hard_ratio:.9f} meaningful_shift={meaningful_shift}"
    )
    print(f"PREREGISTERED_RESULT={label}")


if __name__ == "__main__":
    main()
