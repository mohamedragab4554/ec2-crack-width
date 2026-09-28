"""Command line: ``ec2crack wk ...``, ``ec2crack limit ...``, ``ec2crack assess ...``."""
from __future__ import annotations

import argparse
import json
import sys

from .crack import crack_width_section
from .design import max_spacing_for_limit
from .inspection import assess, read_widths
from .limits import TIGHTNESS_CLASSES, w_max_table_7_1n, wk1_tightness_class_1
from .materials import Concrete
from .report import calc_sheet
from .section import RectangularSection


def _limit(args) -> float | None:
    if args.tightness is not None:
        if args.tightness == 1:
            return wk1_tightness_class_1(args.head, args.h / 1000.0)
        if args.tightness == 0 and args.exposure:
            return w_max_table_7_1n(args.exposure)
        return None
    return w_max_table_7_1n(args.exposure) if args.exposure else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ec2crack", description="EN 1992 crack-width checks")
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("wk", help="crack width of a rectangular section in bending")
    for k, hlp in [("b", "width mm"), ("h", "depth mm"), ("cover", "cover to bars mm"), ("bar", "bar diameter mm"),
                   ("moment", "quasi-permanent moment kNm (on width b)")]:
        w.add_argument(f"--{k}", type=float, required=True, help=hlp)
    w.add_argument("--spacing", type=float, help="bar spacing mm")
    w.add_argument("--n-bars", type=int)
    w.add_argument("--link", type=float, default=0.0)
    w.add_argument("--concrete", default="C30/37")
    w.add_argument("--creep", type=float, default=2.0, help="phi(inf,t0) for Ec,eff (default 2.0)")
    w.add_argument("--short-term", action="store_true", help="kt = 0.6 instead of 0.4")
    w.add_argument("--exposure", help="e.g. XC3 -> Table 7.1N limit")
    w.add_argument("--tightness", type=int, choices=[0, 1, 2, 3], help="EN 1992-3 tightness class")
    w.add_argument("--head", type=float, default=0.0, help="hydrostatic head hD (m) for tightness class 1")
    w.add_argument("--json", action="store_true")
    li = sub.add_parser("limit", help="crack-width limit only")
    li.add_argument("--exposure")
    li.add_argument("--tightness", type=int, choices=[0, 1, 2, 3])
    li.add_argument("--head", type=float, default=0.0)
    li.add_argument("--h", type=float, default=0.0, help="wall thickness mm")
    a = sub.add_parser("assess", help="compare measured widths (CSV) with a limit")
    a.add_argument("csv")
    a.add_argument("--limit", type=float, required=True)
    a.add_argument("--predicted", type=float)
    a.add_argument("--width-col", default="measured_width_mm")
    a.add_argument("--id-col", default="image_id")
    args = ap.parse_args(argv)

    if args.cmd == "limit":
        lim = _limit(args)
        if args.tightness in (2, 3):
            print(TIGHTNESS_CLASSES[args.tightness])
        else:
            print(f"{lim:.3f} mm")
        return 0
    if args.cmd == "assess":
        for o in assess(read_widths(args.csv, args.id_col, args.width_col), args.limit, args.predicted):
            print(f"{o.crack_id:<28}{o.width_mm:>8.2f} mm  {o.ratio_to_limit:>5.2f} x limit  {o.flag}")
        return 0
    sec = RectangularSection(args.b, args.h, args.cover, args.bar, args.spacing, args.n_bars, args.link)
    con = Concrete.from_class(args.concrete, args.creep)
    r = crack_width_section(sec, con, args.moment, long_term=not args.short_term)
    lim = _limit(args)
    if args.json:
        print(json.dumps({**r.as_dict(), "limit": lim}, indent=2))
    else:
        print(calc_sheet(sec, con, args.moment, r, lim))
        if lim and args.spacing:
            s = max_spacing_for_limit(sec, con, args.moment, lim)
            print(f"\nLargest spacing of H{args.bar:g} meeting {lim:.3f} mm: "
                  f"{'none up to 400 mm' if s is None else f'{s:.0f} mm'} "
                  "(crack-width criterion only; also check the detailing rules of EN 1992-1-1 section 9)")
        if args.tightness in (2, 3):
            print(f"\nTightness class {args.tightness}: {TIGHTNESS_CLASSES[args.tightness]}")
    return 0 if lim is None or r.wk <= lim else 1


if __name__ == "__main__":
    sys.exit(main())
