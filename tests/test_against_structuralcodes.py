"""Independent cross-check against the fib 'structuralcodes' library (EC2:2004 implementation)."""
import numpy as np
import pytest

sc = pytest.importorskip("structuralcodes.codes.ec2_2004")

from ec2crack import crack as c  # noqa: E402
from ec2crack import limits, materials  # noqa: E402

RNG = np.random.default_rng(7)


@pytest.mark.parametrize("fck", [20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80, 90])
def test_material_formulas(fck):
    assert materials.fctm(fck) == pytest.approx(sc.fctm(fck), rel=1e-9)
    assert materials.ecm(fck) == pytest.approx(sc.Ecm(sc.fcm(fck)), rel=1e-6)


@pytest.mark.parametrize("exp", ["X0", "XC1", "XC2", "XC3", "XC4", "XD1", "XD2", "XS1", "XS2", "XS3"])
def test_table_7_1n(exp):
    assert limits.w_max_table_7_1n(exp) == sc.w_max(exp, "qp")


def test_crack_width_chain_random_cases():
    for _ in range(200):
        h = RNG.uniform(150, 900); d = h - RNG.uniform(30, 80); x = RNG.uniform(0.1, 0.5) * d
        sigma = RNG.uniform(80, 400); fct = RNG.uniform(1.9, 4.5); Ecm = RNG.uniform(27e3, 40e3)
        As = RNG.uniform(300, 4000); b = 1000.0; cov = RNG.uniform(20, 60); phi = RNG.choice([10, 12, 16, 20, 25])
        hce = c.hc_eff(h, d, x)
        assert hce == pytest.approx(sc.hc_eff(h, d, x))
        rho = As / (b * hce)
        assert rho == pytest.approx(sc.rho_p_eff(As, 0.0, 0.0, b * hce))
        mine, _ = c.eps_sm_minus_eps_cm(sigma, fct, rho, 200000 / Ecm, 0.4)
        theirs = sc.eps_sm_eps_cm(sigma, sc.alpha_e(200000, Ecm), rho, sc.kt("long"), fct, 200000)
        assert mine == pytest.approx(theirs, rel=1e-9)
        s_mine, _ = c.sr_max(cov, phi, rho, 0.0, h, x)  # close spacing -> eq. 7.11
        assert s_mine == pytest.approx(sc.sr_max_close(cov, phi, rho, sc.k1("bond"), 0.5))
        s_far, _ = c.sr_max(cov, phi, rho, 1e9, h, x)
        assert s_far == pytest.approx(sc.sr_max_far(h, x))
        assert s_mine * mine == pytest.approx(sc.wk(s_mine, theirs))
