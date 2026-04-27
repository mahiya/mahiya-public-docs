"""
docs/ 配下を走査して _sidebar.md を自動生成するスクリプト。

使い方:
    python scripts/gen_sidebar.py

ルール:
- docs/<category>/<page>.md を「カテゴリ → ページ」の階層に変換
- 各 .md の H1 (# ...) をリンクテキストとして使う。無ければファイル名を使う
- アンダースコア始まりのファイル (_sidebar.md など) は無視
- ファイル/ディレクトリ名のアルファベット順でソート (ただし README.md は各カテゴリの先頭に固定)
"""

from __future__ import annotations

from _common import (
    HTML_LINK_OPTS,
    ROOT,
    category_label,
    extract_html_title,
    extract_title,
    iter_categories,
    iter_htmls,
    iter_top_level_md,
    relative_link,
)

SIDEBAR_PATH = ROOT / "_sidebar.md"


def build_sidebar() -> str:
    lines: list[str] = ["- [ホーム](/)", ""]

    # docs/ 直下の .md (カテゴリ未分類)
    top_level = list(iter_top_level_md())
    for md in top_level:
        title = extract_title(md)
        lines.append(f"- [{title}]({relative_link(md)})")
    if top_level:
        lines.append("")

    # カテゴリディレクトリ
    for cat, md_files in iter_categories():
        lines.append(f"- {category_label(cat.name)}")
        for md in md_files:
            title = extract_title(md)
            lines.append(f"  - [{title}]({relative_link(md)})")
        lines.append("")

    # HTML ページ (htmls/ 配下)
    htmls = list(iter_htmls())
    if htmls:
        lines.append("- HTML ページ")
        for html in htmls:
            title = extract_html_title(html)
            lines.append(f"  - [{title}]({relative_link(html)}{HTML_LINK_OPTS})")
        lines.append("")

    # 末尾の余分な空行を 1 つに
    while len(lines) >= 2 and lines[-1] == "" and lines[-2] == "":
        lines.pop()
    if lines and lines[-1] != "":
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    content = build_sidebar()
    SIDEBAR_PATH.write_text(content, encoding="utf-8", newline="\n")
    print(f"Wrote {SIDEBAR_PATH.relative_to(ROOT)} ({len(content)} bytes)")


if __name__ == "__main__":
    main()
