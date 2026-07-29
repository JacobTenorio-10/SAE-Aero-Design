#!/usr/bin/env python3
"""
check.py - invariant verification for the SAE Micro skeleton deliverable set.

Run after ANY edit, by you or by Claude:

    python3 check.py              # check files in the current directory
    python3 check.py --dir path   # check files elsewhere
    python3 check.py -q           # only print failures

Exit code 0 = all invariants hold, 1 = at least one failed.
That makes it usable as a git pre-commit hook:

    #!/bin/sh
    python3 check.py || { echo "skeleton invariants failed"; exit 1; }

--------------------------------------------------------------------------
BASELINES - update these deliberately, never to silence a failure.
A changed count is either an intentional structural edit (update it here in
the same commit) or an accident (fix the file, not this number).
--------------------------------------------------------------------------
"""

import argparse
import os
import re
import sys

# ---- baselines ----------------------------------------------------------
HASH_HEADERS_SKELETON = 25      # count of ^#{3,} in the SKELETON guide
H2_SKELETON           = 15      # count of ^## in the SKELETON guide
GLOBAL_COUNT          = 223     # definitions in skeleton_equations_micro.txt

# Globals allowed to hold a negative value. Everything else is a distance or
# a magnitude and must be positive - direction belongs to the sketch, not the
# global. Angles are the only legitimate exception.
NEGATIVE_ALLOWED = {"i_HT", "twist_tip", "sweep_LE", "sweep_HT", "sweep_VT",
                    "dihedral", "dihedral_HT", "dihedral_VT", "thrust_down",
                    "thrust_side", "i_wing"}

# Convention violations. The model stores aft distances as positive magnitudes
# on the -Z side; this wording contradicts that and must never appear.
FORBIDDEN = ["aft-positive", "forward-negative", "negative-valued",
             "positive-valued", "negative X", "aft = positive",
             "apply along $-Z$"]

EQUATIONS = "skeleton_equations_micro.txt"
PARAMS    = "Aircraft_Skeleton_Parameters_Micro.md"
SKELETON  = "Skeleton_Sketch_Part_Guide_Micro.md"
INSTALL   = "Installation_Layout_Guide_Micro.md"
MD_FILES  = [PARAMS, SKELETON, INSTALL]

# Identifiers that look like globals but are prose. Extend as needed.
REF_IGNORE = {"global", "name", "value", "below", "above", "that_global", "some_global"}


class Report:
    def __init__(self, quiet=False):
        self.fails = []
        self.quiet = quiet

    def ok(self, msg):
        if not self.quiet:
            print(f"  PASS  {msg}")

    def fail(self, msg):
        self.fails.append(msg)
        print(f"  FAIL  {msg}")

    def check(self, cond, msg):
        self.ok(msg) if cond else self.fail(msg)


def read_equations(path):
    """Return (raw_bytes, decoded_text_without_bom)."""
    raw = open(path, "rb").read()
    return raw, raw.decode("utf-8-sig")


def globals_in(text):
    """Ordered list of (name, rhs) definitions from the equations file."""
    out = []
    for line in text.split("\r\n"):
        m = re.match(r'^"([^"]+)"\s*=\s*(.*?)(?:\s+\'|$)', line)
        if m:
            out.append((m.group(1), m.group(2).strip()))
    return out


def code_spans(line):
    """Backtick spans and quoted strings - where house style puts globals."""
    return re.findall(r"`([^`]*)`", line) + re.findall(r'"([^"]*)"', line)


def referenced_globals(text, names):
    """Global names actually cited inside code spans or quotes."""
    found = set()
    for line in text.split("\n"):
        for span in code_spans(line):
            for ident in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", span):
                if ident in names:
                    found.add(ident)
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".", help="directory holding the four files")
    ap.add_argument("-q", "--quiet", action="store_true", help="print failures only")
    args = ap.parse_args()
    d = args.dir
    r = Report(args.quiet)

    missing = [f for f in [EQUATIONS] + MD_FILES if not os.path.exists(os.path.join(d, f))]
    if missing:
        print("FAIL  missing file(s): " + ", ".join(missing))
        return 1

    p = lambda f: os.path.join(d, f)

    # ---- 1. equations file: encoding, line endings, global count -----------
    print(f"\n{EQUATIONS}")
    raw, txt = read_equations(p(EQUATIONS))
    r.check(raw[:3] == b"\xef\xbb\xbf", "UTF-8 BOM present")
    bare_lf = txt.count("\n") - txt.count("\r\n")
    r.check(bare_lf == 0, f"CRLF only (bare LF = {bare_lf})")

    defs = globals_in(txt)
    names = [n for n, _ in defs]
    r.check(len(names) == GLOBAL_COUNT,
            f"global count = {len(names)} (baseline {GLOBAL_COUNT})")
    dupes = sorted({n for n in names if names.count(n) > 1})
    r.check(not dupes, f"no duplicate definitions{'' if not dupes else ': ' + ', '.join(dupes)}")

    nameset = set(names)

    # every global referenced inside the equations file must be defined
    internal = set()
    for _, rhs in defs:
        internal |= set(re.findall(r'"([A-Za-z_][A-Za-z0-9_]*)"', rhs))
    undef = sorted(internal - nameset)
    r.check(not undef, f"no undefined globals in RHS expressions{'' if not undef else ': ' + ', '.join(undef)}")

    # sign convention: distances are positive magnitudes
    neg = [n for n, rhs in defs if rhs.startswith("-") and n not in NEGATIVE_ALLOWED]
    r.check(not neg, f"no negative distance globals{'' if not neg else ': ' + ', '.join(neg)}")

    # ---- 2. markdown files: encoding + line endings ------------------------
    for f in MD_FILES:
        print(f"\n{f}")
        rb = open(p(f), "rb").read()
        r.check(rb[:3] != b"\xef\xbb\xbf", "no BOM")
        r.check(b"\r\n" not in rb, "LF line endings only")
        t = rb.decode("utf-8")
        hits = {k: t.count(k) for k in FORBIDDEN if t.count(k)}
        r.check(not hits, f"no forbidden convention strings{'' if not hits else ': ' + str(hits)}")

        if f == SKELETON:
            nh = len(re.findall(r"^#{3,}", t, re.M))
            n2 = len(re.findall(r"^## ", t, re.M))
            r.check(nh == HASH_HEADERS_SKELETON,
                    f"hash-headers = {nh} (baseline {HASH_HEADERS_SKELETON})")
            r.check(n2 == H2_SKELETON, f"H2 headers = {n2} (baseline {H2_SKELETON})")

    # ---- 3. Appendix A must be byte-identical to the equations file --------
    print("\ncross-file")
    params = open(p(PARAMS), encoding="utf-8").read()
    m = re.search(r"```(?:\w*)\n(.*?)```", params, re.S)
    if not m:
        r.fail("Appendix A code block not found in params")
    else:
        r.check(m.group(1).rstrip("\n") == txt.replace("\r\n", "\n").rstrip("\n"),
                "Appendix A byte-identical to equations file (CRLF->LF)")

    # ---- 4. no dangling global references in the guides --------------------
    for f in [SKELETON, INSTALL]:
        t = open(p(f), encoding="utf-8").read()
        refs = set()
        for line in t.split("\n"):
            for span in code_spans(line):
                # only treat as a reference if it reads like a dimension
                # expression or an explicitly quoted global
                for ident in re.findall(r'=\s*"([A-Za-z_][A-Za-z0-9_]*)"', span):
                    refs.add(ident)
        dangling = sorted(refs - nameset - REF_IGNORE)
        r.check(not dangling,
                f"{f}: no dangling `= \"global\"` refs{'' if not dangling else ': ' + ', '.join(dangling)}")

    # ---- 5. the one-variable rule ------------------------------------------
    # Every Smart Dimension / Offset Distance / Modify entry must be a single
    # global. Expressions typed into SolidWorks are invisible to the equations
    # file and drift silently.
    #
    # Documentation of a global's own definition is NOT a dimension. Two shapes
    # are recognised and exempted:
    #   `some_global` `= <expr>`        (restating a definition)
    #   ... is defined in ... as `= <expr>`
    dim_kw = re.compile(r"Smart[- ]Dimension|Offset Distance|Modify|dimension|Dimension")
    single = re.compile(r'^"[A-Za-z_][A-Za-z0-9_]*"$')
    exempt = re.compile(r"\$[A-Z]+\$\d|RADIANS|^B3|^-A3|servo_\*|\u2026")
    doc_re = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)`\s*$")
    for f in [SKELETON, INSTALL]:
        bad = []
        for i, line in enumerate(open(p(f), encoding="utf-8").read().split("\n"), 1):
            if not dim_kw.search(line) or "is defined in" in line:
                continue
            for m2 in re.finditer(r"`=\s*([^`]+)`", line):
                e = m2.group(1).strip()
                if single.match(e) or exempt.search(e):
                    continue
                before = line[: m2.start()]
                dm = doc_re.search(before)
                if dm and dm.group(1) in nameset:      # restating that global's own equation
                    continue
                bad.append(f"L{i}: `= {e[:60]}`")
        r.check(not bad,
                f"{f}: one-variable rule"
                + ("" if not bad else f" — {len(bad)} expression(s): " + "; ".join(bad[:4])))

    # ---- summary -----------------------------------------------------------
    print()
    if r.fails:
        print(f"FAILED - {len(r.fails)} invariant(s) broken:")
        for x in r.fails:
            print(f"  - {x}")
        return 1
    print(f"OK - all invariants hold ({len(names)} globals)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
