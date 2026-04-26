"""
docs/ 配下を走査して README.md のドキュメント一覧セクションを自動更新するスクリプト。

使い方:
    python scripts/gen_index.py

仕組み:
- README.md 内の <!-- DOCS_LIST:START --> ... <!-- DOCS_LIST:END --> の間を更新
- マーカーが見つからない場合、末尾に "## ドキュメント一覧" セクションを追加してマーカー込みで挿入
- 既存の README 本文 (マーカー外の部分) は一切変更しない
"""

from __future__ import annotations

import re

from _common import (
    ROOT,
    category_label,
    extract_title,
    iter_categories,
    iter_top_level_md,
    relative_link,
)

README_PATH = ROOT / "README.md"
START_MARKER = "<!-- DOCS_LIST:START -->"
END_MARKER = "<!-- DOCS_LIST:END -->"


def build_index_body() -> str:
    """マーカー間に挿入するドキュメント一覧本文を組み立てる。"""
    lines: list[str] = []

    # docs/ 直下の .md (カテゴリ未分類)
    top_level = list(iter_top_level_md())
    for md in top_level:
        title = extract_title(md)
        lines.append(f"- [{title}]({relative_link(md)})")
    if top_level:
        lines.append("")

    # カテゴリ別
    for cat, md_files in iter_categories():
        lines.append(f"### {category_label(cat.name)}")
        lines.append("")
        for md in md_files:
            title = extract_title(md)
            lines.append(f"- [{title}]({relative_link(md)})")
        lines.append("")

    # 末尾の空行を整理
    while lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)


def update_readme(original: str, body: str) -> str:
    block = f"{START_MARKER}\n\n{body}\n\n{END_MARKER}"

    if START_MARKER in original and END_MARKER in original:
        # 既存マーカーの間を置換
        pattern = re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER)
        return re.sub(pattern, block, original, count=1, flags=re.DOTALL)

    # マーカーが無い場合は末尾に追加
    suffix = "" if original.endswith("\n") else "\n"
    return f"{original}{suffix}\n## ドキュメント一覧\n\n{block}\n"


def main() -> None:
    if README_PATH.exists():
        original = README_PATH.read_text(encoding="utf-8")
    else:
        original = "# Mahiya Public Docs\n"

    body = build_index_body()
    new_content = update_readme(original, body)

    README_PATH.write_text(new_content, encoding="utf-8", newline="\n")
    print(f"Wrote {README_PATH.relative_to(ROOT)} ({len(new_content)} bytes)")


if __name__ == "__main__":
    main()
