#!/usr/bin/env python3
"""
toggle_steps.py - second toggle pass, for the block level toggleize.py leaves alone.

toggleize.py wraps headings, **N.x —** subsections and `* **Phase …**` bullets.
It does not wrap the bold-paragraph blocks that sit *inside* those, of the form

    **Step 1 — root chord and tip station.**
    1. ...
    2. ...

which are the deepest real structural level in the guides. This pass wraps each
of those in its own <details>, giving the extra nesting rung.

    python3 toggle_steps.py FILE.md [FILE.md ...]

Idempotent: once a block's title has moved into a <summary> there is no
bold-paragraph left at column 0 to match, so re-running is a no-op.

Nothing is reordered and no prose is dropped - the title moves into the
<summary> exactly as toggleize.py does it, and the body is left untouched.
Content inside fenced code blocks is never read.
"""

import html
import re
import sys

# Only column-0 bold paragraphs whose label reads like a build block.
BLOCK_RE = re.compile(
    r"^\*\*((?:Step|Phase|Route|Path|Method|Group|Part)\b[^*]*?)\*\*\s*(.*)$"
)
# Anything that ends the block: a sibling block, a heading, a toggle boundary,
# or a horizontal rule.
STOP_RE = re.compile(r"^(<details>|</details>|<summary>|#{1,6}\s|---\s*$)")


def inline_html(s):
    """Title -> summary-safe inline HTML. Mirrors toggleize.py."""
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", s)
    s = re.sub(r"\$([^$]*)\$", r"\1", s)      # LaTeX will not render in a summary
    return s.strip().rstrip(".")


def transform(path):
    src = open(path, encoding="utf-8").read().split("\n")
    out = []
    fence = False
    i = 0
    added = 0

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

        m = BLOCK_RE.match(line)
        if not m:
            out.append(line)
            i += 1
            continue

        title, rest = m.group(1), m.group(2)

        # collect the body: everything up to the next structural boundary
        j = i + 1
        body = []
        while j < len(src):
            nxt = src[j]
            if nxt.lstrip().startswith("```"):
                # a fenced block belongs to this body; consume it whole
                body.append(nxt)
                j += 1
                while j < len(src) and not src[j].lstrip().startswith("```"):
                    body.append(src[j])
                    j += 1
                if j < len(src):
                    body.append(src[j])
                    j += 1
                continue
            if STOP_RE.match(nxt) or BLOCK_RE.match(nxt):
                break
            body.append(nxt)
            j += 1

        # a block with no body is just a label; leave it exactly as it was
        if not any(b.strip() for b in body):
            out.append(line)
            i += 1
            continue

        if out and out[-1].strip():
            out.append("")
        out.append("<details>")
        out.append(f"<summary><b>{inline_html(title)}</b></summary>")
        out.append("")
        if rest.strip():
            out.append(rest)
        while body and not body[-1].strip():
            body.pop()
        out.extend(body)
        out.append("")
        out.append("</details>")
        added += 1
        i = j

    text = "\n".join(out)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    open(path, "wb").write(text.encode("utf-8"))
    return added


if __name__ == "__main__":
    for p in sys.argv[1:]:
        n = transform(p)
        body = open(p, encoding="utf-8").read()
        o, c = body.count("<details>"), body.count("</details>")
        print(f"{p}: +{n} toggles | <details> {o} | </details> {c} | balanced={o == c}")
