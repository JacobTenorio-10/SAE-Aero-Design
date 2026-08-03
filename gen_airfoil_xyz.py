#!/usr/bin/env python3
"""
gen_airfoil_xyz.py - regenerate the four CRV_Airfoil_* point files.

The XYZ files are a DERIVED artifact of skeleton_equations_micro.txt plus the
raw airfoil coordinates. Never hand-edit them; rerun this instead:

    python3 gen_airfoil_xyz.py
    python3 gen_airfoil_xyz.py --verify-legacy    # reproduce the old 2-deg files

Outputs (tab-separated, 6 dp, LF, no BOM - the format SolidWorks
Insert > Curve > Curve Through XYZ Points expects):

    airfoil_root_upper_xyz.txt   -> CRV_Airfoil_Root_Upper
    airfoil_root_lower_xyz.txt   -> CRV_Airfoil_Root_Lower
    airfoil_tip_upper_xyz.txt    -> CRV_Airfoil_Tip_Upper
    airfoil_tip_lower_xyz.txt    -> CRV_Airfoil_Tip_Lower

TRANSFORM (identical to AIRCRAFT_AIRFOIL_TRANSFORM_MICRO26.xlsx, cells D3/E3):

    X = span
    Y = [ (0.25 - x)*sin(i) + y*cos(i) - 0.25*sin(i) ] * c + span*tan(dihedral)
    Z = [ (0.25 - x)*cos(i) - y*sin(i) - 0.25     ] * c - span*tan(sweep_LE)

twist_tip is a POSITIVE washout magnitude and is SUBTRACTED, matching
    "i_tip" = "i_wing" - "twist_tip"
in skeleton_equations_micro.txt. Both are zero at present, so this sign is
currently invisible; it stops being invisible the moment washout is dialled in.

x, y are normalised airfoil coordinates; i is the section incidence; the
section rotates about the quarter-chord point (0.25, 0). Aft is -Z, up is +Y,
port is +X, origin at the wing-root leading edge.

The trailing edge is CLOSED: the raw file's two TE points carry y = +0.00009
and y = -0.00003, and the spreadsheet overrides both to y = 0 so the upper and
lower curves share one endpoint. This script does the same.
"""

import argparse
import math
import os
import re

EQUATIONS = "skeleton_equations_micro.txt"
RAW = "FX74CL5140_coords_raw.txt"

# Legacy Control_Panel values, for --verify-legacy
LEGACY = dict(b_semi=550.0, c_root=300.0, c_tip=180.0,
              i_root=2.0, i_tip=0.0, sweep_LE=0.0, dihedral=4.0)


def read_globals(path):
    txt = open(path, "rb").read().decode("utf-8-sig")
    vals = {}
    for line in txt.replace("\r\n", "\n").split("\n"):
        m = re.match(r'^"([^"]+)"\s*=\s*(-?[\d.]+)\s*(?:\'|$)', line)
        if m:
            vals[m.group(1)] = float(m.group(2))
    need = ["b_semi", "c_root", "c_tip", "i_wing", "twist_tip", "sweep_LE", "dihedral"]
    missing = [k for k in need if k not in vals]
    if missing:
        raise SystemExit(f"missing numeric global(s) in {path}: {', '.join(missing)}")
    return dict(b_semi=vals["b_semi"], c_root=vals["c_root"], c_tip=vals["c_tip"],
                i_root=vals["i_wing"], i_tip=vals["i_wing"] - vals["twist_tip"],
                sweep_LE=vals["sweep_LE"], dihedral=vals["dihedral"])


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


def transform(pts, chord, incidence, span, sweep, dihedral):
    i = math.radians(incidence)
    si, ci = math.sin(i), math.cos(i)
    dy = span * math.tan(math.radians(dihedral))
    dz = span * math.tan(math.radians(sweep))
    out = []
    for x, y in pts:
        Y = ((0.25 - x) * si + y * ci - 0.25 * si) * chord + dy
        Z = ((0.25 - x) * ci - y * si - 0.25) * chord - dz
        out.append((span, Y, Z))
    return out


def write(path, rows):
    body = "".join(f"{X:.6f}\t{Y:.6f}\t{Z:.6f}\n" for X, Y, Z in rows)
    open(path, "wb").write(body.encode("utf-8"))
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".")
    ap.add_argument("--verify-legacy", action="store_true",
                    help="regenerate with the old Control_Panel values instead")
    args = ap.parse_args()
    d = args.dir
    j = lambda f: os.path.join(d, f)

    P = LEGACY if args.verify_legacy else read_globals(j(EQUATIONS))
    pts, le = read_airfoil(j(RAW))

    print(f"airfoil points {len(pts)}, leading edge at index {le}")
    for k, v in P.items():
        print(f"  {k:9} = {v}")

    # upper runs TE -> LE, lower runs LE -> TE, sharing both endpoints
    upper_idx = pts[: le + 1]
    lower_idx = pts[le:]

    jobs = [
        ("airfoil_root_upper_xyz.txt", upper_idx, P["c_root"], P["i_root"], 0.0),
        ("airfoil_root_lower_xyz.txt", lower_idx, P["c_root"], P["i_root"], 0.0),
        ("airfoil_tip_upper_xyz.txt",  upper_idx, P["c_tip"],  P["i_tip"],  P["b_semi"]),
        ("airfoil_tip_lower_xyz.txt",  lower_idx, P["c_tip"],  P["i_tip"],  P["b_semi"]),
    ]
    for name, sub, chord, inc, span in jobs:
        rows = transform(sub, chord, inc, span, P["sweep_LE"], P["dihedral"])
        n = write(j(name), rows)
        zs = [r[2] for r in rows]
        ys = [r[1] for r in rows]
        print(f"  wrote {name:28} {n:3} pts | Z {min(zs):10.4f}..{max(zs):9.4f}"
              f" | Y {min(ys):9.4f}..{max(ys):8.4f}")


if __name__ == "__main__":
    main()
