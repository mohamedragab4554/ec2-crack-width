"""Plain-text / Markdown calculation sheet."""
from __future__ import annotations

from .crack import CrackWidthResult
from .materials import Concrete
from .section import RectangularSection


def calc_sheet(sec: RectangularSection, con: Concrete, M: float, r: CrackWidthResult, limit: float | None) -> str:
    L = [
        "| Step | Clause | Value |", "|---|---|---|",
        f"| Concrete | Table 3.1 | fck {con.fck:g} MPa, fctm {con.fctm:.2f} MPa, Ecm {con.Ecm / 1000:.1f} GPa |",
        f"| Effective modulus | eq. 7.20 | phi {con.creep:g} -> Ec,eff {con.Ec_eff / 1000:.1f} GPa |",
        f"| Section | - | b {sec.b:g}, h {sec.h:g}, c {sec.c:g}, d {sec.d:.1f} mm; "
        f"As {sec.As:.0f} mm2 (bar {sec.bar:g} @ {sec.bar_spacing:.0f}) |",
        f"| Neutral axis | elastic, cracked | x = {r.x:.1f} mm |",
        f"| Steel stress | M = {M:g} kNm | sigma_s = {r.sigma_s:.1f} MPa |",
        f"| Effective tension area | 7.3.2(3) | hc,eff {r.hc_eff:.1f} mm, Ac,eff {r.Ac_eff:.0f} mm2, "
        f"rho_p,eff {r.rho_p_eff:.5f} |",
        f"| Mean strain difference | eq. 7.9 | {r.eps_sm_minus_eps_cm * 1e3:.4f} x10^-3"
        f"{' (0.6 sigma_s/Es governs)' if r.eps_governed_by_minimum else ''} |",
        f"| Maximum crack spacing | eq. {r.sr_max_rule} | sr,max = {r.sr_max:.1f} mm |",
        f"| **Crack width** | eq. 7.8 | **wk = {r.wk:.3f} mm** |",
    ]
    if limit is not None:
        ok = "OK" if r.wk <= limit else "NOT OK"
        L.append(f"| Limit | Table 7.1N / EN 1992-3 | w_lim = {limit:.3f} mm -> **{ok}** "
                 f"(utilisation {r.wk / limit:.2f}) |")
    return "\n".join(L)
