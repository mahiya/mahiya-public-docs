# DeepInfra が Hugging Face Inference Providers に統合

## 発行元
- **発行組織**: Hugging Face
- **著者**: Aray Sultanbekova、Shang-Pin、Utemuratov、Yessen K、Oguz Vuruskaner、Célina Hanouti、Simon Brandeis、Lucain Pouget
- **発行日**: 2026年4月29日
- **URL**: https://huggingface.co/blog/inference-providers-deepinfra

## 一言概要
業界最安級のサーバーレス AI 推論プラットフォーム **DeepInfra** が、Hugging Face Hub の公式 Inference Provider として統合され、HF トークン 1 つで DeepSeek V4 Pro / Kimi-K2.6 / GLM-5.1 などの巨大モデルを OpenAI 互換 API から直接呼べるようになったにゃ。

## ブログで説明している内容

- **DeepInfra の特徴**
  - サーバーレス AI 推論プラットフォーム
  - 業界最安級のトークン単価
  - 100+ モデルを提供（LLM・テキスト生成・テキスト→画像/動画・埋め込みなど）

- **2 つのアクセス方法**
  - **Web UI**: ユーザー設定で API キー設定
    - カスタムキー: プロバイダーアカウントに直接請求
    - HF ルーティング: HF トークンで認証 → HF アカウントに請求
  - **クライアント SDK**:
    - Python: `huggingface_hub` (>=1.11.2)
    - JavaScript: `@huggingface/inference`
    - OpenAI SDK 互換 (`base_url="https://router.huggingface.co/v1"`)

- **初期サポートモデル**
  - DeepSeek V4 Pro (862B, テキスト生成)
  - Kimi-K2.6 (1.1T, 画像テキスト生成)
  - GLM-5.1 (754B, テキスト生成)
  - 今後: Text-to-Image、Text-to-Video、Embedding を追加予定

- **料金体系**
  - 直接リクエスト: プロバイダー料金で課金
  - ルーティング: HF からのマークアップなし、標準プロバイダー料金
  - **PRO 会員**: 月額 $2 分の Inference クレジット（全プロバイダー対応）

- **エージェント連携**
  - Pi、OpenCode、Hermes Agents などの Agent Harnesses から利用可能

## 注目ポイントの解説

注目すべきは、**HF Router 経由の OpenAI SDK 互換 API** という設計にゃ。
ユーザーは `model="deepseek-ai/DeepSeek-V4-Pro:deepinfra"` のように **`モデル名:プロバイダー名`** という記法でプロバイダーを切り替えられるため、

- **コードを書き換えずにバックエンド (Together / Fireworks / DeepInfra など) を切り替えできる**
- HF トークン 1 本で複数プロバイダーをまたいだ請求集約
- マークアップなしの透過課金

という、**プロバイダー抽象化レイヤー** として Hugging Face が機能していることが分かるにゃ。

事業者ロックインを避けながら、DeepSeek V4 Pro (862B) や Kimi-K2.6 (1.1T) のような巨大モデルを安価に試せるのは、個人開発者・スタートアップにとって非常に大きい恩恵にゃ。
