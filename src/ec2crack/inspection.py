"""Compare crack widths measured on site (or by a vision pipeline) with design limits.

This is triage support, not an assessment: a measured surface width is compared with the
serviceability limit and with the design prediction wk; any exceedance is referred to an engineer.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass


@dataclass(frozen=True)
class Observation:
    crack_id: str
    width_mm: float
    ratio_to_limit: float
    ratio_to_predicted: float | None
    flag: str


def assess(widths: dict[str, float], limit_mm: float, predicted_wk_mm: float | None = None,
           review_fraction: float = 0.8) -> list[Observation]:
    """Flag each observed width: 'exceeds limit', 'review' (>= review_fraction of limit) or 'within limit'."""
    if limit_mm <= 0:
        raise ValueError("limit must be positive")
    out = []
    for cid, w in widths.items():
        r = w / limit_mm
        flag = "exceeds limit" if r > 1 else "review" if r >= review_fraction else "within limit"
        out.append(Observation(cid, w, r, None if not predicted_wk_mm else w / predicted_wk_mm, flag))
    return sorted(out, key=lambda o: -o.ratio_to_limit)


def read_widths(path: str, id_col: str = "image_id", width_col: str = "measured_width_mm") -> dict[str, float]:
    """Read a CSV of measured widths (default columns match water-tank-crack-digital-twin output)."""
    with open(path, newline="", encoding="utf-8") as f:
        return {r[id_col]: float(r[width_col]) for r in csv.DictReader(f) if r.get(width_col)}
