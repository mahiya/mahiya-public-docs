# DeepSeek-V4: エージェントが本当に使える 100 万トークン文脈

## 発行元
- **発行組織**: Hugging Face Blog（DeepSeek の発表を Hugging Face コミュニティで紹介）
- **主著者**: ben burtenshaw 他
- **発行日**: 2026年4月24日
- **URL**: https://huggingface.co/blog/deepseekv4

## 一言概要
DeepSeek-V4 は、**ハイブリッド注意機構 (CSA + HCA)** によって 100 万トークン文脈での推論を FLOP・KV キャッシュとも大幅に削減し、さらに**エージェント用途** に最適化されたツール呼び出しスキーマと RL サンドボックス (DSec) を備えた、フロンティア閉鎖モデルに迫る性能を目指す OSS LLM にゃ。

## ブログで説明している内容

- **チェックポイント (4 種)**
  - DeepSeek-V4-Pro (1.6T total / 49B active, instruct)
  - DeepSeek-V4-Flash (284B total / 13B active, instruct)
  - 上記の Base 版 2 つ
  - 推奨サンプリング: temperature=1.0, top_p=1.0

- **長コンテキスト効率化**
  - V4-Pro: V3.2 比で FLOP 27%、KV キャッシュ 10% にまで削減
  - V4-Flash: FLOP 10%、KV キャッシュ 7%

- **ハイブリッド注意機構**
  - **CSA (Compressed Sparse Attention)**: KV を 4 倍圧縮、softmax-gated プーリング、FP4 lightning indexer で上位ブロック選択
  - **HCA (Heavily Compressed Attention)**: 128 倍圧縮、スパース選択なしの dense
  - 61 層構成: Layer 0-1 = HCA、Layer 2-60 = CSA/HCA 交互、MTP ブロックはスライディングウィンドウのみ

- **KV キャッシュ最適化**
  - FP8 ストレージ、RoPE 次元のみ BF16
  - 標準 GQA (8 ヘッド bfloat16) 比で約 2% のメモリ使用量

- **エージェント向け改良**
  - **インターリーブ思考の保持**: ユーザーターン境界を超えて推論トレースを保持（ツール呼び出しがある場合）
  - **専用ツール呼び出しスキーマ**: 新特殊トークン `|DSML|`、XML 形式でエスケープ失敗を削減
  - **DSec (DeepSeek Elastic Compute)**: RL 学習用サンドボックス。関数呼び出し / コンテナ / Firecracker microVM / QEMU フル VM を統一 API で扱う

- **ベンチマーク (主要)**
  - Terminal Bench 2.0: V4-Pro-Max=67.9（GPT-5.4=75.1, Gemini-3.1=68.5）
  - SWE Verified: V4-Pro-Max=80.6（Opus-4.6=80.8 と同等）
  - MCPAtlas Public: 73.6（Opus-4.6=73.8 と僅差）
  - Toolathlon: 51.8（K2.6=50.0、GLM-5.1=40.7 を上回る）
  - 内部 R&D コーディング (30 タスク): V4-Pro-Max=67%、Sonnet 4.5=47%、Opus 4.5=70%

- **長コンテキスト検索 (MRCR 8-needle)**
  - 256K: 0.82 以上、1M: 0.59

- **3 つの推論モード**
  - Non-think（高速、CoT なし）
  - Think High（`<think>` ブロックで明示推論）
  - Think Max（最大推論努力、384K+ トークン必須）

- **開発者調査**: DeepSeek 社内 85 名のうち 52% が「現行モデルから置き換え可能」、39% が前向き

## 注目ポイントの解説

このリリースの**真の差別化要因は「長コンテキスト × エージェント」の同時最適化**にゃ。

通常 100 万トークン文脈は「読めるけど高い・遅い・忘れる」になりがちだけど、V4 は

1. **CSA + HCA のハイブリッド** で計算と KV キャッシュを実用領域まで圧縮
2. **インターリーブ思考の保持** によりマルチターンエージェントが累積推論できる
3. **`|DSML|` + XML スキーマ** で JSON エスケープ問題を回避（実エージェントで意外と多い失敗モード）
4. **DSec という RL 用サンドボックス** で、関数呼び出しから本物の VM までをシームレスに学習に組み込む

という、**「エージェントを RL で本格的に学習させる」ための土台までセット** で公開している点が出色にゃ。

ベンチマーク的には知識・推論系で SOTA を取りに行くというより、**SWE Verified や MCPAtlas のようなエージェント実用性能で Opus-4.6 とパリティを取る** という、はっきりとしたターゲット設定をしているのも興味深いにゃ。一方で、`|DSML|` スキーマへのコミュニティ適応や、未検証フレームワークでの転移性能はこれからの課題にゃ。
