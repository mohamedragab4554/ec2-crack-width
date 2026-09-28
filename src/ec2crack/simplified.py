"""Crack control without direct calculation, EN 1992-1-1 7.3.3 (Tables 7.2N and 7.3N)."""
from __future__ import annotations

import numpy as np

_STRESS_72 = [160, 200, 240, 280, 320, 360, 400, 450]
_PHI_MAX = {0.4: [40, 32, 20, 16, 12, 10, 8, 6], 0.3: [32, 25, 16, 12, 10, 8, 6, 5],
            0.2: [25, 16, 12, 8, 6, 5, 4, np.nan]}
_STRESS_73 = [160, 200, 240, 280, 320, 360]
_S_MAX = {0.4: [300, 300, 250, 200, 150, 100], 0.3: [300, 250, 200, 150, 100, 50],
          0.2: [200, 150, 100, 50, np.nan, np.nan]}


def _lookup(table: dict, stresses: list, wk: float, sigma_s: float) -> float:
    if wk not in table:
        raise ValueError("wk must be 0.2, 0.3 or 0.4 mm")
    if not stresses[0] <= sigma_s <= stresses[-1]:
        raise ValueError(f"sigma_s outside table range {stresses[0]}-{stresses[-1]} MPa")
    return float(np.interp(sigma_s, stresses, table[wk]))


def max_bar_diameter_table(sigma_s: float, wk: float) -> float:
    """Table 7.2N phi*_s (mm), linear interpolation between tabulated stresses."""
    return _lookup(_PHI_MAX, _STRESS_72, wk, sigma_s)


def max_bar_diameter_bending(sigma_s: float, wk: float, h: float, d: float, fct_eff: float,
                             kc: float = 0.4) -> float:
    """Eq. 7.6N modification for bending: phi_s = phi*_s (fct,eff/2.9) kc hcr / (2(h - d)), hcr = h/2."""
    return max_bar_diameter_table(sigma_s, wk) * (fct_eff / 2.9) * kc * (h / 2.0) / (2.0 * (h - d))


def max_bar_spacing(sigma_s: float, wk: float) -> float:
    """Table 7.3N maximum bar spacing (mm) for cracks caused mainly by loading."""
    return _lookup(_S_MAX, _STRESS_73, wk, sigma_s)


def as_min(b: float, h: float, fct_eff: float, sigma_s: float, kc: float = 0.4) -> float:
    """Eq. 7.1 minimum area (mm2) for a rectangular section in bending (Act = b h / 2)."""
    k = 1.0 if h <= 300 else 0.65 if h >= 800 else 1.0 - 0.35 * (h - 300) / 500
    return kc * k * fct_eff * (b * h / 2.0) / sigma_s
