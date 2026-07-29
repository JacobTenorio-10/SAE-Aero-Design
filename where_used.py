#!/usr/bin/env python3
"""
where_used.py - build Global_Where_Used.md

A reverse index: for every global in skeleton_equations_micro.txt, every
section of every document that cites it. Regenerate after any edit; the file
is derived, so it can never drift.

    python3 where_used.py                       # read and write in cwd
    python3 where_used.py --dir path -o OUT.md

Workflow: you change a value in SolidWorks, look the global up here, and go
straight to the sections that need touching. No searching.
"""

import argparse
import os
import re

EQUATIONS = "skeleton_equations_micro.txt"
DOCS = [
    ("SKELETON", "Skeleton_Sketch_Part_Guide_Micro.md"),
    ("INSTALL",  "Installation_Layout_Guide_Micro.md"),
    ("PARAMS",   "Aircraft_Skeleton_Parameters_Micro.md"),
]

# Section openers, in the house style: H2, hash-headers, and bold-para
# subsections like **7.3.6 — ...**
SECTION_RE = re.compile(r"^(?:(#{2,})\s*(.+?)\s*$|\*\*(\d+\.[\d.]*)\s*—\s*(.+?)\*\*)")


def parse_equations(path):
    txt = open(path, "rb").read().decode("utf-8-sig")
    defs = []
    for line in txt.split("\r\n"):
        m = re.match(r'^"([^"]+)"\s*=\s*(.*?)(?:\s+\'(.*))?$', line)
        if m:
            name, rhs, comment = m.group(1), m.group(2).strip(), (m.group(3) or "").strip()
            derived = '"' in rhs
            defs.append({"name": name, "rhs": rhs, "comment": comment, "derived": derived})
    return defs, txt


def section_label(line):
    m = SECTION_RE.match(line)
    if not m:
        return None
    if m.group(1):
        return m.group(2).strip()
    return f"{m.group(3)} — {m.group(4).strip()}"


def code_spans(line):
    return re.findall(r"`([^`]*)`", line) + re.findall(r'"([^"]*)"', line)


def scan(path, names):
    """-> {global: [(section, line_no), ...]} preserving document order."""
    text = open(path, encoding="utf-8").read()
    hits = {}
    current = "(front matter)"
    in_fence = False
    for i, line in enumerate(text.split("\n"), 1):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:                     # Appendix A is the equations file
            continue
        lbl = section_label(line)
        if lbl:
            current = lbl
        seen = set()
        for span in code_spans(line):
            for ident in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", span):
                if ident in names and ident not in seen:
                    seen.add(ident)
                    hits.setdefault(ident, [])
                    if not hits[ident] or hits[ident][-1][0] != current:
                        hits[ident].append((current, i))
    return hits


def trunc(s, n):
    return s if len(s) <= n else s[: n - 1] + "…"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".")
    ap.add_argument("-o", "--out", default="Global_Where_Used.md")
    args = ap.parse_args()
    d = args.dir

    defs, _ = parse_equations(os.path.join(d, EQUATIONS))
    names = {x["name"] for x in defs}

    per_doc = {}
    for tag, fn in DOCS:
        path = os.path.join(d, fn)
        per_doc[tag] = scan(path, names) if os.path.exists(path) else {}

    # dependency map: which globals consume this one in the equations file
    consumers = {n: [] for n in names}
    for x in defs:
        for ref in re.findall(r'"([A-Za-z_][A-Za-z0-9_]*)"', x["rhs"]):
            if ref in consumers:
                consumers[ref].append(x["name"])

    orphans, out = [], []
    out.append("# Global Where-Used Index")
    out.append("")
    out.append("**Generated file — do not edit by hand.** Rebuild with "
               "`python3 where_used.py` after any change to "
               "`skeleton_equations_micro.txt` or the guides.")
    out.append("")
    out.append("Look up the global you changed; the *Cited in* column lists every "
               "section that has to agree with it. `Feeds` lists other globals whose "
               "equations consume it — those re-derive automatically, but their "
               "consumers may still need prose updates.")
    out.append("")
    out.append(f"- Globals defined: **{len(defs)}**")

    for x in defs:
        n = x["name"]
        cites = sum(len(per_doc[t].get(n, [])) for t, _ in DOCS)
        if cites == 0 and not consumers[n]:
            orphans.append(n)

    out.append(f"- Orphans (cited nowhere, consumed by nothing): **{len(orphans)}**")
    out.append("")

    # documented in the parameter reference but never used in a build step
    doc_only = []
    for x in defs:
        n = x["name"]
        if n in orphans:
            continue
        built = per_doc["SKELETON"].get(n) or per_doc["INSTALL"].get(n)
        if not built and per_doc["PARAMS"].get(n):
            doc_only.append(n)
    out.append(f"- Documented but never built: **{len(doc_only)}**")
    out.append("")

    if orphans:
        out.append("## Orphans — defined but unused")
        out.append("")
        out.append("Each is either a documentation defect (the guide drives that "
                   "geometry from something else) or a global you can delete.")
        out.append("")
        out.append("| Global | Value | Comment |")
        out.append("|---|---|---|")
        for n in orphans:
            x = next(y for y in defs if y["name"] == n)
            out.append(f"| `{n}` | {x['rhs']} | {trunc(x['comment'], 90)} |")
        out.append("")

    if doc_only:
        out.append("## Documented but never built")
        out.append("")
        out.append("Listed in the parameter reference, but **no guide step ever "
                   "dimensions anything to them**. Either the geometry is driven "
                   "from a different global (so the comment here is misleading), "
                   "or a build step is missing. Check each against the guide before "
                   "trusting its comment.")
        out.append("")
        out.append("| Global | Value | Comment |")
        out.append("|---|---|---|")
        for n in doc_only:
            x = next(y for y in defs if y["name"] == n)
            out.append(f"| `{n}` | {x['rhs']} | {trunc(x['comment'], 90)} |")
        out.append("")

    out.append("## Index")
    out.append("")
    out.append("| Global | Kind | Value / equation | Feeds | Cited in |")
    out.append("|---|---|---|---|---|")
    for x in defs:
        n = x["name"]
        kind = "derived" if x["derived"] else "input"
        refs = []
        for tag, _ in DOCS:
            for sec, line in per_doc[tag].get(n, []):
                refs.append(f"{tag} §{trunc(sec, 46)} (L{line})")
        feeds = ", ".join(f"`{c}`" for c in consumers[n]) or "—"
        cited = "<br>".join(refs) if refs else "**— nowhere —**"
        rhs = x["rhs"].replace("|", "\\|")
        out.append(f"| `{n}` | {kind} | `{trunc(rhs, 44)}` | {feeds} | {cited} |")
    out.append("")

    open(os.path.join(d, args.out), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"wrote {args.out}: {len(defs)} globals, {len(orphans)} orphans")
    if orphans:
        print("orphans: " + ", ".join(orphans))


if __name__ == "__main__":
    main()
