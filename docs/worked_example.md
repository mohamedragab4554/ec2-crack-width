# Worked example: 250 mm slab, C30/37, XC3

A one-metre strip of a 250 mm slab, H12 at 150 mm centres, 35 mm cover, quasi-permanent moment 25 kNm/m, final creep coefficient 2.0. The key values below are asserted in `tests/test_hand_calculation.py`.

| # | Quantity | Clause | Hand calculation | Result |
|---|---|---|---|---|
| 1 | fcm, fctm, Ecm | Table 3.1 | 30 + 8; 0.30 · 30^(2/3); 22 (38/10)^0.3 | 38 MPa; 2.896 MPa; 32.84 GPa |
| 2 | Ec,eff | eq. 7.20 | 32.84 / (1 + 2.0) | 10.95 GPa |
| 3 | d, As | — | 250 − 35 − 12/2; (1000/150) · π·12²/4 | 209 mm; 754 mm² |
| 4 | Modular ratio n | — | 200 / 10.95 | 18.27 |
| 5 | Neutral axis x | cracked elastic | 500 x² + 13 780 x − 2 880 000 = 0 | 63.4 mm |
| 6 | σs | — | 25·10⁶ / (754 · (209 − 63.4/3)) | 176.5 MPa |
| 7 | hc,eff | 7.3.2(3) | min(2.5·41, (250 − 63.4)/3, 125) | 62.2 mm |
| 8 | ρp,eff | eq. 7.10 | 754 / (1000 · 62.2) | 0.01212 |
| 9 | εsm − εcm | eq. 7.9 | [176.5 − 0.4 · 2.896/0.01212 · (1 + 6.09 · 0.01212)] / 200 000 = 0.37·10⁻³ < 0.6 σs/Es | 0.529·10⁻³ (lower bound governs) |
| 10 | Spacing check | 7.3.4(3) | 150 ≤ 5(35 + 6) = 205 → eq. 7.11 | — |
| 11 | sr,max | eq. 7.11 | 3.4 · 35 + 0.8 · 0.5 · 0.425 · 12 / 0.01212 | 287.3 mm |
| 12 | **wk** | eq. 7.8 | 287.3 · 0.529·10⁻³ | **0.152 mm** |
| 13 | Limit | Table 7.1N | XC3, quasi-permanent | 0.30 mm → OK (0.51) |

Output of `ec2crack wk --b 1000 --h 250 --cover 35 --bar 12 --spacing 150 --moment 25 --exposure XC3`:

| Step | Clause | Value |
|---|---|---|
| Concrete | Table 3.1 | fck 30 MPa, fctm 2.90 MPa, Ecm 32.8 GPa |
| Effective modulus | eq. 7.20 | phi 2 -> Ec,eff 10.9 GPa |
| Section | - | b 1000, h 250, c 35, d 209.0 mm; As 754 mm2 (bar 12 @ 150) |
| Neutral axis | elastic, cracked | x = 63.4 mm |
| Steel stress | M = 25 kNm | sigma_s = 176.5 MPa |
| Effective tension area | 7.3.2(3) | hc,eff 62.2 mm, Ac,eff 62217 mm2, rho_p,eff 0.01212 |
| Mean strain difference | eq. 7.9 | 0.5294 x10^-3 (0.6 sigma_s/Es governs) |
| Maximum crack spacing | eq. 7.11 | sr,max = 287.3 mm |
| **Crack width** | eq. 7.8 | **wk = 0.152 mm** |
| Limit | Table 7.1N / EN 1992-3 | w_lim = 0.300 mm -> **OK** (utilisation 0.51) |

Largest spacing of H12 meeting 0.300 mm: 325 mm (crack-width criterion only; also check the detailing rules of EN 1992-1-1 section 9)
