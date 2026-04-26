# Jina Embeddings 系列 5モデル 比較サマリ

| 項目 | v1 (2307.11224) | v2 (2310.19923) | v3 (2409.10173) | v4 (2506.18902) | v5-text (2602.15547) |
|--|--|--|--|--|--|
| 発表年月 | 2023-07 | 2023-10 | 2024-09 | 2025-06 | 2026-02 |
| ベースモデル | T5 エンコーダ | 改造BERT(自前事前学習) | XLM-RoBERTa改造 | Qwen2.5-VL-3B-Instruct | Qwen3-0.6B / EuroBERT-210M |
| 位置埋め込み | 相対バイアス(T5) | 双方向ALiBi | RoPE(θ調整) | 記載なし | RoPE(低θ外挿) |
| Transformer層数 | 記載なし | 4/12/24 | 24 | 記載なし | 記載なし |
| LoRA | なし | なし | rank4×5(4タスク) | rank-LoRA×3(各60M) | rank32×4 |
| パラメータ数 | 35/110/330M | 33/137/435M | 559M+α(計約572M) | 3.8B+60M×3 | small約677M / nano約239M |
| 最大コンテキスト | 512 | 8,192 | 8,192 | 32,768 | 32,000 |
| 出力次元 | 512/768/1024 | 512/768/1024 | 1024 | 単一2048 / 多128 | small1024 / nano768 |
| 学習タスク | STS/検索/QA/否定 | 検索/分類/STS/長文 | 検索/STS/分類/Sep | 検索/STS/コード/マルチモーダル | 検索/STS/分類/クラスタ |
| Instruction Tuning | なし | なし | なし(LoRA代替) | 不要 | 軽量プレフィックスのみ |
| MRL | なし | なし | あり(32–1024) | あり(128–2048) | あり(256まで安定) |
| 多言語 | 英語のみ | 英語のみ | 89言語 | 多言語(15+実証) | 多言語(small=119) |
| 損失関数 | 双方向InfoNCE+Triplet margin | MLM→双方向InfoNCE→拡張InfoNCE | 双方向InfoNCE / CoSent / 拡張InfoNCE | InfoNCE+KL+MRL+CoSENT | コサイン蒸留+InfoNCE+CoSENT+GOR |
| プーリング | mean | mean | mean | 単一mean / 多トークン射影 | last-token (EOS) |
| 訓練段階 | 2段(ペア→トリプレット) | 3段(MLM→ペア→hard neg) | 3段(MLM→ペア→LoRA) | 2段(ペア→タスク別LoRA) | 2段(蒸留→タスク別LoRA) |
| ハードネガマイニング | cross-encoder検証 | 既存検索モデル+CE検証 | BGE-large+BM25 | データセット内triplet | in-batch+事前マイニング |
| 訓練最適化 | DeepSpeed/32bit | DeepSpeed/FP16/AC | FA2/AC/DeepSpeed | バックボーン凍結 | 記載なし |
| 主要ベンチマーク | MTEB STS 79.93 (base) | MTEB-en 60.37 (base, ada-002同等) | MTEB-en 65.52 / MMTEB 64.44 | Jina-VDR 81.52 / ViDoRe 90.17 | MMTEB 67.0 / MTEB-en 71.7 |
| 特記事項 | データ品質重視+negation | 8k長文OSS初期 | LoRAマルチタスク化 | 真のマルチモーダル+late-interaction | 教師蒸留で小型化 |
