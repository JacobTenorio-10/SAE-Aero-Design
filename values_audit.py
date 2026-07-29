#!/usr/bin/env python3
"""
values_audit.py - build Values_Audit.md

Finds every numeric literal in the guides that duplicates a global's value.
Each one is a second copy of a fact whose master lives in
skeleton_equations_micro.txt, with no link back - so it goes stale silently
the moment the global changes. That is the mechanism that left the §3 station
block two revisions behind.

    python3 values_audit.py                       # read and write in cwd
    python3 values_audit.py --dir path -o OUT.md

Fix pattern: replace the literal with a citation of the global name, or - if
the number genuinely helps the reader - mark it non-normative, e.g.
*(≈19.05)*, so a stale one is visibly informational rather than authoritative.

Risk tiers
  HIGH    >=3 decimal places, or >=4 digits. Almost certainly a restatement;
          silently wrong the moment the global moves.
  MEDIUM  2 decimals, or a 3-digit integer. Usually a restatement.
  LOW     small integers, or a value shared by many globals. Mostly step
          numbers, counts and prose - review, don't bulk-edit.
"""

import argparse
import os
import re

EQUATIONS = "skeleton_equations_micro.txt"
DOCS = [
    ("SKELETON", "Skeleton_Sketch_Part_Guide_Micro.md"),
    ("INSTALL",  "Installation_Layout_Guide_Micro.md"),
]

SECTION_RE = re.compile(r"^(?:(#{2,})\s*(.+?)\s*$|\*\*(\d+\.[\d.]*)\s*—\s*(.+?)\*\*)")
NUM_RE = re.compile(r"(?<![\w.$])(\d+\.\d+|\d+)(?![\w.])")


def parse_equations(path):
    txt = open(path, "rb").read().decode("utf-8-sig")
    vals = {}
    for line in txt.split("\r\n"):
        m = re.match(r'^"([^"]+)"\s*=\s*([-\d.]+)\s*(?:\'|$)', line)
        if m:
            try:
                vals[m.group(1)] = float(m.group(2))
            except ValueError:
                pass
    return vals


def section_label(line):
    m = SECTION_RE.match(line)
    if not m:
        return None
    return m.group(2).strip() if m.group(1) else f"{m.group(3)} — {m.group(4).strip()}"


def tier(literal, value, owners):
    """HIGH / MEDIUM / LOW risk that this literal is a stale-prone restatement."""
    if len(owners) > 2:
        return "LOW"
    if "." in literal:
        dec = len(literal.split(".")[1])
        if dec >= 3:
            return "HIGH"
        if dec == 2:
            return "HIGH" if len(literal.replace(".", "")) >= 5 else "MEDIUM"
        return "MEDIUM" if value >= 10 else "LOW"
    if len(literal) >= 4:
        return "HIGH"
    if len(literal) == 3:
        return "MEDIUM"
    return "LOW"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".")
    ap.add_argument("-o", "--out", default="Values_Audit.md")
    args = ap.parse_args()
    d = args.dir

    vals = parse_equations(os.path.join(d, EQUATIONS))
    by_value = {}
    for k, v in vals.items():
        by_value.setdefault(v, []).append(k)

    rows = []
    for tag, fn in DOCS:
        path = os.path.join(d, fn)
        if not os.path.exists(path):
            continue
        current, in_fence = "(front matter)", False
        for i, line in enumerate(open(path, encoding="utf-8").read().split("\n"), 1):
            if line.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            lbl = section_label(line)
            if lbl:
                current = lbl
            # a literal directly inside a global citation is fine - it IS the
            # equation. Only bare prose literals are restatements.
            stripped = re.sub(r'`=\s*"[^"]*"[^`]*`', "", line)
            for m in NUM_RE.finditer(stripped):
                lit = m.group(1)
                try:
                    v = float(lit)
                except ValueError:
                    continue
                if v in by_value:
                    owners = by_value[v]
                    rows.append({
                        "doc": tag, "line": i, "sec": current, "lit": lit,
                        "owners": owners, "tier": tier(lit, v, owners),
                        "ctx": stripped.strip()[:150],
                    })

    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    rows.sort(key=lambda r: (order[r["tier"]], r["doc"], r["line"]))
    counts = {t: sum(1 for r in rows if r["tier"] == t) for t in order}

    out = ["# Inline Values Audit", ""]
    out.append("**Generated file — do not edit by hand.** Rebuild with "
               "`python3 values_audit.py`.")
    out.append("")
    out.append("Every row is a numeric literal in a guide that duplicates a global's "
               "value. The master copy lives in `skeleton_equations_micro.txt`; these "
               "copies have no link back to it, so they go stale silently. Converting "
               "the HIGH rows to global citations is what stops most guide edits from "
               "being necessary at all.")
    out.append("")
    out.append(f"| Tier | Count | Meaning |")
    out.append("|---|---|---|")
    out.append(f"| HIGH | {counts['HIGH']} | ≥3 decimals or ≥4 digits — convert these first |")
    out.append(f"| MEDIUM | {counts['MEDIUM']} | 2 decimals or 3-digit integer — usually a restatement |")
    out.append(f"| LOW | {counts['LOW']} | small integers / shared values — mostly prose, review individually |")
    out.append(f"| **Total** | **{len(rows)}** | across {len({r['sec'] for r in rows})} sections |")
    out.append("")

    hot = {}
    for r in rows:
        if r["tier"] in ("HIGH", "MEDIUM"):
            hot[r["sec"]] = hot.get(r["sec"], 0) + 1
    if hot:
        out.append("## Sections carrying the most restatements (HIGH + MEDIUM)")
        out.append("")
        out.append("| Section | Count |")
        out.append("|---|---|")
        for sec, n in sorted(hot.items(), key=lambda x: -x[1])[:15]:
            out.append(f"| {sec} | {n} |")
        out.append("")

    for t in ("HIGH", "MEDIUM", "LOW"):
        sub = [r for r in rows if r["tier"] == t]
        if not sub:
            continue
        out.append(f"## {t} — {len(sub)} literal(s)")
        out.append("")
        out.append("| Doc | Line | Section | Literal | Duplicates | Context |")
        out.append("|---|---|---|---|---|---|")
        for r in sub:
            owners = ", ".join(f"`{o}`" for o in r["owners"])
            ctx = r["ctx"].replace("|", "\\|")
            out.append(f"| {r['doc']} | {r['line']} | {r['sec'][:44]} | `{r['lit']}` | {owners} | {ctx} |")
        out.append("")

    open(os.path.join(d, args.out), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"wrote {args.out}: {len(rows)} literals "
          f"(HIGH {counts['HIGH']}, MEDIUM {counts['MEDIUM']}, LOW {counts['LOW']})")


if __name__ == "__main__":
    main()
