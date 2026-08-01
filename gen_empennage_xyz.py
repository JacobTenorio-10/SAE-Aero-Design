#!/usr/bin/env python3
"""
gen_empennage_xyz.py - regenerate the eight CRV_HT_* / CRV_VT_* point files.

The counterpart to gen_airfoil_xyz.py, for the empennage (guide section 8.6).
The XYZ files are a DERIVED artifact of skeleton_equations_micro.txt plus the
raw NACA 0012 coordinates. Never hand-edit them; rerun this instead:

    python3 gen_empennage_xyz.py
    python3 gen_empennage_xyz.py --report   # print the resolved tail globals

Outputs (tab-separated, 6 dp, LF, no BOM - the format SolidWorks
Insert > Curve > Curve Through XYZ Points expects):

    airfoil_HT_root_upper_xyz.txt  -> CRV_HT_Root_Upper
    airfoil_HT_root_lower_xyz.txt  -> CRV_HT_Root_Lower
    airfoil_HT_tip_upper_xyz.txt   -> CRV_HT_Tip_Upper
    airfoil_HT_tip_lower_xyz.txt   -> CRV_HT_Tip_Lower
    airfoil_VT_root_upper_xyz.txt  -> CRV_VT_Root_Upper
    airfoil_VT_root_lower_xyz.txt  -> CRV_VT_Root_Lower
    airfoil_VT_tip_upper_xyz.txt   -> CRV_VT_Tip_Upper
    airfoil_VT_tip_lower_xyz.txt   -> CRV_VT_Tip_Lower

TRANSFORMS (identical to AIRCRAFT_EMPENNAGE_TRANSFORM_MICRO26.xlsx)

  Horizontal tail - the wing/HT axis map, shifted aft by J1:
    X = span
    Y = [ (0.25 - x)*sin(i) + y*cos(i) - 0.25*sin(i) ] * c + span*tan(dihedral_HT)
        + y_emp_axis
    Z = [ (0.25 - x)*cos(i) - y*sin(i) - 0.25     ] * c - span*tan(sweep_HT) - x_HT_LE_root

  ...and both surfaces are then lifted by y_emp_axis, because the empennage is
  referenced to AX_Long_Emp (the boom axis, y_emp_axis above AX_Long), not to
  the waterline. See note 3.

  Vertical tail - span runs +Y, so the span and thickness axes swap. A
  symmetric section at zero incidence means no chord rotation at all:
    X = y * c
    Y = span + h_tail_top + y_emp_axis
    Z = -x * c - span*tan(sweep_VT) - x_VT_LE_root

x, y are normalised airfoil coordinates. Aft is -Z, up is +Y, port is +X,
origin at the WING-root leading edge (not the tail).

TWO THINGS THAT ARE EASY TO GET WRONG
-------------------------------------
1. The trailing edge is CLOSED here, not in the raw file. The raw NACA 0012
   carries y = +0.00126 and y = -0.00126 at its two TE points; both are
   overridden to 0 so the upper and lower curves share one endpoint. Feeding
   SolidWorks the raw file directly gives an open TE and a failed knit.

2. INCIDENCE SENSE. "i_HT" is stored in the equations file as a POSITIVE
   magnitude (the positive-magnitude rule); the nose-DOWN direction is carried
   by the Flip on PLN_Incidence_HT. A coordinate transform has no plane to
   flip, so the sense has to be reapplied here. Positive i in the formula above
   rotates the section nose-UP, so the HT is built with -i_HT. Do not "fix"
   this by making i_HT negative in the equations file - that breaks the
   positive-magnitude rule and check.py will fail.

3. VERTICAL DATUM. The empennage sits on AX_Long_Emp, which is y_emp_axis above
   AX_Long, so both surfaces carry a + y_emp_axis lift. For the HT that is the
   whole vertical datum - the stabiliser has none of its own. For the VT it is
   applied ON TOP OF h_tail_top, which is itself measured from the waterline,
   so the fin root ends up h_tail_top above the boom axis. If the fin is meant
   to root ON the boom instead, set VT_SEAT_LIFT to 0.0 below and give the fin
   its own y_VT_root global measured from AX_Long_Emp - do not silently drop
   y_emp_axis from the HT to compensate.
"""

import argparse
import math
import os
import re

EQUATIONS = "skeleton_equations_micro.txt"
RAW = "NACA0012_coords_raw.txt"

# See note 2 in the module docstring. Nose-down stabiliser.
I_HT_SENSE = -1.0

# See note 3. Set to 0.0 if the fin should root on the boom rather than
# h_tail_top above it. Does not affect the HT.
VT_SEAT_LIFT = 1.0

NEEDED = ["c_root_HT", "c_tip_HT", "c_root_VT", "c_tip_VT",
          "b_semi_HT", "b_VT", "i_HT", "sweep_HT", "sweep_VT",
          "dihedral_HT", "x_HT_LE_root", "x_VT_LE_root", "h_tail_top",
          "y_emp_axis"]


def read_globals(path):
    """Resolve the equations file, including derived globals, and return NEEDED.

    Trig arguments carry their own * pi/180 (the radians rule), so the
    functions below take radians - matching SolidWorks with its
    Angular equation units drop-down set to Radians.
    """
    txt = open(path, "rb").read().decode("utf-8-sig")
    defs = []
    for line in txt.split("\r\n"):
        m = re.match(r'^"([^"]+)"\s*=\s*(.*?)(?:\s+\'|$)', line)
        if m:
            defs.append((m.group(1), m.group(2).strip()))

    env = dict(sin=math.sin, cos=math.cos, tan=math.tan,
               sqr=math.sqrt, abs=abs, pi=math.pi)
    vals, pending = {}, list(defs)
    for _ in range(len(defs) + 2):
        still = []
        for name, rhs in pending:
            expr = rhs.replace("^", "**")
            expr = re.sub(r'"([A-Za-z_][A-Za-z0-9_]*)"', r'V["\1"]', expr)
            try:
                vals[name] = eval(expr, {"__builtins__": {}}, dict(env, V=vals))
            except Exception:
                still.append((name, rhs))
        if not still or len(still) == len(pending):
            break
        pending = still

    missing = [k for k in NEEDED if k not in vals]
    if missing:
        raise SystemExit(f"could not resolve global(s) in {path}: {', '.join(missing)}")
    return {k: vals[k] for k in NEEDED}


def read_airfoil(path):
    """Normalised (x, y) pairs, trailing edge closed to y = 0 at both ends."""
    pts = []
    for line in open(path, encoding="utf-8"):
        t = line.split()
        if len(t) != 2:
            continue
        try:
            pts.append([float(t[0]), float(t[1])])
        except ValueError:
            continue                      # header line
    if len(pts) < 5:
        raise SystemExit(f"{path}: parsed only {len(pts)} coordinate pairs")
    pts[0][1] = 0.0                       # close the trailing edge
    pts[-1][1] = 0.0
    le = min(range(len(pts)), key=lambda k: pts[k][0])
    return pts, le


def transform_HT(pts, chord, incidence, span, sweep, dihedral, lift):
    i = math.radians(incidence)
    si, ci = math.sin(i), math.cos(i)
    dy = span * math.tan(math.radians(dihedral)) + lift
    dz = span * math.tan(math.radians(sweep))
    return [(span,
             ((0.25 - x) * si + y * ci - 0.25 * si) * chord + dy,
             ((0.25 - x) * ci - y * si - 0.25) * chord - dz)
            for x, y in pts]


def transform_VT(pts, chord, span, sweep, seat, station, lift):
    dz = span * math.tan(math.radians(sweep))
    return [(y * chord,
             span + seat + lift,
             -x * chord - dz - station)
            for x, y in pts]


def write(path, rows):
    body = "".join(f"{X:.6f}\t{Y:.6f}\t{Z:.6f}\n" for X, Y, Z in rows)
    open(path, "wb").write(body.encode("utf-8"))
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".")
    ap.add_argument("--report", action="store_true",
                    help="print the resolved tail globals and exit")
    args = ap.parse_args()
    d = args.dir
    j = lambda f: os.path.join(d, f)

    P = read_globals(j(EQUATIONS))
    if args.report:
        for k in NEEDED:
            print(f"  {k:16} = {P[k]:.6f}")
        return

    pts, le = read_airfoil(j(RAW))
    i_HT = I_HT_SENSE * P["i_HT"]
    lift = P["y_emp_axis"]
    print(f"airfoil points {len(pts)}, leading edge at index {le}")
    for k in NEEDED:
        print(f"  {k:16} = {P[k]:.6f}")
    print(f"  {'HT incidence':16} = {I_HT_SENSE * P['i_HT']:.6f}   (i_HT with the "
          f"nose-down sense reapplied; see the module docstring)")
    print(f"  {'vertical lift':16} = {lift:.6f}   (y_emp_axis; VT_SEAT_LIFT = "
          f"{VT_SEAT_LIFT})")

    # upper runs TE -> LE, lower runs LE -> TE, sharing both endpoints
    upper = pts[: le + 1]
    lower = pts[le:]

    jobs = []
    for tag, sub in (("upper", upper), ("lower", lower)):
        jobs.append((f"airfoil_HT_root_{tag}_xyz.txt",
                     transform_HT(sub, P["c_root_HT"], i_HT, 0.0,
                                  P["sweep_HT"], P["dihedral_HT"], lift)))
        jobs.append((f"airfoil_HT_tip_{tag}_xyz.txt",
                     transform_HT(sub, P["c_tip_HT"], i_HT, P["b_semi_HT"],
                                  P["sweep_HT"], P["dihedral_HT"], lift)))
        jobs.append((f"airfoil_VT_root_{tag}_xyz.txt",
                     transform_VT(sub, P["c_root_VT"], 0.0, P["sweep_VT"],
                                  P["h_tail_top"], P["x_VT_LE_root"],
                                  VT_SEAT_LIFT * lift)))
        jobs.append((f"airfoil_VT_tip_{tag}_xyz.txt",
                     transform_VT(sub, P["c_tip_VT"], P["b_VT"], P["sweep_VT"],
                                  P["h_tail_top"], P["x_VT_LE_root"],
                                  VT_SEAT_LIFT * lift)))

    # HT files need the aft station folded in; transform_HT leaves it out so the
    # wing formula stays recognisable. Apply it as the documented "- J1" shift.
    shifted = []
    for name, rows in jobs:
        if name.startswith("airfoil_HT"):
            rows = [(X, Y, Z - P["x_HT_LE_root"]) for X, Y, Z in rows]
        shifted.append((name, rows))

    for name, rows in sorted(shifted):
        n = write(j(name), rows)
        xs = [r[0] for r in rows]
        ys = [r[1] for r in rows]
        zs = [r[2] for r in rows]
        print(f"  wrote {name:30} {n:3} pts | X {min(xs):9.4f}..{max(xs):8.4f}"
              f" | Y {min(ys):9.4f}..{max(ys):8.4f}"
              f" | Z {min(zs):10.4f}..{max(zs):10.4f}")


if __name__ == "__main__":
    main()
