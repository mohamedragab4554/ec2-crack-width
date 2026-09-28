import pytest

from ec2crack import Concrete, RectangularSection
from ec2crack.cli import main
from ec2crack.crack import equivalent_diameter
from ec2crack.design import max_spacing_for_limit
from ec2crack.inspection import assess
from ec2crack.limits import w_max_table_7_1n, wk1_tightness_class_1
from ec2crack.simplified import as_min, max_bar_diameter_table, max_bar_spacing


def test_tightness_class_1_interpolation():
    assert wk1_tightness_class_1(1.0, 0.3) == 0.2        # hD/h = 3.3
    assert wk1_tightness_class_1(6.0, 0.3) == pytest.approx(0.125)   # hD/h = 20
    assert wk1_tightness_class_1(12.0, 0.3) == 0.05      # hD/h = 40
    with pytest.raises(ValueError):
        w_max_table_7_1n("XZ9")


def test_simplified_tables():
    assert max_bar_diameter_table(280, 0.3) == 12
    assert max_bar_diameter_table(300, 0.3) == pytest.approx(11)   # between 12 (280) and 10 (320)
    assert max_bar_spacing(200, 0.3) == 250
    with pytest.raises(ValueError):
        max_bar_spacing(400, 0.3)


def test_as_min_rectangular():
    # b 1000, h 250, fct 2.9, sigma_s 500: 0.4 * 1.0 * 2.9 * 125000 / 500 = 290 mm2
    assert as_min(1000, 250, 2.9, 500) == pytest.approx(290)
    assert as_min(1000, 800, 2.9, 500) == pytest.approx(0.4 * 0.65 * 2.9 * 400000 / 500)


def test_equivalent_diameter():
    assert equivalent_diameter({16: 2, 12: 2}) == pytest.approx((2 * 256 + 2 * 144) / (2 * 16 + 2 * 12))


def test_design_search_and_inspection():
    sec = RectangularSection(1000, 250, 35, 12, spacing=150)
    s = max_spacing_for_limit(sec, Concrete(30, 2.0), 25.0, 0.3)
    assert s is not None and s >= 150
    obs = assess({"a": 0.35, "b": 0.25, "c": 0.1}, 0.3, predicted_wk_mm=0.15)
    assert [o.flag for o in obs] == ["exceeds limit", "review", "within limit"]


def test_cli_exit_codes(capsys):
    args = ["wk", "--b", "1000", "--h", "250", "--cover", "35", "--bar", "12", "--spacing", "150", "--moment"]
    assert main(args + ["25", "--exposure", "XC3"]) == 0
    assert main(args + ["60", "--exposure", "XC3"]) == 1
    assert "wk =" in capsys.readouterr().out


def test_design_search_does_not_exploit_eq_7_14_discontinuity():
    # H10: fails between ~170 and 200 mm, passes again just beyond 5(c + phi/2) = 200 mm via eq. 7.14
    from ec2crack import crack_width_section
    con = Concrete(30, 2.0)
    sec = RectangularSection(1000, 250, 35, 10, spacing=150)
    s = max_spacing_for_limit(sec, con, 25.0, 0.3)
    assert s is not None and s < 200
    assert crack_width_section(RectangularSection(1000, 250, 35, 10, spacing=210), con, 25.0).wk <= 0.3
