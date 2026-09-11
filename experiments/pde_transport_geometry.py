"""MorphoMatter Experiment 013: preregistered PDE transport geometry test."""
from __future__ import annotations

from math import isfinite

from morphomatter.boundary import config_signature, interpolate_config
from morphomatter.geometry_transport import GEOMETRY_MASKS
from morphomatter.nucleation import NucleationConfig
from morphomatter.pde_transport import (
    COUPLING_NUMERICAL_BOUNDS,
    DRIVE_NUMERICAL_BOUNDS,
    FIELD_MAX_ITERATIONS,
    FIELD_TOLERANCE,
    ROOT_TOLERANCE,
    TARGET_FRACTION,
    all_pde_fields,
    pde_c1_point,
    pde_c2_point,
)

LAMBDAS = (0.00, 0.20, 0.40, 0.60, 0.80, 1.00)
EFFECT_THRESHOLD = 0.05

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
    if value is None:
        return "NONE"
    if not isfinite(value):
        return "INF"
    return f"{value:.6f}"


def _delta(value: float, reference: float) -> float:
    if not isfinite(value) and not isfinite(reference):
        return 0.0
    if not isfinite(value):
        return float("inf")
    if not isfinite(reference):
        return float("-inf")
    return value - reference


def _shift_passes(delta: float) -> bool:
    return (not isfinite(delta)) or abs(delta) >= EFFECT_THRESHOLD - 1e-12


def main() -> None:
    if LAMBDAS != (0.00, 0.20, 0.40, 0.60, 0.80, 1.00):
        raise SystemExit("preregistered lambda grid changed")
    if tuple(GEOMETRY_MASKS) != (
        "slab",
        "cylinder_like",
        "pyramid_like",
        "concave_hourglass",
        "meandering_channel",
    ):
        raise SystemExit("preregistered geometry set changed")
    if abs(EFFECT_THRESHOLD - 0.05) > 1e-12:
        raise SystemExit("preregistered effect threshold changed")
    if abs(TARGET_FRACTION - 0.50) > 1e-12:
        raise SystemExit("preregistered target fraction changed")
    if FIELD_TOLERANCE != 1e-10 or FIELD_MAX_ITERATIONS != 20_000:
        raise SystemExit("preregistered PDE solver protocol changed")
    if DRIVE_NUMERICAL_BOUNDS != (0.0, 20.0):
        raise SystemExit("preregistered drive numerical bounds changed")
    if COUPLING_NUMERICAL_BOUNDS != (0.0, 30.0):
        raise SystemExit("preregistered coupling numerical bounds changed")
    if ROOT_TOLERANCE != 1e-6:
        raise SystemExit("preregistered root tolerance changed")
    if config_signature(interpolate_config(EASY_CONFIG, HARD_CONFIG, 0.0)) != config_signature(EASY_CONFIG):
        raise SystemExit("easy endpoint interpolation mismatch")
    if config_signature(interpolate_config(EASY_CONFIG, HARD_CONFIG, 1.0)) != config_signature(HARD_CONFIG):
        raise SystemExit("hard endpoint interpolation mismatch")

    fields = all_pde_fields()
    print(
        "pde_fields: geometry core source mean median min max iterations residual"
    )
    for field in fields:
        print(
            f"geometry={field.geometry} core={len(field.core_cells)} "
            f"source={len(field.source_cells)} mean={field.mean_core:.9f} "
            f"median={field.median_core:.9f} min={field.min_core:.9f} "
            f"max={field.max_core:.9f} iterations={field.iterations} "
            f"residual={field.residual:.3e}"
        )

    total_points = 0
    inconsistent = 0
    hard_points: dict[str, tuple[object, object]] = {}

    print(
        "pde_surface_map: lambda geometry C1_analytic C1_numeric C1_class "
        "C2_analytic C2_numeric C2_class"
    )
    for lam in LAMBDAS:
        config = interpolate_config(EASY_CONFIG, HARD_CONFIG, lam, seed=0)
        for field in fields:
            c1 = pde_c1_point(config, field)
            c2 = pde_c2_point(config, field)
            total_points += 2
            inconsistent += int(not c1.consistent) + int(not c2.consistent)
            print(
                f"lambda={lam:.2f} geometry={field.geometry} "
                f"C1_analytic={_fmt(c1.analytic_root)} C1_numeric={_fmt(c1.numerical_root)} "
                f"C1_class={c1.classification} "
                f"C2_analytic={_fmt(c2.analytic_root)} C2_numeric={_fmt(c2.numerical_root)} "
                f"C2_class={c2.classification}"
            )
            if abs(lam - 1.0) < 1e-12:
                hard_points[field.geometry] = (c1, c2)

    if total_points != 60:
        raise SystemExit(f"preregistered PDE surface point count changed: {total_points}")
    if inconsistent:
        raise SystemExit(f"PDE analytic/numerical mismatch: {inconsistent}")

    slab_c1, slab_c2 = hard_points["slab"]
    shifted: list[str] = []
    reachability_changes: list[str] = []

    for name in GEOMETRY_MASKS:
        if name == "slab":
            continue
        c1, c2 = hard_points[name]
        c1_delta = _delta(c1.analytic_root, slab_c1.analytic_root)
        c2_delta = _delta(c2.analytic_root, slab_c2.analytic_root)
        if _shift_passes(c1_delta) or _shift_passes(c2_delta):
            shifted.append(name)
        if c1.classification != slab_c1.classification or c2.classification != slab_c2.classification:
            reachability_changes.append(name)
        print(
            f"hard_shift geometry={name} C1_delta={_fmt(c1_delta)} C2_delta={_fmt(c2_delta)} "
            f"C1_class={c1.classification} C2_class={c2.classification}"
        )

    label = (
        "PDE_GEOMETRY_SHIFTS_TRANSITION_SURFACES"
        if len(shifted) >= 2
        else "PDE_GEOMETRY_EFFECT_SMALL"
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
