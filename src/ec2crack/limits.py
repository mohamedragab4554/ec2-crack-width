"""Crack-width limits: EN 1992-1-1 Table 7.1N and EN 1992-3 7.3.1 (tightness classes)."""
from __future__ import annotations

RC_QUASI_PERMANENT = {"X0": 0.4, "XC1": 0.4, "XC2": 0.3, "XC3": 0.3, "XC4": 0.3,
                      "XD1": 0.3, "XD2": 0.3, "XS1": 0.3, "XS2": 0.3, "XS3": 0.3}


def w_max_table_7_1n(exposure: str) -> float:
    """Recommended w_max (mm) for reinforced and unbonded prestressed members under the
    quasi-permanent combination. For X0/XC1 the 0.4 mm value is for appearance only (Note 1).
    National Annexes may set different values."""
    key = exposure.upper().strip()
    if key not in RC_QUASI_PERMANENT:
        raise ValueError(f"unknown exposure class {exposure!r}")
    return RC_QUASI_PERMANENT[key]


def wk1_tightness_class_1(hydrostatic_head_m: float, wall_thickness_m: float) -> float:
    """EN 1992-3 7.3.1(111): wk1 = 0.2 mm for hD/h <= 5 down to 0.05 mm for hD/h >= 35, linear between.

    Applies to cracks expected to pass through the full thickness of a liquid-retaining element.
    """
    if hydrostatic_head_m < 0 or wall_thickness_m <= 0:
        raise ValueError("invalid head or thickness")
    ratio = hydrostatic_head_m / wall_thickness_m
    if ratio <= 5:
        return 0.2
    if ratio >= 35:
        return 0.05
    return 0.2 - 0.15 * (ratio - 5.0) / 30.0


TIGHTNESS_CLASSES = {
    0: "Some leakage acceptable: use EN 1992-1-1 7.3.1 (Table 7.1N).",
    1: "Leakage limited to a small amount: through-cracks limited to wk1 (depends on hD/h).",
    2: "Leakage minimal: cracks passing through the full section should be avoided.",
    3: "No leakage: special measures (liners or prestress) needed.",
}
