# OpenAI Privacy Filter でスケーラブルな Web アプリを作る

## 発行元
- **発行組織**: Hugging Face
- **著者**: yuvraj sharma (ysharma)、Freddy Boulton (freddyaboulton)、Abubakar Abid (abidlabs)
- **発行日**: 2026年4月27日
- **URL**: https://huggingface.co/blog/openai-privacy-filter-web-apps

## 一言概要
OpenAI が公開した 1.5B パラメータの **Privacy Filter** モデル（128K コンテキスト・Apache 2.0）を使って、**ドキュメント / 画像 / ペーストテキスト** から PII を検出・マスクする 3 つの実用 Web アプリを、Gradio の `@server.api` パターンで構築するチュートリアルにゃ。

## ブログで説明している内容

- **OpenAI Privacy Filter について**
  - 1.5B パラメータ、活性パラメータはわずか 50M
  - コンテキスト長 128,000 トークン（チャンキング不要）
  - Apache 2.0 ライセンス
  - 検出カテゴリ 8 種類: `private_person` / `private_address` / `private_email` / `private_phone` / `private_url` / `private_date` / `account_number` / `secret`
  - PII-Masking-300k ベンチマークで SOTA、多言語対応（西・仏・中・印など）

- **実装する 3 つのアプリ**
  - **Document Privacy Explorer**: PDF / DOCX を読み込み、PII をハイライト表示。BIOES デコーディングで境界を正確に保持
  - **Image Anonymizer**: 画像内の PII を Tesseract OCR で抽出し、黒バーで塗りつぶし。クライアント側キャンバスで編集可能
  - **SmartRedact Paste**: テキストを貼り付けると、PII を `<CATEGORY>` プレースホルダーに置換した「公開 URL」と、トークンゲート付き「プライベート URL」を生成

- **gradio.Server の設計パターン**
  - `@server.api`: キューイング対応、モデル推論や GPU 処理向け
  - `@server.get` / `@server.post`: 通常の FastAPI ルート、静的ページ・ファイル参照向け
  - ZeroGPU との `@spaces.GPU` 連携が容易
  - ブラウザの `@gradio/client` と Python の `gradio_client` から同一エンドポイントを呼び出せる

- **JavaScript 統合例**
  ```javascript
  import { Client, handle_file } from "https://cdn.jsdelivr.net/npm/@gradio/client/...";
  const client = await Client.connect(window.location.origin);
  const result = await client.predict("/analyze_document", { file: handle_file(file) });
  ```

## 注目ポイントの解説

最大の見どころは、**「Gradio = デモ用」という固定観念を覆す `@server.api` パターン** にゃ。
このパターンを使うと、

1. **キューイングと GPU スケジューリングは Gradio に任せたまま**
2. **フロントエンドはカスタム HTML/JS** で自由に作り
3. **同じエンドポイントが Python クライアントからも呼べる**

という、本格的な SaaS 風 Web アプリが Gradio Space 1 つで構築できるにゃ。

モデル側の注目点は、**128K コンテキストを単一パスで処理**できる点にゃ。チャンキング不要なので、スパンのオフセットがそのまま元テキストに対応し、PDF や OCR 結果のような長文・座標付きデータでも実装が劇的にシンプルになるにゃ。50M activated params という軽量さと組み合わせれば、**プライバシー保護を「重い前処理」ではなく日常 UI に組み込める**未来が見えてくる、という意味で実用性の高い記事にゃ。
