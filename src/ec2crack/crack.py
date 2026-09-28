"""Crack width, EN 1992-1-1:2004 7.3.4 (eqs. 7.8-7.14) - units mm, MPa."""
from __future__ import annotations

from dataclasses import asdict, dataclass

from .materials import ES, Concrete
from .section import RectangularSection, analyse

K3, K4 = 3.4, 0.425  # recommended values, 7.3.4(3) Note


@dataclass(frozen=True)
class CrackWidthResult:
    sigma_s: float
    x: float
    hc_eff: float
    Ac_eff: float
    rho_p_eff: float
    alpha_e: float
    eps_sm_minus_eps_cm: float
    eps_governed_by_minimum: bool
    sr_max: float
    sr_max_rule: str
    wk: float

    def as_dict(self) -> dict:
        return asdict(self)


def hc_eff(h: float, d: float, x: float, tension: bool = False) -> float:
    """Effective tension depth, 7.3.2(3) / Figure 7.1."""
    if tension:
        return min(2.5 * (h - d), h / 2.0)
    return min(2.5 * (h - d), (h - x) / 3.0, h / 2.0)


def eps_sm_minus_eps_cm(sigma_s: float, fct_eff: float, rho_p_eff: float, alpha_e: float,
                        kt: float) -> tuple[float, bool]:
    """Eq. 7.9 with the 0.6 sigma_s/Es lower bound. Returns (value, lower bound governs)."""
    main = (sigma_s - kt * fct_eff / rho_p_eff * (1.0 + alpha_e * rho_p_eff)) / ES
    floor = 0.6 * sigma_s / ES
    return (floor, True) if main < floor else (main, False)


def sr_max(c: float, bar: float, rho_p_eff: float, spacing: float, h: float, x: float,
           k1: float = 0.8, k2: float = 0.5) -> tuple[float, str]:
    """Maximum crack spacing: eq. 7.11 when spacing <= 5(c + bar/2), else eq. 7.14."""
    if spacing <= 5.0 * (c + bar / 2.0):
        return K3 * c + k1 * k2 * K4 * bar / rho_p_eff, "7.11"
    return 1.3 * (h - x), "7.14"


def crack_width(*, sigma_s: float, h: float, d: float, x: float, b: float, As: float, c: float, bar: float,
                spacing: float, fct_eff: float, Ecm: float, long_term: bool = True, high_bond: bool = True,
                tension: bool = False) -> CrackWidthResult:
    """wk = sr,max (eps_sm - eps_cm), eq. 7.8, from a known steel stress."""
    if As <= 0 or sigma_s < 0:
        raise ValueError("As must be positive and sigma_s non-negative")
    hce = hc_eff(h, d, x, tension)
    Ac_eff = b * hce
    rho = As / Ac_eff
    alpha_e = ES / Ecm
    kt = 0.4 if long_term else 0.6
    eps, floor = eps_sm_minus_eps_cm(sigma_s, fct_eff, rho, alpha_e, kt)
    k1 = 0.8 if high_bond else 1.6
    k2 = 1.0 if tension else 0.5
    s, rule = sr_max(c, bar, rho, spacing, h, 0.0 if tension else x, k1, k2)
    return CrackWidthResult(sigma_s, x, hce, Ac_eff, rho, alpha_e, eps, floor, s, rule, s * eps)


def crack_width_section(section: RectangularSection, concrete: Concrete, moment_kNm: float, *,
                        long_term: bool = True, fct_eff: float | None = None) -> CrackWidthResult:
    """Crack width of a rectangular section under the quasi-permanent (or frequent) moment."""
    cs = analyse(section, concrete, moment_kNm)
    return crack_width(sigma_s=cs.sigma_s, h=section.h, d=section.d, x=cs.x, b=section.b, As=section.As,
                       c=section.c, bar=section.bar, spacing=section.bar_spacing,
                       fct_eff=concrete.fctm if fct_eff is None else fct_eff, Ecm=concrete.Ecm,
                       long_term=long_term)


def equivalent_diameter(bars: dict[float, int]) -> float:
    """Eq. 7.12: phi_eq = sum(n phi^2) / sum(n phi) for mixed bar sizes {diameter: count}."""
    num = sum(n * d * d for d, n in bars.items())
    den = sum(n * d for d, n in bars.items())
    if den <= 0:
        raise ValueError("no bars")
    return num / den
