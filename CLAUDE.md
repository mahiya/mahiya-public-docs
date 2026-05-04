# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## このリポジトリについて

技術調査・検証レポートを集めた **Docsify** ベースの公開ドキュメントサイト (GitHub Pages 配信)。ビルドステップは無く、`index.html` と Markdown を置くだけで成立する。Python スクリプト群はサイトのナビゲーション (`_sidebar.md`) と索引 (`README.md` のドキュメント一覧) を `docs/` ツリーから自動再生成するためのもの。

## 主要コマンド

リポジトリルートから実行する。両スクリプトとも冪等。

```bash
python scripts/gen_sidebar.py   # _sidebar.md を再生成
python scripts/gen_index.py     # README.md の <!-- DOCS_LIST:START/END --> 内を再生成
```

ローカルプレビューは `index.html` を任意の静的サーバーで配信する (例: `python -m http.server`)。

リリース時の定型ワークフロー (索引再生成 → gitleaks スキャン → コミット → push) は `.claude/skills/pre-push/` にスキル化済み。「push して」「pre-push を実行」等のフレーズで起動する。`.claude/settings.json` で `Bash(git push:*)` を allow / `git push --force*` を deny しているのが前提。`Co-Authored-By: Claude ...` トレーラーは Anthropic のセーフガードで拒否されるため、コミットメッセージには付けない。

## アーキテクチャ

### ドキュメントツリーの規約 (重要)

`scripts/_common.py` に集約されたルールが `gen_sidebar.py` / `gen_index.py` の両方を駆動する。新ページを追加するときは以下に従う。

- **配置**: `docs/<category>/<page>.md`。カテゴリディレクトリが見出しグループになる。`docs/` 直下に置いた `.md` は「カテゴリ未分類」として上部に並ぶ。
- **タイトル**: 各ファイルの先頭 `# ...` (H1) がサイドバーと索引のリンクテキストになる。H1 が無ければファイル名 (拡張子なし) にフォールバック。
- **ソート順**: 各カテゴリ内のファイルはアルファベット順 (`README.md` は強制的に先頭)。カテゴリ間の並びは `_common.py` の `CATEGORY_PRIORITY` dict が決める — 値が小さいほど上、大きいほど下、未指定は `DEFAULT_PRIORITY` (100)。HTML ページセクションは `HTML_PRIORITY` (500)。同じ優先度内ではアルファベット順。例: `others` は 1000 を割り当てられているため最下段に来る。並び順を変えたいときはこの dict を編集する。
- **除外**: ファイル名が `_` または `.` で始まるものは無視 (`_sidebar.md` 自身など)。
- **カテゴリ表示名**: ディレクトリ名 → 表示ラベルの変換は `_common.py` の `CATEGORY_LABELS` dict で行う。未登録ならハイフン区切りを Title Case 化 (例: `vector-db` → `Vector DB`)。新カテゴリで特殊な表記が必要なら ここに追加する。
- **HTML ページ**: `htmls/` 配下の `.html` は別セクション (`HTML ページ`) として、カテゴリと同じ優先度キューに混ざって出力される。Docsify の SPA ルーターに食われないよう `':ignore :target=_blank'` リンクオプションが自動付与される (`HTML_LINK_OPTS`)。
- **セクション統合**: カテゴリと HTML ページは `iter_sections()` が `(優先度, ラベル)` でソートして単一の列として yield する — 両ジェネレータはこの結果をそのまま流すだけ。
- **`<title>` 抽出**: HTML ファイルからは `<title>` → `<h1>` → ファイル名の順でラベルを決定する。

### 自動生成の境界

`README.md` は **マーカー外の本文を一切変更しない**。`gen_index.py` は `<!-- DOCS_LIST:START -->` と `<!-- DOCS_LIST:END -->` の間だけを差し替える (マーカーが無ければ末尾に追記)。手書きで序文や使い方を README に追加するのは安全。

`_sidebar.md` は全体が生成物 — 手で編集しても次回の `gen_sidebar.py` で上書きされる。

### Docsify の設定

`index.html` に GitHub Dark 風のカスタムテーマと `$docsify` 設定が同居する。プラグインは search / pagination / copy-code / Prism (bash, python, yaml, json, markdown) を CDN 経由でロード。`alias` で全パスの `_sidebar.md` を ルート の `_sidebar.md` に解決させているため、サブディレクトリごとのサイドバー切り替えは行っていない。

`_coverpage.md` は Docsify のカバーページだが、現状の `$docsify.coverpage` は無効 (有効化したい場合は `index.html` に `coverpage: true` を追加)。

## このリポジトリで作業するときのコツ

- Markdown ページを追加・改名・移動したら、コミット前に必ず `python scripts/gen_sidebar.py` と `python scripts/gen_index.py` を流す (pre-push スキルが自動でやる)。
- 新カテゴリディレクトリを作るときは、表示名が崩れていないか `CATEGORY_LABELS` を確認する。
- `git add -A` / `git add .` は使わず、関連ファイルのみを個別にステージする方針 (pre-push スキルに従う)。`__pycache__/` は `.gitignore` 済みだが念のため目視確認。
