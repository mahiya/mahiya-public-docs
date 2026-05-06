"""Convert Notion-style inline `$$X$$` to standard `$X$` for KaTeX rendering.

Rules:
- Multi-line block math (`$$\\n...\\n$$`) is left untouched.
- A line whose entire trimmed content is `$$X$$` is left as-is (renders as display).
- Otherwise, every single-line `$$...$$` occurrence is rewritten to `$...$`.
- Existing `$..$` (single-dollar) patterns are not modified.

Run from repo root:

    python scripts/fix_inline_math.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Single-line `$$...$$` (no newlines, no nested `$`).
INLINE_MATH = re.compile(r"\$\$([^$\n]+?)\$\$")

# Files known to use Notion-style math. Add new ones here as needed.
TARGETS = [
    "docs/splade/csplade.md",
    "docs/splade/prosper.md",
    "docs/splade/splade_v1.md",
    "docs/splade/splade_v2.md",
    "docs/splade/splade_v3.md",
    "docs/others/agent-memory.md",
]


def convert_line(line: str) -> str:
    stripped = line.strip()
    # Leave a line that is only `$$X$$` alone — KaTeX renders it as display block.
    if INLINE_MATH.fullmatch(stripped):
        return line
    return INLINE_MATH.sub(r"$\1$", line)


def process_file(path: Path) -> bool:
    with path.open("r", encoding="utf-8", newline="") as f:
        content = f.read()

    # Detect dominant newline so we can preserve it on write.
    if "\r\n" in content:
        nl = "\r\n"
    else:
        nl = "\n"
    lines = content.split(nl)

    out: list[str] = []
    in_block = False
    for line in lines:
        if line.strip() == "$$":
            in_block = not in_block
            out.append(line)
            continue
        if in_block:
            out.append(line)
            continue
        out.append(convert_line(line))

    new_content = nl.join(out)
    if new_content == content:
        return False

    with path.open("w", encoding="utf-8", newline="") as f:
        f.write(new_content)
    return True


def main() -> int:
    changed = 0
    for rel in TARGETS:
        path = REPO_ROOT / rel
        if not path.exists():
            print(f"skip (missing): {rel}")
            continue
        if process_file(path):
            print(f"modified: {rel}")
            changed += 1
        else:
            print(f"unchanged: {rel}")
    print(f"\n{changed} file(s) modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
