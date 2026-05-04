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
HTMLS_DIR = ROOT / "htmls"

# カテゴリ名の表示変換 (ディレクトリ名 → サイドバー / 索引上のラベル)
CATEGORY_LABELS: dict[str, str] = {
    "elasticsearch": "Elasticsearch",
    "vector-db": "Vector DB",
    "vectordb": "Vector DB",
    "reranker": "Reranker モデル",
    "hfblogs": "Hugging Face Community Blogs",
}

# セクションの並び順を上書きする優先度。小さいほど上、大きいほど下。
# 未指定のカテゴリは DEFAULT_PRIORITY (100) として扱われ、その中ではアルファベット順。
# HTML ページセクションは HTML_PRIORITY (500) を使う。
CATEGORY_PRIORITY: dict[str, int] = {
    "others": 1000,  # Others は最後
}
DEFAULT_PRIORITY = 100
HTML_PRIORITY = 500  # HTML ページセクションの優先度 (Others より上に出る)

# Docsify のルーターに HTML パスを解釈させないためのリンクオプション。
# 別タブで開き、SPA の history を汚さない。
HTML_LINK_OPTS = " ':ignore :target=_blank'"

# iter_sections() が返すセクション種別の識別子
KIND_MD = "md"
KIND_HTML = "html"
HTML_SECTION_LABEL = "HTML ページ"


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


def extract_html_title(html_path: Path) -> str:
    """HTML ファイルから <title> を抽出する。無ければ最初の <h1>、それも無ければファイル名。"""
    try:
        text = html_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return html_path.stem
    m = re.search(r"<title>\s*(.*?)\s*</title>", text, flags=re.IGNORECASE | re.DOTALL)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(r"<h1[^>]*>\s*(.*?)\s*</h1>", text, flags=re.IGNORECASE | re.DOTALL)
    if m:
        # タグを雑に剥がす
        return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return html_path.stem


def category_label(dirname: str) -> str:
    """ディレクトリ名をカテゴリ表示名に変換。未登録ならハイフン区切りを Title Case 化。"""
    if dirname in CATEGORY_LABELS:
        return CATEGORY_LABELS[dirname]
    return " ".join(part.capitalize() for part in dirname.split("-"))


def category_priority(dirname: str) -> int:
    """ディレクトリ名の表示優先度を返す。未登録なら DEFAULT_PRIORITY。"""
    return CATEGORY_PRIORITY.get(dirname, DEFAULT_PRIORITY)


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
    """カテゴリディレクトリと、その配下の .md ファイル一覧をイテレート。

    並び順は (CATEGORY_PRIORITY, ディレクトリ名) の辞書順。優先度が同じカテゴリは
    アルファベット順になる。
    """
    if not DOCS_DIR.is_dir():
        return
    categories = sorted(
        [d for d in DOCS_DIR.iterdir() if d.is_dir() and is_visible(d)],
        key=lambda d: (category_priority(d.name), d.name.lower()),
    )
    for cat in categories:
        md_files = sorted(
            [p for p in cat.rglob("*.md") if is_visible(p)],
            key=lambda p: (p.parent.as_posix().lower(), *md_sort_key(p)),
        )
        if md_files:
            yield cat, md_files


def iter_htmls() -> Iterator[Path]:
    """htmls/ 配下の .html ファイルを順番にイテレート。"""
    if not HTMLS_DIR.is_dir():
        return
    files = sorted(
        [p for p in HTMLS_DIR.rglob("*.html") if is_visible(p)],
        key=lambda p: p.name.lower(),
    )
    yield from files


def iter_sections() -> Iterator[tuple[str, str, list[Path]]]:
    """全セクション (カテゴリ + HTML ページ) を優先度順に yield する。

    Returns: (表示ラベル, 種別 KIND_MD/KIND_HTML, ファイル一覧)。
    優先度が同じ場合はラベル文字列でタイブレーク。
    """
    sections: list[tuple[int, str, str, list[Path]]] = []

    for cat, md_files in iter_categories():
        sections.append((category_priority(cat.name), category_label(cat.name), KIND_MD, md_files))

    htmls = list(iter_htmls())
    if htmls:
        sections.append((HTML_PRIORITY, HTML_SECTION_LABEL, KIND_HTML, htmls))

    sections.sort(key=lambda s: (s[0], s[1].lower()))
    for _, label, kind, files in sections:
        yield label, kind, files
