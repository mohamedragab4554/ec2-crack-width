"""Design helpers: largest bar spacing that satisfies a crack-width limit."""
from __future__ import annotations

from dataclasses import replace

from .crack import crack_width_section
from .materials import Concrete
from .section import RectangularSection

DEFAULT_SPACINGS = tuple(range(50, 405, 5))


def max_spacing_for_limit(section: RectangularSection, concrete: Concrete, moment_kNm: float, limit_mm: float,
                          spacings=DEFAULT_SPACINGS) -> float | None:
    """Largest spacing (mm) such that **every** spacing up to it satisfies wk <= limit.

    EN 1992-1-1 eqs. 7.11 and 7.14 are not continuous: just beyond s = 5(c + phi/2) the far-spacing
    rule can give a *smaller* wk than closer spacing. Scanning upwards and stopping at the first
    failure prevents the search from recommending a wider spacing because of that discontinuity.
    Returns None if even the smallest spacing fails.
    """
    best = None
    for s in sorted(spacings):
        trial = replace(section, spacing=float(s), n_bars=None)
        if crack_width_section(trial, concrete, moment_kNm).wk > limit_mm:
            break
        best = float(s)
    return best
