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
import math
import os
import re
import sys

# ---- baselines ----------------------------------------------------------
HASH_HEADERS_SKELETON = 25      # count of ^#{3,} in the SKELETON guide
H2_SKELETON           = 15      # count of ^## in the SKELETON guide
GLOBAL_COUNT          = 247     # definitions in skeleton_equations_micro.txt

# THE POSITIVE-MAGNITUDE RULE: no value in the equations file may be negative,
# angles included. Direction belongs to the model (dimension side, plane Flip,
# pattern arrow), never to a stored sign. There are no exemptions -- do not add
# one here to silence a failure; fix the value and carry the direction in the
# geometry instead. A minus OPERATOR inside a formula is fine.

# THE RADIANS RULE: SolidWorks' "Angular equation units" drop-down (Tools >
# Equations) must be set to Radians, because every trig call in the equations
# file converts its own argument with * pi/180. That drop-down is per-document
# and DEFAULTS TO DEGREES, which converts a second time and silently collapses
# every swept station toward zero -- no error, just wrong geometry. check.py
# cannot read the drop-down; it enforces the half it can see, namely that no
# trig call is ever written without its conversion. If the document is ever
# switched to Degrees, this check must be INVERTED, not deleted.
TRIG = re.compile(r"\b(sin|cos|tan|asin|acos|atan|sec|cosec|cotan)\s*\(")

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
    neg = [n for n, rhs in defs if rhs.lstrip().startswith("-")]
    r.check(not neg,
            "positive-magnitude rule: no negative values"
            + ("" if not neg else f" -- {len(neg)} found: " + ", ".join(neg)))

    # definition order: SolidWorks evaluates the list top-down, so a global may
    # never reference one defined below it. Nothing else catches this, and it is
    # the failure mode that a derivation-direction change introduces.
    seen, fwd = set(), []
    for n, rhs in defs:
        for ref in re.findall(r'"([A-Za-z_][A-Za-z0-9_]*)"', rhs):
            if ref not in seen:
                fwd.append(f"{n} <- {ref}")
        seen.add(n)
    r.check(not fwd,
            "definition order: no forward references"
            + ("" if not fwd else f" -- {len(fwd)}: " + "; ".join(fwd[:4])))

    # radians rule: every trig argument carries its own pi/180 conversion
    badtrig = []
    for n, rhs in defs:
        for m in TRIG.finditer(rhs):
            depth, j = 1, m.end()
            while j < len(rhs) and depth:
                if rhs[j] == "(":
                    depth += 1
                elif rhs[j] == ")":
                    depth -= 1
                j += 1
            if not re.search(r"pi\s*/\s*180", rhs[m.end():j - 1]):
                badtrig.append(n)
    badtrig = sorted(set(badtrig))
    r.check(not badtrig,
            "radians rule: every trig argument converted with pi/180"
            + ("" if not badtrig else f" -- missing in {len(badtrig)}: " + ", ".join(badtrig)))

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

    # ---- 6. evaluated-value invariants -------------------------------------
    # Everything above is textual. This block resolves the equation graph and
    # checks the results, because a value can be perfectly well-formed and still
    # describe an aeroplane that will not fly.
    print("\nevaluated values")
    env = dict(sin=math.sin, cos=math.cos, tan=math.tan,
               sqr=math.sqrt, abs=abs, pi=math.pi)
    vals, pending = {}, list(defs)
    for _ in range(len(defs) + 2):
        still = []
        for n, rhs in pending:
            e = re.sub(r'"([A-Za-z_][A-Za-z0-9_]*)"', r'V["\1"]', rhs.replace("^", "**"))
            try:
                vals[n] = eval(e, {"__builtins__": {}}, dict(env, V=vals))
            except Exception:
                still.append((n, rhs))
        prev = len(pending)
        pending = still
        if not pending or len(pending) == prev:
            break

    need = ("SM", "SM_min", "SM_max")
    if all(k in vals for k in need):
        sm, lo, hi = vals["SM"], vals["SM_min"], vals["SM_max"]
        r.check(lo <= sm <= hi,
                f"static margin {sm:.4f} within [{lo:.2f}, {hi:.2f}]")
    else:
        r.fail("static margin: SM / SM_min / SM_max did not resolve")

    if pending:
        r.check(False, f"{len(pending)} global(s) did not evaluate: "
                       + ", ".join(n for n, _ in pending[:5]))
    else:
        r.ok(f"all {len(vals)} globals evaluate")

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
