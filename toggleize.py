#!/usr/bin/env python3
"""
toggleize.py - wrap every section of the Markdown guides in nested
<details>/<summary> toggle lists.

    python3 toggleize.py FILE.md [FILE.md ...]

Nesting levels, deepest last:

    ## N.                       -> level 1   (markdown heading kept inside)
    ### / #### / #####          -> level 2/3/4 (markdown heading kept inside)
    **N.x — Title**             -> level 2   (title moves into <summary>)
    **N.x.y — Title**           -> level 3
    * **Phase A — Title**       -> level (parent + 1), body de-indented 2

Markdown headings are preserved verbatim inside their <details> so the
guide's hash-header and H2 count invariants still hold and anchors keep
working. Bold-paragraph subsections were never headings, so their title
moves into the <summary> with no duplication.

Content inside fenced code blocks is never touched.
"""

import re
import sys

H_RE      = re.compile(r"^(#{2,6})\s+(.*)$")
SUB_RE    = re.compile(r"^\*\*(\d+(?:\.\d+)*)\s*—\s*(.+?)\*\*\s*(.*)$")
BULLET_RE = re.compile(r"^\* \*\*(.+?)\*\*\s*(.*)$")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline_html(s):
    """Title -> summary-safe inline HTML."""
    s = esc(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", s)
    s = re.sub(r"\$([^$]*)\$", r"\1", s)          # LaTeX won't render in a summary
    return s.strip().rstrip(".")


def classify(line, stack):
    """-> (level, summary_html, keep_heading, remainder) or None."""
    m = H_RE.match(line)
    if m:
        hashes, title = m.group(1), m.group(2)
        if len(hashes) == 2:
            return 1, f"<b>{inline_html(title)}</b>", True, None
        return len(hashes) - 1, f"<b>{inline_html(title)}</b>", True, None

    m = SUB_RE.match(line)
    if m:
        num, title, rest = m.group(1), m.group(2), m.group(3)
        level = 1 + len(num.split("."))
        return level, f"<b>{esc(num)} — {inline_html(title)}</b>", False, rest

    m = BULLET_RE.match(line)
    if m:
        title, rest = m.group(1), m.group(2)
        if not re.match(r"^(Phase|Step|Route|Path|Method|Group|Part)\b", title):
            return None
        level = (stack[-1] + 1) if stack else 2
        return level, f"<b>{inline_html(title)}</b>", False, rest
    return None


def transform(path):
    src = open(path, encoding="utf-8").read().split("\n")
    out, stack = [], []
    fence = False
    i = 0
    n_open = 0

    def close_to(level):
        while stack and stack[-1] >= level:
            if out and out[-1].strip():
                out.append("")
            out.append("</details>")
            stack.pop()

    while i < len(src):
        line = src[i]

        if line.lstrip().startswith("```"):
            fence = not fence
            out.append(line)
            i += 1
            continue
        if fence:
            out.append(line)
            i += 1
            continue

        info = classify(line, stack)
        if info is None:
            out.append(line)
            i += 1
            continue

        level, summary, keep_heading, rest = info
        close_to(level)

        if out and out[-1].strip():
            out.append("")
        out.append("<details>")
        out.append(f"<summary>{summary}</summary>")
        out.append("")
        n_open += 1
        stack.append(level)

        if keep_heading:
            out.append(line)          # preserve the markdown heading verbatim
        else:
            if rest:
                out.append(rest)
            # a bullet-level block owns the indented lines that follow;
            # de-indent them by 2 so blockquotes stay blockquotes
            if BULLET_RE.match(line):
                i += 1
                while i < len(src):
                    nxt = src[i]
                    if nxt.lstrip().startswith("```"):
                        break
                    if nxt.strip() == "":
                        out.append("")
                        i += 1
                        continue
                    if not nxt.startswith("  "):
                        break
                    out.append(nxt[2:])
                    i += 1
                continue
        i += 1

    close_to(0)
    text = "\n".join(out)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    open(path, "wb").write(text.encode("utf-8"))
    return n_open


if __name__ == "__main__":
    for p in sys.argv[1:]:
        k = transform(p)
        body = open(p, encoding="utf-8").read()
        print(f"{p}: {k} toggles | <details> {body.count('<details>')} "
              f"| </details> {body.count('</details>')} "
              f"| <summary> {body.count('<summary>')}")
