"""Worked example (docs/worked_example.md), every intermediate value checked by hand."""
import pytest

from ec2crack import Concrete, RectangularSection, crack_width_section
from ec2crack.section import analyse

SEC = RectangularSection(b=1000, h=250, cover=35, bar=12, spacing=150)
CON = Concrete.from_class("C30/37", creep=2.0)


def test_material_properties_table_3_1():
    assert CON.fcm == 38
    assert CON.fctm == pytest.approx(2.896, abs=1e-3)
    assert CON.Ecm == pytest.approx(32837, abs=1)
    assert CON.Ec_eff == pytest.approx(32837 / 3, abs=1)


def test_section_geometry():
    assert SEC.d == 209
    assert SEC.As == pytest.approx(753.98, abs=0.01)


def test_cracked_section_equilibrium():
    cs = analyse(SEC, CON, 25.0)
    assert cs.x == pytest.approx(63.4, abs=0.1)
    # force equilibrium: compression 0.5 b x sigma_c == tension As sigma_s
    assert 0.5 * SEC.b * cs.x * cs.sigma_c == pytest.approx(SEC.As * cs.sigma_s, rel=1e-9)
    # moment equilibrium: As sigma_s (d - x/3) == M
    assert SEC.As * cs.sigma_s * (SEC.d - cs.x / 3) == pytest.approx(25e6, rel=1e-9)
    assert cs.sigma_s == pytest.approx(176.5, abs=0.1)


def test_crack_width_steps():
    r = crack_width_section(SEC, CON, 25.0)
    assert r.hc_eff == pytest.approx((250 - r.x) / 3)          # (h - x)/3 governs over 2.5(h-d) = 102.5
    assert r.rho_p_eff == pytest.approx(0.01212, abs=1e-5)
    assert r.eps_governed_by_minimum                            # 0.6 sigma_s / Es
    assert r.eps_sm_minus_eps_cm == pytest.approx(0.6 * r.sigma_s / 200000)
    assert r.sr_max_rule == "7.11"
    assert r.sr_max == pytest.approx(3.4 * 35 + 0.8 * 0.5 * 0.425 * 12 / r.rho_p_eff)
    assert r.wk == pytest.approx(0.152, abs=0.001)


def test_wide_spacing_uses_7_14():
    wide = RectangularSection(b=1000, h=250, cover=35, bar=12, spacing=300)  # > 5(c + phi/2) = 205
    r = crack_width_section(wide, CON, 25.0)
    assert r.sr_max_rule == "7.14" and r.sr_max == pytest.approx(1.3 * (250 - r.x))


def test_monotonic_behaviour():
    wks = [crack_width_section(SEC, CON, m).wk for m in (10, 20, 30, 40)]
    assert wks == sorted(wks)
    tighter = crack_width_section(RectangularSection(1000, 250, 35, 12, spacing=100), CON, 25.0).wk
    assert tighter < crack_width_section(SEC, CON, 25.0).wk
