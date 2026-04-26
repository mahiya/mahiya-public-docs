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

import re
from pathlib import Path

# プロジェクトルート (このファイルの 1 つ上)
ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
SIDEBAR_PATH = ROOT / "_sidebar.md"

# カテゴリ名の表示変換 (ディレクトリ名 → サイドバー上のラベル)
CATEGORY_LABELS: dict[str, str] = {
    "elasticsearch": "Elasticsearch",
    "vector-db": "Vector DB",
}


def extract_title(md_path: Path) -> str:
    """Markdown ファイルから H1 タイトルを抽出する。無ければファイル名 (拡張子なし) を返す。"""
    try:
        with md_path.open("r", encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^#\s+(.+?)\s*$", line)
                if m:
                    return m.group(1).strip()
    except OSError:
        pass
    return md_path.stem


def category_label(dirname: str) -> str:
    """ディレクトリ名をサイドバー上のカテゴリ名に変換。未登録ならハイフン区切りを Title Case 化。"""
    if dirname in CATEGORY_LABELS:
        return CATEGORY_LABELS[dirname]
    return " ".join(part.capitalize() for part in dirname.split("-"))


def relative_link(md_path: Path) -> str:
    """ROOT からの相対パスを Docsify 用のスラッシュ区切り文字列で返す。"""
    rel = md_path.relative_to(ROOT)
    return rel.as_posix()


def is_visible(path: Path) -> bool:
    """先頭が _ や . で始まるパスは除外する。"""
    return not (path.name.startswith("_") or path.name.startswith("."))


def md_sort_key(path: Path) -> tuple[int, str]:
    """README.md を先頭、それ以外はファイル名のアルファベット順でソートするキー。"""
    is_readme = 0 if path.name.lower() == "readme.md" else 1
    return (is_readme, path.name.lower())


def build_sidebar() -> str:
    lines: list[str] = ["- [ホーム](/)", ""]

    if not DOCS_DIR.is_dir():
        lines.append("<!-- docs/ ディレクトリが存在しません -->")
        return "\n".join(lines) + "\n"

    # docs/ 直下の .md (カテゴリ未分類)
    top_level_md = sorted(
        [p for p in DOCS_DIR.glob("*.md") if is_visible(p)],
        key=md_sort_key,
    )
    for md in top_level_md:
        title = extract_title(md)
        lines.append(f"- [{title}]({relative_link(md)})")
    if top_level_md:
        lines.append("")

    # カテゴリディレクトリ
    categories = sorted(
        [d for d in DOCS_DIR.iterdir() if d.is_dir() and is_visible(d)],
        key=lambda d: d.name.lower(),
    )
    for cat in categories:
        md_files = sorted(
            [p for p in cat.rglob("*.md") if is_visible(p)],
            key=lambda p: (p.parent.as_posix().lower(), *md_sort_key(p)),
        )
        if not md_files:
            continue
        lines.append(f"- {category_label(cat.name)}")
        for md in md_files:
            title = extract_title(md)
            lines.append(f"  - [{title}]({relative_link(md)})")
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
