"""Rectangular RC section in bending: elastic cracked-section analysis (units: mm, N, MPa).

Assumptions: plane sections, concrete carries no tension, linear-elastic steel and concrete,
modular ratio n = Es / Ec,eff. Compression steel, if given, uses (n - 1) to avoid counting the
displaced concrete twice.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .materials import ES, Concrete


def bar_area(diameter: float) -> float:
    return math.pi * diameter**2 / 4.0


@dataclass(frozen=True)
class RectangularSection:
    b: float                 # width (mm); use 1000 for a 1 m slab strip
    h: float                 # overall depth (mm)
    cover: float             # nominal cover to the tension bars (mm), "c" in eq. 7.11
    bar: float               # tension bar diameter (mm)
    spacing: float | None = None   # bar spacing (mm) -> As = b/s * area(bar)
    n_bars: int | None = None      # or a number of bars
    link: float = 0.0        # link/stirrup diameter inside the cover (mm), beams only
    As2: float = 0.0         # compression steel area (mm2)
    d2: float = 0.0          # depth to compression steel (mm)

    def __post_init__(self):
        if (self.spacing is None) == (self.n_bars is None):
            raise ValueError("give exactly one of spacing or n_bars")
        if min(self.b, self.h, self.bar) <= 0 or self.cover < 0:
            raise ValueError("dimensions must be positive")
        if self.d >= self.h or self.d <= 0:
            raise ValueError("effective depth outside the section")

    @property
    def As(self) -> float:  # noqa: N802
        if self.spacing is not None:
            return self.b / self.spacing * bar_area(self.bar)
        return self.n_bars * bar_area(self.bar)

    @property
    def c(self) -> float:
        """Cover to the longitudinal tension bars (eq. 7.11 'c')."""
        return self.cover + self.link

    @property
    def d(self) -> float:
        return self.h - self.cover - self.link - self.bar / 2.0

    @property
    def bar_spacing(self) -> float:
        """Centre-to-centre spacing of the tension bars."""
        if self.spacing is not None:
            return self.spacing
        if self.n_bars < 2:
            return math.inf
        return (self.b - 2 * self.c - self.bar) / (self.n_bars - 1)


@dataclass(frozen=True)
class CrackedSection:
    x: float        # neutral-axis depth (mm)
    I_cr: float     # cracked second moment of area, concrete units (mm4)
    n: float        # modular ratio Es / Ec,eff
    sigma_s: float  # tension steel stress (MPa)
    sigma_c: float  # extreme-fibre concrete compressive stress (MPa)


def analyse(section: RectangularSection, concrete: Concrete, moment_kNm: float) -> CrackedSection:
    """Cracked elastic analysis under a sagging moment (kNm) applied to the whole width b."""
    n = ES / concrete.Ec_eff
    b, d, As, As2, d2 = section.b, section.d, section.As, section.As2, section.d2
    # first moment about the neutral axis: b x^2/2 + (n-1) As2 (x - d2) - n As (d - x) = 0
    A = b / 2.0
    B = (n - 1.0) * As2 + n * As
    C = -((n - 1.0) * As2 * d2 + n * As * d)
    x = (-B + math.sqrt(B * B - 4 * A * C)) / (2 * A)
    I_cr = b * x**3 / 3.0 + n * As * (d - x) ** 2 + (n - 1.0) * As2 * (x - d2) ** 2
    M = abs(moment_kNm) * 1e6
    return CrackedSection(x=x, I_cr=I_cr, n=n, sigma_s=n * M * (d - x) / I_cr, sigma_c=M * x / I_cr)
