"""Rebuild docs/images from the package (no data files needed): python scripts/make_figures.py"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ec2crack import Concrete, RectangularSection, crack_width_section  # noqa: E402
from ec2crack.limits import wk1_tightness_class_1  # noqa: E402

OUT = ROOT / "docs" / "images"
BG, PANEL, GRID, INK, MUTED = "#0b1220", "#101a2b", "#22324a", "#e6edf5", "#8aa0b8"
SERIES = ["#3987e5", "#d95926", "#199e70", "#c98500"]  # validated categorical order (dark surface)
plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": PANEL, "savefig.facecolor": BG, "axes.edgecolor": GRID,
    "axes.labelcolor": INK, "text.color": INK, "xtick.color": MUTED, "ytick.color": MUTED, "grid.color": GRID,
    "axes.grid": True, "axes.axisbelow": True, "grid.linewidth": 0.6, "font.size": 10.5, "axes.titlesize": 12.5,
    "axes.titleweight": "bold", "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 2,
})


def design_chart() -> None:
    con = Concrete.from_class("C30/37", creep=2.0)
    base = RectangularSection(b=1000, h=250, cover=35, bar=12, spacing=150)
    spacings = np.arange(75, 305, 5)
    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    for col, bar in zip(SERIES, (10, 12, 16, 20), strict=True):
        wk = [crack_width_section(replace(base, bar=float(bar), spacing=float(s)), con, 25.0).wk for s in spacings]
        ax.plot(spacings, wk, color=col, label=f"H{bar}")
        ax.text(spacings[-1] + 3, wk[-1], f"H{bar}", color=INK, va="center", fontsize=9)
    ax.axhline(0.3, color=INK, ls="--", lw=1.2)
    ax.text(78, 0.307, "w_max 0.3 mm (Table 7.1N, XC3)", fontsize=9)
    ax.axvline(5 * (35 + 6), color=MUTED, ls=":", lw=1)
    ax.text(5 * (35 + 6) + 3, 0.02, "5(c + phi/2) for H12:\neq. 7.11 -> 7.14", fontsize=8, color=MUTED)
    ax.set_xlim(75, 325)
    ax.set_xlabel("bar spacing (mm)")
    ax.set_ylabel("wk (mm)")
    ax.set_title("wk vs bar spacing: 250 mm slab, C30/37, c 35 mm, M_qp 25 kNm/m", loc="left")
    ax.legend(frameon=False, ncol=4, loc="upper left", bbox_to_anchor=(0, 0.93))
    fig.text(0.01, 0.015, "The drop is EC2 switching to eq. 7.14 (sr,max = 1.3(h - x)) once spacing > 5(c + phi/2): "
             "the two rules are not continuous.", color=MUTED, fontsize=8.5)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(OUT / "design_chart.png", dpi=150)
    plt.close(fig)


def tightness_chart() -> None:
    r = np.linspace(0, 45, 200)
    fig, ax = plt.subplots(figsize=(8.8, 3.4))
    ax.plot(r, [wk1_tightness_class_1(x, 1.0) for x in r], color=SERIES[0])
    ax.scatter([20], [0.125], s=40, color=SERIES[1], zorder=3)
    ax.annotate("6 m head, 300 mm wall -> 0.125 mm", (20, 0.125), (23, 0.16), fontsize=9,
                arrowprops=dict(arrowstyle="-", color=MUTED))
    ax.set_xlabel("hD / h (hydrostatic head / wall thickness)")
    ax.set_ylabel("wk1 (mm)")
    ax.set_ylim(0, 0.23)
    ax.set_title("EN 1992-3 tightness class 1: through-crack limit", loc="left")
    fig.tight_layout()
    fig.savefig(OUT / "tightness_class_1.png", dpi=150)
    plt.close(fig)


def validation_chart() -> None:
    import structuralcodes.codes.ec2_2004 as sc

    from ec2crack import crack as c
    rng = np.random.default_rng(7)
    mine, theirs = [], []
    for _ in range(300):
        h = rng.uniform(150, 900); d = h - rng.uniform(30, 80); x = rng.uniform(0.1, 0.5) * d
        sigma = rng.uniform(80, 400); fct = rng.uniform(1.9, 4.5); Ecm = rng.uniform(27e3, 40e3)
        As = rng.uniform(300, 4000); cov = rng.uniform(20, 60); phi = rng.choice([10, 12, 16, 20, 25])
        rho = As / (1000 * c.hc_eff(h, d, x))
        e1, _ = c.eps_sm_minus_eps_cm(sigma, fct, rho, 200000 / Ecm, 0.4)
        s1, _ = c.sr_max(cov, phi, rho, 0.0, h, x)
        mine.append(s1 * e1)
        e2 = sc.eps_sm_eps_cm(sigma, sc.alpha_e(200000, Ecm), rho, sc.kt("long"), fct, 200000)
        theirs.append(sc.wk(sc.sr_max_close(cov, phi, rho, sc.k1("bond"), 0.5), e2))
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    m = max(max(mine), max(theirs))
    ax.plot([0, m], [0, m], color=MUTED, lw=1, ls="--")
    ax.scatter(theirs, mine, s=12, color=SERIES[0], alpha=0.8)
    err = np.max(np.abs(np.array(mine) - np.array(theirs)))
    ax.set_xlabel("wk, fib structuralcodes (mm)"); ax.set_ylabel("wk, ec2crack (mm)")
    ax.set_title(f"300 random cases: max |difference| {err:.1e} mm", loc="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "validation.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    design_chart(); tightness_chart(); validation_chart()
    print("written", sorted(p.name for p in OUT.glob("*.png")))
