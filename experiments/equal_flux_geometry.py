"""MorphoMatter Experiment 014: preregistered equal-total-flux geometry test."""
from __future__ import annotations

from morphomatter.boundary import config_signature, interpolate_config
from morphomatter.equal_flux_transport import (
    Q_TOTAL,
    TARGET_FRACTION,
    all_equal_flux_fields,
    equal_flux_c1_point,
    equal_flux_c2_point,
)
from morphomatter.geometry_transport import (
    FRONTIER_SUPPORT,
    GEOMETRY_MASKS,
    PROPAGATION_DRIVE,
    THRESHOLD_SCALE,
)
from morphomatter.nucleation import NucleationConfig


LAMBDAS = (0.00, 0.20, 0.40, 0.60, 0.80, 1.00)
RELATIVE_SHIFT_THRESHOLD = 0.10

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
    if abs(Q_TOTAL - 1.0) > 1e-12:
        raise SystemExit("preregistered total flux changed")
    if abs(TARGET_FRACTION - 0.50) > 1e-12:
        raise SystemExit("preregistered target fraction changed")
    if abs(THRESHOLD_SCALE - 0.80) > 1e-12:
        raise SystemExit("preregistered threshold changed")
    if abs(FRONTIER_SUPPORT - 0.25) > 1e-12:
        raise SystemExit("preregistered frontier support changed")
    if abs(PROPAGATION_DRIVE - 0.12) > 1e-12:
        raise SystemExit("preregistered propagation drive changed")
    if abs(RELATIVE_SHIFT_THRESHOLD - 0.10) > 1e-12:
        raise SystemExit("preregistered relative shift threshold changed")
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

    fields = all_equal_flux_fields()
    fields_by_name = {field.geometry: field for field in fields}

    print(
        "equal_flux_fields: geometry source_count injection_per_source total_injection "
        "sink_flux eval_count mean median min max iterations residual"
    )
    for field in fields:
        print(
            f"geometry={field.geometry} source_count={len(field.source_cells)} "
            f"injection_per_source={field.injection_per_source:.9f} "
            f"total_injection={field.total_injection:.9f} sink_flux={field.sink_flux:.9f} "
            f"eval_count={len(field.evaluation_cells)} "
            f"mean={field.mean_evaluation:.9f} median={field.median_evaluation:.9f} "
            f"min={field.min_evaluation:.9f} max={field.max_evaluation:.9f} "
            f"iterations={field.iterations} residual={field.residual:.3e}"
        )

    total_points = 0
    inconsistent = 0
    hard_points: dict[str, tuple[object, object]] = {}

    print(
        "equal_flux_surface_map: lambda geometry "
        "EF_C1_analytic EF_C1_numeric EF_C1_class "
        "EF_C2_analytic EF_C2_numeric EF_C2_class"
    )

    for lam in LAMBDAS:
        config = interpolate_config(EASY_CONFIG, HARD_CONFIG, lam, seed=0)
        for name in GEOMETRY_MASKS:
            field = fields_by_name[name]
            c1 = equal_flux_c1_point(config, field)
            c2 = equal_flux_c2_point(config, field)
            total_points += 2
            inconsistent += int(not c1.consistent) + int(not c2.consistent)
            print(
                f"lambda={lam:.2f} geometry={name} "
                f"EF_C1_analytic={c1.analytic_root:.6f} "
                f"EF_C1_numeric={_fmt(c1.numerical_root)} EF_C1_class={c1.classification} "
                f"EF_C2_analytic={c2.analytic_root:.6f} "
                f"EF_C2_numeric={_fmt(c2.numerical_root)} EF_C2_class={c2.classification}"
            )
            if abs(lam - 1.0) < 1e-12:
                hard_points[name] = (c1, c2)

    if total_points != 60:
        raise SystemExit(f"preregistered equal-flux surface count changed: {total_points}")
    if inconsistent:
        raise SystemExit(f"equal-flux analytic/numerical mismatch: {inconsistent}")

    slab_c1, slab_c2 = hard_points["slab"]
    if slab_c1.analytic_root <= 0 or slab_c2.analytic_root <= 0:
        raise SystemExit("slab hard-endpoint roots must be positive for relative comparison")

    shifted: list[str] = []
    reachability_changes: list[str] = []
    for name in GEOMETRY_MASKS:
        if name == "slab":
            continue
        c1, c2 = hard_points[name]
        c1_ratio = c1.analytic_root / slab_c1.analytic_root
        c2_ratio = c2.analytic_root / slab_c2.analytic_root
        c1_relative_shift = abs(c1_ratio - 1.0)
        c2_relative_shift = abs(c2_ratio - 1.0)
        if (
            c1_relative_shift >= RELATIVE_SHIFT_THRESHOLD - 1e-12
            or c2_relative_shift >= RELATIVE_SHIFT_THRESHOLD - 1e-12
        ):
            shifted.append(name)
        if c1.classification != slab_c1.classification or c2.classification != slab_c2.classification:
            reachability_changes.append(name)
        print(
            f"hard_shift geometry={name} "
            f"C1_ratio={c1_ratio:.6f} C1_relative_shift={c1_relative_shift:.6f} "
            f"C2_ratio={c2_ratio:.6f} C2_relative_shift={c2_relative_shift:.6f} "
            f"C1_class={c1.classification} C2_class={c2.classification}"
        )

    label = (
        "EQUAL_FLUX_GEOMETRY_EFFECT_PERSISTS"
        if len(shifted) >= 2
        else "EQUAL_FLUX_GEOMETRY_EFFECT_COLLAPSES"
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
