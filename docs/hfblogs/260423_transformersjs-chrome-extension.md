# Transformers.js を Chrome 拡張機能で使う：Gemma 4 ブラウザアシスタントの設計

## 発行元
- **発行組織**: Hugging Face
- **著者**: Nico Martin (nico-martin)
- **発行日**: 2026-04-23
- **URL**: https://huggingface.co/blog/transformersjs-chrome-extension

## 一言概要
Manifest V3 (MV3) 制約下で Transformers.js を組み込み、Gemma 4 と MiniLM を Background Service Worker で動かして Side Panel からチャット操作する Chrome 拡張機能のアーキテクチャを詳細解説したガイドにゃ。

## ブログで説明している内容

- **Chrome 拡張機能 (MV3) のアーキテクチャ**
  - 3 つの実行コンテキスト: Background (`background.js`)、Side Panel (`sidebar.html`)、Content Script (`content.js`)
  - 責務分離: Background = 制御平面・モデル実行、Side Panel = UI、Content Script = DOM 抽出/ハイライト
  - 会話履歴は Background の `Agent.chatMessages` に集中保持
- **メッセージング契約**
  - Side Panel → Background: `CHECK_MODELS`, `INITIALIZE_MODELS`, `AGENT_INITIALIZE`, `AGENT_GENERATE_TEXT`, `AGENT_GET_MESSAGES`, `AGENT_CLEAR`, `EXTRACT_FEATURES`
  - Background → Side Panel: `DOWNLOAD_PROGRESS`, `MESSAGES_UPDATE`
  - Background → Content: `EXTRACT_PAGE_DATA`, `HIGHLIGHT_ELEMENTS`, `CLEAR_HIGHLIGHTS`
- **Transformers.js 統合**
  - テキスト生成: `onnx-community/gemma-4-E2B-it-ONNX` (q4f16, WebGPU)
  - 埋め込み: `onnx-community/all-MiniLM-L6-v2-ONNX` (fp32)
  - 全推論を Background で集約 → 全タブで単一ホスト共有、メモリ重複を回避
- **モデルダウンロード/キャッシュライフサイクル**
  - `CHECK_MODELS` → キャッシュ確認 → `INITIALIZE_MODELS` → `DOWNLOAD_PROGRESS` を UI に送信
  - キャッシュは `chrome-extension://<extension-id>` 配下
- **パーミッション設計**
  - `permissions`: `sidePanel`, `storage`, `scripting`, `tabs`
  - `host_permissions`: `http://*/*`, `https://*/*`
- **Agent とツール実行ループ**
  - 内部モデルトランスクリプト (`messages`) と UI トランスクリプト (`chatMessages`) の二層構造
  - ツールスキーマを `tools` で渡し、`<|tool_call>...<tool_call|>` を `extractToolCalls.ts` でパース
  - 実装ツール: `get_open_tabs`, `go_to_tab`, `open_url`, `close_tab`, `find_history`, `ask_website`, `highlight_website_element`
- **データ境界と永続化**
  - 会話状態: Background メモリ (`Agent.chatMessages`)
  - ツール設定: `chrome.storage.local`
  - セマンティック履歴: IndexedDB (`VectorHistoryDB`)
  - ページコンテンツ: Background キャッシュ (`WebsiteContentManager`)
- **ビルド構成**
  - vite.config.ts のマルチエントリで sidebar.html / background.js / content.js を独立出力
  - Content Script は自己完結型でランタイムチャンクロード問題を回避
- **設計パターン**
  - Side Panel コパイロット / Popup アシスタント / タブごと Agent / ハイブリッド UI

## 注目ポイントの解説

このブログでいちばん示唆深いのは「Background をモデルホストの単一サービスとして扱う」という設計パターンにゃ。MV3 では Service Worker が一時停止・再起動される可能性があるけど、それでも全タブが Background のパイプラインインスタンスを共有することで重複ロードを避け、Side Panel の UI 応答性も保てる。これは、ブラウザ拡張で LLM をローカル実行する際にぶつかる「複数コンテキストにモデルを抱えるとメモリが爆発する」問題への現実的な答えなのにゃ。

もう一つ重要なのは、推論モデル (Gemma 4) と埋め込みモデル (MiniLM) を意図的に分離している点にゃ。Gemma 4 がツール呼び出しの判断、MiniLM が履歴のセマンティック検索という役割分担で、量子化レベル (q4f16 vs fp32) も用途に合わせて変えている。この「役割ごとに別モデル」というデザインは、ブラウザというリソース制約環境での実装パターンとして広く応用できそうにゃん。

ツール実行ループで「内部モデルトランスクリプト」と「UI トランスクリプト」を二層に分けるのも巧みな設計にゃ。モデルが見るプロンプト履歴とユーザーが見るチャット履歴を切り離せば、ツール呼び出しの中間結果を UI から隠しつつメタデータとして保持でき、しかも複数ターンのツール呼び出しが透過的に進む。Chrome 拡張に限らず、エージェント設計の参考になる構造にゃん。
