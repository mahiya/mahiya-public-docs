"""
docs/ 配下のドキュメントツリーを扱う共通ヘルパー。

gen_sidebar.py / gen_index.py から共有される。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator

# プロジェクトルート (このファイルの 1 つ上)
ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"

# カテゴリ名の表示変換 (ディレクトリ名 → サイドバー / 索引上のラベル)
CATEGORY_LABELS: dict[str, str] = {
    "elasticsearch": "Elasticsearch",
    "vector-db": "Vector DB",
    "vectordb": "Vector DB",
    "reranker": "Reranker",
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
    """ディレクトリ名をカテゴリ表示名に変換。未登録ならハイフン区切りを Title Case 化。"""
    if dirname in CATEGORY_LABELS:
        return CATEGORY_LABELS[dirname]
    return " ".join(part.capitalize() for part in dirname.split("-"))


def relative_link(md_path: Path) -> str:
    """ROOT からの相対パスを Docsify 用のスラッシュ区切り文字列で返す。"""
    return md_path.relative_to(ROOT).as_posix()


def is_visible(path: Path) -> bool:
    """先頭が _ や . で始まるパスは除外する。"""
    return not (path.name.startswith("_") or path.name.startswith("."))


def md_sort_key(path: Path) -> tuple[int, str]:
    """README.md を先頭、それ以外はファイル名のアルファベット順でソートするキー。"""
    is_readme = 0 if path.name.lower() == "readme.md" else 1
    return (is_readme, path.name.lower())


def iter_top_level_md() -> Iterator[Path]:
    """docs/ 直下の .md ファイル (カテゴリ未分類) を順番にイテレート。"""
    if not DOCS_DIR.is_dir():
        return
    files = sorted(
        [p for p in DOCS_DIR.glob("*.md") if is_visible(p)],
        key=md_sort_key,
    )
    yield from files


def iter_categories() -> Iterator[tuple[Path, list[Path]]]:
    """カテゴリディレクトリと、その配下の .md ファイル一覧をイテレート。"""
    if not DOCS_DIR.is_dir():
        return
    categories = sorted(
        [d for d in DOCS_DIR.iterdir() if d.is_dir() and is_visible(d)],
        key=lambda d: d.name.lower(),
    )
    for cat in categories:
        md_files = sorted(
            [p for p in cat.rglob("*.md") if is_visible(p)],
            key=lambda p: (p.parent.as_posix().lower(), *md_sort_key(p)),
        )
        if md_files:
            yield cat, md_files
