"""Concrete properties, EN 1992-1-1 Table 3.1 and 7.20 (units: MPa, mm)."""
from __future__ import annotations

import math
from dataclasses import dataclass

ES = 200_000.0  # MPa, reinforcing steel modulus (EN 1992-1-1 3.2.7(4))


def fcm(fck: float) -> float:
    """Mean compressive strength, Table 3.1: fcm = fck + 8 MPa."""
    return fck + 8.0


def fctm(fck: float) -> float:
    """Mean axial tensile strength, Table 3.1."""
    if fck <= 0:
        raise ValueError("fck must be positive")
    if fck <= 50:
        return 0.30 * fck ** (2.0 / 3.0)
    return 2.12 * math.log(1.0 + fcm(fck) / 10.0)


def ecm(fck: float) -> float:
    """Secant modulus of elasticity, Table 3.1: Ecm = 22 (fcm/10)^0.3 GPa, returned in MPa."""
    return 22_000.0 * (fcm(fck) / 10.0) ** 0.3


@dataclass(frozen=True)
class Concrete:
    """Concrete grade with the properties used for crack control.

    ``creep`` is the final creep coefficient phi(inf, t0) used for the effective modulus
    Ec,eff = Ecm / (1 + phi) (eq. 7.20) in the cracked-section stress calculation.
    """

    fck: float
    creep: float = 0.0

    @property
    def fcm(self) -> float:
        return fcm(self.fck)

    @property
    def fctm(self) -> float:
        return fctm(self.fck)

    @property
    def Ecm(self) -> float:  # noqa: N802 - Eurocode symbol
        return ecm(self.fck)

    @property
    def Ec_eff(self) -> float:  # noqa: N802
        return self.Ecm / (1.0 + self.creep)

    @classmethod
    def from_class(cls, name: str, creep: float = 0.0) -> "Concrete":
        """``Concrete.from_class("C30/37")``."""
        try:
            return cls(float(name.upper().lstrip("C").split("/")[0]), creep)
        except ValueError as exc:
            raise ValueError(f"cannot parse concrete class {name!r}") from exc
