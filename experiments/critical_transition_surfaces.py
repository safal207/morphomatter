"""MorphoMatter Experiment 011: preregistered critical transition surfaces.

This experiment characterizes zero crossings of the frozen synthetic transition
law. It does not claim a physical phase diagram.
"""
from __future__ import annotations

from morphomatter.boundary import config_signature, interpolate_config
from morphomatter.critical_surfaces import (
    FRONTIER_NEIGHBOR_FRACTION,
    PROPAGATION_DRIVE,
    SCAN_STEP,
    commit_surface_point,
    frontier_surface_point,
    nucleation_surface_point,
)
from morphomatter.nucleation import NucleationConfig


LAMBDAS = (0.00, 0.20, 0.40, 0.60, 0.80, 1.00)
THRESHOLDS = (0.70, 0.75, 0.80, 0.85, 0.90)

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


def _fmt_scan(value: float | None) -> str:
    return "NONE" if value is None else f"{value:.2f}"


def main() -> None:
    if LAMBDAS != (0.00, 0.20, 0.40, 0.60, 0.80, 1.00):
        raise SystemExit("preregistered lambda grid changed")
    if THRESHOLDS != (0.70, 0.75, 0.80, 0.85, 0.90):
        raise SystemExit("preregistered threshold grid changed")
    if abs(FRONTIER_NEIGHBOR_FRACTION - 0.25) > 1e-12:
        raise SystemExit("preregistered frontier support changed")
    if abs(PROPAGATION_DRIVE - 0.12) > 1e-12:
        raise SystemExit("preregistered propagation drive changed")
    if abs(SCAN_STEP - 0.01) > 1e-12:
        raise SystemExit("preregistered scan step changed")
    if config_signature(interpolate_config(EASY_CONFIG, HARD_CONFIG, 0.0)) != config_signature(EASY_CONFIG):
        raise SystemExit("easy endpoint interpolation mismatch")
    if config_signature(interpolate_config(EASY_CONFIG, HARD_CONFIG, 1.0)) != config_signature(HARD_CONFIG):
        raise SystemExit("hard endpoint interpolation mismatch")

    total_points = 0
    inconsistent = 0
    reference_rows: list[tuple[float, object, object, object]] = []

    print(
        "critical_surface_map: "
        "lambda threshold "
        "nucleation_root nucleation_class nucleation_scan "
        "frontier_root frontier_class frontier_scan "
        "commit_root commit_class commit_scan"
    )

    for lam in LAMBDAS:
        config = interpolate_config(EASY_CONFIG, HARD_CONFIG, lam, seed=0)
        for threshold in THRESHOLDS:
            nucleation = nucleation_surface_point(config, threshold)
            frontier = frontier_surface_point(config, threshold)
            commit = commit_surface_point(config, threshold)
            points = (nucleation, frontier, commit)
            total_points += len(points)
            inconsistent += sum(not point.consistent for point in points)

            print(
                f"lambda={lam:.2f} threshold={threshold:.2f} "
                f"nucleation_root={nucleation.critical_value:.6f} "
                f"nucleation_class={nucleation.classification} "
                f"nucleation_scan={_fmt_scan(nucleation.scan_value)} "
                f"frontier_root={frontier.critical_value:.6f} "
                f"frontier_class={frontier.classification} "
                f"frontier_scan={_fmt_scan(frontier.scan_value)} "
                f"commit_root={commit.critical_value:.6f} "
                f"commit_class={commit.classification} "
                f"commit_scan={_fmt_scan(commit.scan_value)}"
            )

            if abs(threshold - 0.80) < 1e-12:
                reference_rows.append((lam, nucleation, frontier, commit))

    if total_points != 90:
        raise SystemExit(f"preregistered surface point count changed: {total_points}")
    if len(reference_rows) != 6:
        raise SystemExit("reference threshold slice count changed")

    print("reference_slice_threshold=0.80")
    for lam, nucleation, frontier, commit in reference_rows:
        print(
            f"lambda={lam:.2f} "
            f"C1_nucleation_drive={nucleation.critical_value:.6f} "
            f"C1_class={nucleation.classification} "
            f"C2_frontier_coupling={frontier.critical_value:.6f} "
            f"C2_class={frontier.classification} "
            f"C3_commit_coupling={commit.critical_value:.6f} "
            f"C3_class={commit.classification}"
        )

    print("reverse_surface=UNDEFINED_ONE_WAY_MODEL")
    print(f"surface_points={total_points} inconsistent_points={inconsistent}")

    label = (
        "TRANSITION_SURFACES_RESOLVED"
        if inconsistent == 0
        else "SURFACE_MODEL_INCONSISTENT"
    )
    print(f"PREREGISTERED_RESULT={label}")

    if inconsistent:
        raise SystemExit("critical-surface analytic/scan mismatch")


if __name__ == "__main__":
    main()
