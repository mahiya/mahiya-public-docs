# BAAI BGE Reranker 市場調査レポート

> 調査日: 2026年4月25日

---

## 基本情報

| 項目 | 内容 |
|------|------|
| **開発元** | BAAI（北京人工知能研究院 / Beijing Academy of Artificial Intelligence） |
| **シリーズ名** | BGE（BAAI General Embedding） Reranker |
| **ライセンス** | Apache 2.0（完全無償・商用利用可） |
| **ライブラリ** | FlagEmbedding（FlagOpen/FlagEmbedding） |
| **HuggingFace** | https://huggingface.co/BAAI |
| **GitHub** | https://github.com/FlagOpen/FlagEmbedding（11.6k stars, 867 forks） |
| **最新安定リリース** | FlagEmbedding v1.4.0（2026年4月22日） |

### モデルラインナップ

| モデル名 | ベースモデル | パラメータ数 | サイズ | 特徴 |
|----------|------------|------------|-------|------|
| bge-reranker-base | xlm-roberta-base | ~278M | ~1.1GB | 軽量・高速、英語/中国語 |
| bge-reranker-large | xlm-roberta-large | ~560M | ~2.2GB | 高精度、英語/中国語 |
| bge-reranker-v2-m3 | bge-m3 | 568M | 2.27GB | 多言語対応・軽量・主力モデル |
| bge-reranker-v2-gemma | gemma-2b | 2.51B | 10GB | LLMベース・高精度多言語 |
| bge-reranker-v2-minicpm-layerwise | MiniCPM-2B | 2.72B | 10.9GB | レイヤー選択可能・最高精度 |
| bge-reranker-v2.5-gemma2-lightweight | Gemma2-9B | 2.72B | 10.9GB | トークン圧縮・レイヤー削減対応 |

### 価格

- **モデル自体**: 無料（Apache 2.0）
- **セルフホスト推定コスト**:
  - bge-reranker-base v2: 約$0.18 / 1,000クエリ（サーバー費用のみ）
  - bge-reranker-large v2: 約$0.35 / 1,000クエリ（サーバー費用のみ）
  - GPU（NVIDIA T4）利用時: $0.0097 / 1Mトークン（50%稼働）
- **API経由（サードパーティ）**: Pinecone等が推論サービスとして提供

---

## 市場ポジション

BGE Rerankerは、**OSSリランカーの事実上のデファクトスタンダード**として広く認知されている。特に以下の点で市場を席巻している：

- **HuggingFaceダウンロード数**: bge-reranker-v2-m3 は月間810万ダウンロード以上
- **エコシステムの厚み**: 69件以上のファインチューニング済みモデル、41件以上の量子化バリアント、100以上のSpacesで利用
- **採用事例**: Pinecone、LlamaIndex、LangChainとのネイティブ統合
- **事実上の「ベースライン」扱い**: 複数のサードパーティベンチマーク記事において「他モデルがBGEを有意に上回らない場合、追加コスト・レイテンシは正当化されない」と評される

### 市場内での位置づけの変化

2024年時点ではOSSリランカーの第一選択肢だったが、2025年以降は**Qwen3-Reranker（Alibaba）**や**mxbai-rerank-v2（Mixedbread）**などの新興モデルとの競争が激化している。ただし、BGEは「安全なデフォルト」「枯れた基準点」としての地位を維持している。

---

## 開発元のアピールポイント

BAA（北京人工知能研究院）が公式に主張している強みは以下のとおり：

### 1. 多言語対応（100言語以上）
bge-reranker-v2-m3はbge-m3バックボーンを採用し、100言語以上に対応。BEIR（英語）、C-MTEB/Retrieval（中国語）、MIRACL（多言語）の全ベンチマークで大幅な性能向上を公式に主張している。

### 2. 軽量・高速推論
v2-m3モデル（568M）はクロスエンコーダとしては小型で、コンシューマGPUでも動作可能。FP16モードによるさらなる高速化もサポート。

### 3. 柔軟なモデル選択
スピード重視（v2-m3）、精度重視（v2-gemma / minicpm-layerwise）、レイヤー数調整（layerwise系）など、ユースケースに応じたモデル選択が可能。

### 4. 完全なエコシステム
FlagEmbeddingライブラリにより、推論・ファインチューニング・評価・データセットを一貫してサポート。LoRAファインチューニング、DeepSpeed、Flash Attention対応。

### 5. Apache 2.0ライセンス
商用利用・改変・再配布が完全無料。コード・データ・ウェイト全て公開。

### 6. BGE-M3との統合
埋め込みモデル（BGE-M3）とリランカー（bge-reranker-v2-m3）が同一バックボーンで設計されており、パイプライン全体での整合性が高い。

---

## 第三者評価：強み

### コスト効率の高さ
- 「**Best open quality per dollar**: bge-reranker-large v2」と第三者レビューで評価（Medium）
- bge-reranker-base v2は「90% of quality for ~½ cost」という評価
- GPU利用時はAPIサービス（Cohere: $100/月、BGE: $0*）と比較して圧倒的コスト優位

### 多言語ベースライン最強クラス
- mxbai-rerank-v2との比較で**Mr.TyDi（多言語）でBGEが優位**（bge-v2-m3: 30.99 vs mxbai-large: 29.79 NDCG@10）
- 多言語RAGパイプラインの「BGE-M3（検索） + BGE-Reranker-v2-m3（リランク）」構成が定番として定着

### セルフホスト適性
- データプライバシー要件のある企業での採用が多い
- 1,600以上のGitHubプロジェクトが依存（FlagEmbeddingリポジトリ）
- TEI（Text Embeddings Inference）でのネイティブサポートにより本番デプロイが容易

### 低レイテンシ（GPU使用時）
- GPU使用時: 50〜100ms/クエリ（NVIDIA T4）
- bge-reranker-base v2: P95レイテンシ92ms

### エコシステムとの統合
- LangChain、LlamaIndex、Pinecone、Weaviate等の主要フレームワークにネイティブ統合済み
- 活発な開発継続（2025年3月 BGE-VL マルチモーダル拡張、2025年 BGE-Reasoner リリース）

---

## 第三者評価：弱点・批判点

### 1. 英語精度で新興モデルに追いつかれている

mxbai-rerank-v2との比較（BEIRベンチマーク）：

| モデル | パラメータ | BEIR NDCG@10 |
|--------|-----------|-------------|
| mxbai-rerank-large-v2 | 1.5B | **57.49** |
| mxbai-rerank-base-v2 | 0.5B | 55.57 |
| bge-reranker-v2-gemma | 2.5B | 55.38 |
| bge-reranker-v2-m3 | 568M | 53.94 |

Mixedbreadの1.5BモデルがBGEの2.5Bモデルより高精度で、かつ8倍高速という報告がある。

### 2. コードサーチでの弱さ
CoIR-Retrieval/CosQA（コード検索）での評価：
- bge-reranker-v2-m3: **24.86** NDCG@10（最下位クラス）
- mxbai-rerank-large-v2: 32.05 NDCG@10

コードリトリーバル用途での採用には注意が必要。

### 3. ドメイン横断での不安定なパフォーマンス
Agentset.aiのベンチマークで「sharp spikes, performing well only in select cases」と評価され、金融・科学・ウェブ等の複数ドメインで一貫した高精度を示す Zerank-1 や Voyage Rerank 2.5 と対照的に、特定ドメインで急激なスコア低下が見られる。

### 4. CPU推論での実用性問題
- CPU時のレイテンシ: 200〜400ms/クエリ（「real-time 用途では実用不可」と指摘される）
- 本番環境でのCPU利用報告: バッチ処理で20〜30秒のレイテンシ事例あり
- INT8量子化+ONNX最適化後でも8〜15秒という報告

### 5. bge-reranker-v2-gemma の性能/速度問題
- 推論時間: bge-reranker-v2-m3（0.5秒）に対し bge-reranker-v2-gemma（7.2秒）で約14倍遅い
- HuggingFaceディスカッションで「v2-gemma は v2-m3 より精度が低い場合がある」という報告あり
- ファインチューニング方法が不明瞭（GitHub Issue #1019, #1348）

### 6. 商用モデルとの精度差
- 商用APIのトップ（Cohere Rerank v4.0 Pro: ELO 1629、Zerank-2: ELO 1638）には精度面で及ばない
- 特に高精度要求のエンタープライズ用途では商用APIが引き続き優位

### 7. レイテンシドキュメントの不透明さ
公式READMEに具体的なレイテンシ数値の記載がなく、「fast inference」という記述のみ。FP16モードのトレードオフ（精度劣化の程度）も定量的に明示されていない。

---

## ベンチマーク結果

### MTEB Reranking比較（2025年時点）

Qwen公式レポートより：

| モデル | パラメータ | MTEB-R | CMTEB-R | MMTEB-R | MLDR |
|--------|-----------|--------|---------|---------|------|
| **bge-reranker-v2-m3** | 0.6B | 57.03 | 72.16 | 58.36 | 59.51 |
| Qwen3-Reranker-0.6B | 0.6B | 61.82 | 71.02 | 64.64 | 50.26 |
| Qwen3-Reranker-4B | 4B | 65.80 | 71.31 | 66.36 | 67.28 |
| Qwen3-Reranker-8B | 8B | **69.02** | **77.45** | **72.94** | **70.19** |

- MTEB-R（英語）: BGEは57.03で、同規模Qwen3に対し約4.8ポイント劣後
- CMTEB-R（中国語）: BGEは72.16で健闘するも、Qwen3-8Bの77.45には及ばない
- MMTEB-R（多言語）: BGEは58.36で、Qwen3-0.6Bの64.64にも及ばない

### BEIRベンチマーク比較（mxbai-rerank-v2レポートより）

| モデル | パラメータ | BEIR NDCG@10 | Mr.TyDi NDCG@10 | C-Pack NDCG@10 | CosQA NDCG@10 |
|--------|-----------|-------------|----------------|----------------|---------------|
| mxbai-rerank-large-v2 | 1.5B | **57.49** | 29.79 | **84.16** | **32.05** |
| mxbai-rerank-base-v2 | 0.5B | 55.57 | 28.56 | 83.70 | 31.73 |
| bge-reranker-v2-gemma | 2.5B | 55.38 | 30.40 | 78.50 | 31.51 |
| **bge-reranker-v2-m3** | 568M | 53.94 | **30.99** | 81.83 | 24.86 |

- 多言語（Mr.TyDi）ではbge-v2-m3が首位
- 英語（BEIR）・中国語（C-Pack）・コード（CosQA）ではmxbaiが優位

### 実用ベンチマーク（レイテンシ・コスト比較）

Bhagya Rana（Medium）実測値：

| モデル | nDCG@10 | P95レイテンシ | コスト/1kクエリ |
|--------|---------|-------------|--------------|
| Cohere Rerank | **0.735** | 210ms | $2.40 |
| MonoT5-3B | 0.726 | 480ms | $1.25 |
| bge-reranker-large v2 | 0.715 | 145ms | $0.35 |
| **bge-reranker-base v2** | **0.699** | **92ms** | **$0.18** |
| Jina-reranker-v2 | 0.694 | - | - |
| MiniLM-L-6-v2 | 0.662 | 55ms | $0.08 |

- BGE-large v2は「品質・コスト比最良のOSSモデル」として評価
- BGE-base v2は「large比で90%の品質を約半額で実現」

### 速度比較（mxbai-rerank-v2公式データ）

| モデル | 1クエリあたり推論時間 |
|--------|-------------------|
| mxbai-rerank-large-v2 (1.5B) | 0.89秒 |
| bge-reranker-v2-m3 (568M) | 3.05秒 |
| bge-reranker-v2-gemma (2.5B) | 7.20秒 |

---

## 競合比較

### 主要OSSリランカーとの比較マトリクス

| 項目 | BGE v2-m3 | mxbai-rerank-v2 large | Qwen3-Reranker-4B | jina-reranker-v3 |
|------|-----------|----------------------|-------------------|-----------------|
| パラメータ | 568M | 1.5B | 4B | 560M |
| ライセンス | Apache 2.0 | Apache 2.0 | Apache 2.0 | CC BY-NC 4.0 |
| 英語（BEIR） | 53.94 | **57.49** | - | 61.94 |
| 多言語 | **30.99**（Mr.TyDi） | 29.79 | **66.36**（MMTEB-R） | - |
| 中国語 | 81.83 | **84.16** | 71.31 | - |
| 推論速度 | 3.05秒 | **0.89秒** | >1000ms | - |
| CPU利用 | △ | - | - | - |
| エコシステム | ◎（成熟） | ○ | ○ | ○ |
| コミュニティ | ◎（11.6k stars） | ○ | ○ | ○ |

### 商用APIとの比較

| 項目 | BGE（セルフホスト） | Cohere Rerank v3 | Voyage Rerank 2.5 | Zerank-2 |
|------|------------------|-----------------|------------------|---------|
| コスト | $0.18〜0.35/1kクエリ | $2.40/1kクエリ | - | $2.50/月〜 |
| 精度 | 0.699〜0.715 nDCG | **0.735** nDCG | - | **ELO 1638** |
| レイテンシ | 92〜145ms（GPU） | 100〜150ms | 100〜200ms | 100〜200ms |
| データプライバシー | ◎（ローカル処理） | × | × | × |
| ゼロ設定 | × | ◎ | ◎ | ◎ |

### 競合ポジショニングサマリー

- **vs mxbai-rerank-v2**: 英語・中国語・コードで劣るが、多言語（Mr.TyDi）では優位。速度も3倍以上遅い。ただしBGEはエコシステムの成熟度で優位。
- **vs Qwen3-Reranker**: 全体的にQwen3-Reranker-4B/8Bが優位（特に多言語MTEB）。ただしQwen3は推論コストが大きく（>1秒）、BGEはより軽量で実用的。Qwen3-0.6Bとの比較では一部でBGEが優位（CMTEB-Rで72.16 vs 71.02）。
- **vs Cohere/商用API**: 精度面では商用APIに劣るが、コストは約7〜14倍安価。データプライバシー要件がある場合はBGEが唯一の選択肢になりうる。
- **vs jina-reranker-v3**: jina-v3はBEIRで61.94と高スコアだが、ライセンスがCC BY-NC 4.0で商用利用制限あり。BGEはApache 2.0で完全商用利用可。

---

## 参考リンク

### 公式リソース
- [BAAI/bge-reranker-v2-m3 - HuggingFace](https://huggingface.co/BAAI/bge-reranker-v2-m3)
- [BAAI/bge-reranker-v2-gemma - HuggingFace](https://huggingface.co/BAAI/bge-reranker-v2-gemma)
- [BAAI/bge-reranker-v2.5-gemma2-lightweight - HuggingFace](https://huggingface.co/BAAI/bge-reranker-v2.5-gemma2-lightweight)
- [FlagOpen/FlagEmbedding - GitHub](https://github.com/FlagOpen/FlagEmbedding)
- [BGE Reranker v2 公式ドキュメント](https://bge-model.com/bge/bge_reranker_v2.html)

### ベンチマーク・比較記事
- [Top 8 Rerankers: Quality vs Cost（Medium/Bhagya Rana）](https://medium.com/@bhagyarana80/top-8-rerankers-quality-vs-cost-4e9e63b73de8)
- [Best Reranker for RAG: We tested the top models（Agentset）](https://agentset.ai/blog/best-reranker)
- [Reranker Benchmark: Top 8 Models Compared（AIMultiple）](https://aimultiple.com/rerankers)
- [Top 5 Reranking Models to Improve RAG Results（MachineLearningMastery）](https://machinelearningmastery.com/top-5-reranking-models-to-improve-rag-results/)
- [Top 7 Rerankers for RAG（Analytics Vidhya）](https://www.analyticsvidhya.com/blog/2025/06/top-rerankers-for-rag/)
- [Best Reranker Models for RAG: Open-Source vs API（BSWEN, 2026）](https://docs.bswen.com/blog/2026-02-25-best-reranker-models/)

### 競合比較元資料
- [mxbai-rerank-v2 公式ブログ（Mixedbread）](https://www.mixedbread.com/blog/mxbai-rerank-v2)
- [Qwen3 Embedding: Advancing Text Embedding and Reranking（Qwen公式）](https://qwenlm.github.io/blog/qwen3-embedding/)
- [Contextual AI Rerank v2 vs BGE v2-M3（Agentset比較）](https://agentset.ai/rerankers/compare/contextual-ai-rerank-v2-instruct-vs-baaibge-reranker-v2-m3)
- [BAAI/BGE Reranker v2 M3 詳細（Agentset）](https://agentset.ai/rerankers/baaibge-reranker-v2-m3)
- [BGE Reranker/Pinecone モデルカード](https://docs.pinecone.io/models/bge-reranker-v2-m3)
