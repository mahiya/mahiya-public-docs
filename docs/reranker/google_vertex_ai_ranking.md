# Google Vertex AI Ranking API 市場調査レポート

> 調査日: 2026年4月25日

---

## 基本情報

| 項目 | 内容 |
|------|------|
| 正式名称 | Google Vertex AI Ranking API / Agent Builder Ranking API / Agent Search Ranking API |
| 提供元 | Google Cloud |
| リリース日 | GA: 2025年5月31日（004シリーズ）|
| 公式ドキュメント | https://docs.cloud.google.com/generative-ai-app-builder/docs/ranking |
| 公式ブログ発表 | https://cloud.google.com/blog/products/ai-machine-learning/launching-our-new-state-of-the-art-vertex-ai-ranking-api |

### 利用可能モデル

| モデル名 | リリース日 | 特徴 | トークン上限/レコード |
|----------|-----------|------|----------------------|
| semantic-ranker-default-004 | 2025年4月9日 | 最高精度、汎用 | 1,024トークン |
| semantic-ranker-fast-004 | 2025年4月9日 | 低レイテンシ特化 | 1,024トークン |
| semantic-ranker-default-003 | 2024年9月10日 | 旧世代 | 512トークン |
| semantic-ranker-default-002 | 2024年6月3日 | 旧世代 | 512トークン |

### 価格

| 内容 | 料金 |
|------|------|
| 基本料金 | $1.00 / 1,000クエリ |
| 定義（1クエリ） | ドキュメント100件まで含む |
| 100件超過時 | 100件ごとに1クエリ追加換算 |
| 無料枠 | 新規顧客向け $300 クレジット |
| 制限 | 1リクエストあたり最大200レコード |

**参考比較（競合）**
- Cohere Rerank: $2.00 / 1,000クエリ（同ドキュメント数前提）
- Voyage AI Rerank: $0.05 / 1M tokens 相当

---

## 市場ポジション

### GCP エコシステムでの位置付け

Vertex AI Ranking API は Google Cloud の AI 検索・RAG スタック内のコアコンポーネントとして位置付けられている。正式には **Agent Builder**（旧：Generative AI App Builder）の一機能として提供されており、以下の GCP サービスとネイティブに統合されている。

- **Vertex Vector Search** — ベクトル検索後のリランキング
- **RAG Engine (Agent Platform)** — 組み込みリランキング機能として選択可能
- **AlloyDB** — `ai.rank()` SQL 関数での直接呼び出し
- **Elasticsearch (Open Inference API)** — Elastic との公式パートナー連携
- **LangChain / GenKit** — フレームワーク統合

### 市場認知度

- RAG パイプラインのリランキング層として **GCP ユーザーへの訴求力は高い**。GCP 上でエンべディング・リランキング・LLM 推論を一気通貫で構築できる点がアピールされている。
- 独立したリランキング API としての市場認知度は **Cohere・Voyage AI に比べて低め**。主要な第三者リランカーリーダーボード（Agentset.ai、ZeroEntropy、Analytics Vidhya など）にはほぼ登場しない。これは GA リリースが2025年5月と比較的新しいことも一因と考えられる。
- Google Cloud Blog での発表（2025年5月31日）を受けて、ML エンジニアコミュニティでの認知は急拡大中（X/LinkedIn での言及が増加）。

---

## 開発元のアピールポイント

Google が公式に主張している差別化ポイントは以下の通り。

### 1. BEIR ベンチマークでの業界最高精度

`semantic-ranker-default-004` は BEIR データセットの **NDCG@5 において競合スタンドアローン型リランキング API サービスをリード**すると Google は主張している。比較対象として暗示されているのは Cohere および Voyage AI。評価スクリプトは GitHub に公開されており再現性を担保（ただしスクリプトは Google 自身が公開したもの）。

### 2. 競合比 2倍の速度（defaultモデル）

`semantic-ranker-default-004` は競合リランキング API サービスと比較して **少なくとも2倍高速**と主張（任意のスケールで）。`semantic-ranker-fast-004` はさらにその約3分の1の低レイテンシ。

### 3. 長コンテキスト対応

1リクエストあたり合計 **最大200,000トークン** の処理に対応。v004 から1レコードあたり 1,024トークンに拡張（旧モデルは512トークン）。

### 4. ステートレス API — インデックス不要

検索時に都度クエリ＋ドキュメントリストを渡すだけで動作し、**事前インデックス構築が不要**。既存の検索基盤を変えずに「最後の1マイル」として追加できる。

### 5. 多様なインテグレーション

GCP エコシステム（Vector Search / AlloyDB / RAG Engine）だけでなく、Elasticsearch、LangChain、GenKit とのネイティブ統合をサポート。

### 6. 業界ドメイン別精度向上

Retail・News・Finance・Healthcare などの業界特化ドメインで、ベースライン（text-embedding-004 + BM25）に対して **NDCG@5 が大幅に向上**することを示すグラフを公式ブログで掲載。

### 7. 25言語対応（多言語）

テキストデータについて 25言語に対応していることを公式ドキュメントで明記。

---

## 第三者評価：強み

### 価格競争力

独立したブログ記事（Sascha Heyer / Google Cloud Community on Medium）によると、**Google Ranking API は $1.00/1,000クエリ と Cohere Rerank（$2.00）の半額**であり、コスト効率が高いと評価されている。

### GCP 統合の利便性

Elasticsearch Labs の技術記事では、「GCP 上で埋め込み・リランキング・LLM 推論を同一クラウドプロバイダー内で完結できる」ことを明確なアドバンテージとして評価している。GCP を既に使用している開発チームにとっての運用コスト削減効果が指摘されている。

### 実装の容易さ

複数の技術ブログが「数分でインテグレーション可能」という低摩擦な導入体験を評価している。LangChain への統合がドキュメント化されており、既存の RAG パイプラインへの追加が容易。

### 統計的優位の公開

Google は BEIR 評価ノートブックを GitHub に公開しており、第三者が評価プロセスを検証可能な状態にしている点は透明性として評価できる（ただし実際の検証は限定的）。

---

## 第三者評価：弱点・批判点

### 1. 第三者独立ベンチマークへの不在

2026年時点で主要なリランカーリーダーボードへの **Google Vertex AI Ranking API の掲載はほぼ存在しない**：

- **Agentset.ai リーダーボード**（2026年2月更新）: 上位10位内に不在。Zerank 2、Cohere Rerank 4 Pro、Voyage AI Rerank 2.5 などが上位を占める。
- **ZeroEntropy の比較記事**: Google Vertex AI への言及なし。
- **Analytics Vidhya の Top 7 Rerankers**: Google Vertex AI への言及なし。
- **Medium の Top 8 Rerankers Quality vs Cost**: Google Vertex AI への言及なし。

これは GA リリース（2025年5月）が比較的最近であること、および独立評価コミュニティへの浸透が遅れていることを示唆する。

### 2. ベンダーロックイン (GCP 依存)

- API は GCP の認証（IAM / サービスアカウント）に完全依存しており、**GCP 外での利用は事実上不可**。
- Gartner Peer Insights のユーザーレビューでは「パイプライン・モニタリング設定・Feature Store の構成が他クラウドへ移管しにくい」という**ベンダーロックイン懸念**が一般的な Vertex AI の批判点として挙がっている。
- Ranking API も同様の構造的制約を持つ（Discovery Engine API の有効化・IAM ロール設定が必須）。

### 3. 学習曲線と複雑な料金体系

G2 および Gartner Peer Insights のユーザーレビューより（Vertex AI 全体に関する評価）：
- 「学習曲線が急峻で、特に GCP 未経験チームにはドキュメントが断片的」
- 「複雑な料金体系でバジェット計画が立てにくい」
- 「エンドポイントへの scale-to-zero オプションがなく、アイドル時も課金される」
- 「コスト上限（ハードキャップ）機能がなく、自前でガードレールを実装する必要がある」

### 4. トークン制限（v003以前）

旧モデル（v003以前）では **1レコードあたり512トークンに制限**されており、長文ドキュメントの切り捨てが発生していた。v004 で1024トークンへ拡張されたが、Jina Reranker（最大8,000トークン）や Cohere Rerank v3.5（4,096トークン）と比較するとまだ制約がある。

### 5. 多言語サポートの範囲

25言語対応に留まり、Cohere Rerank v3.5（100言語以上）や MixedBread mxbai-rerank-v2（100言語以上）と比較して言語カバレッジが限定的。日本語対応は含まれているとされるが、日本語特化の評価データは公開されていない。

### 6. ベンチマーク自己申告問題

Googleが公表している BEIR 結果（NDCG@5 でのリード）は Google 自身が実施・公開したものであり、**完全に独立した第三者機関による検証データが存在しない**。評価ノートブックは公開されているが、実際に追試した公開レポートは確認できていない。

---

## ベンチマーク結果

### Google 公式発表（BEIR, NDCG@5）

Google 公式ブログ（2025年5月）および公開評価ノートブックによると：

- `semantic-ranker-default-004` は **BEIR データセットの NDCG@5 において競合スタンドアローン型リランキング API をリード**
- 評価対象として暗示されている競合: Cohere Rerank、Voyage AI Rerank
- 比較ベースライン: Vertex AI text-embedding-004 + BM25 検索

**具体的な数値スコアは公式ブログのグラフ形式で提示されており、テキストとして公開されていない**（図を直接確認する必要あり）。

### 速度ベンチマーク（Google 公式）

| モデル | 速度クレーム |
|--------|-------------|
| semantic-ranker-default-004 | 競合比 少なくとも2倍高速 |
| semantic-ranker-fast-004 | default 比 約3倍低レイテンシ |

実測レイテンシについては Medium の技術記事（Google Cloud Community）において **約700ms** という参考値が報告されている（トークン量に相関）。

### 第三者ベンチマークでの位置（Agentset.ai リーダーボード, 2026年2月更新）

Google Vertex AI Ranking API は **このリーダーボードに掲載されていない**。参考として上位モデルを示す：

| 順位 | モデル | ELO | nDCG@10 | レイテンシ | 価格/1Mトークン |
|------|--------|-----|---------|-----------|----------------|
| 1 | Zerank 2 | 1638 | 0.079 | 265ms | $0.025 |
| 2 | Cohere Rerank 4 Pro | 1629 | 0.095 | 614ms | $0.050 |
| 3 | Zerank 1 | 1573 | 0.082 | 266ms | $0.025 |
| 4 | Voyage AI Rerank 2.5 | 1544 | 0.110 | 613ms | $0.050 |
| 5 | Zerank 1 Small | 1539 | 0.083 | 248ms | $0.025 |

---

## 競合比較

### 主要リランカー比較表

| 項目 | Google Vertex AI (default-004) | Cohere Rerank v3.5 | Voyage AI Rerank 2.5 | Jina Reranker v2 |
|------|-------------------------------|--------------------|-----------------------|------------------|
| 価格 | $1.00/1,000クエリ | $2.00/1,000クエリ | ~$0.05/1Mトークン | $0.30*/1k推定 |
| トークン上限/レコード | 1,024トークン | 4,096トークン | - | 8,000トークン |
| 多言語 | 25言語 | 100言語以上 | 英語中心 | 多言語対応 |
| 独立ベンチマーク | **掲載なし** | 上位常連 | 上位常連 | 一部掲載 |
| GCP外利用 | **不可** | 可 | 可 | 可 |
| オープンソース | 非公開 | 非公開 | 非公開 | 一部OSS |
| 速度 (Google申告) | 競合比2倍速 | 基準 | 595-613ms程度 | 110ms程度 |

### 各競合との定性比較

**vs. Cohere Rerank**
- 価格は Google の方が安い（$1.00 vs $2.00 per 1k）
- 多言語カバレッジは Cohere が優位（100言語以上 vs 25言語）
- トークン上限は Cohere が優位（4,096 vs 1,024）
- 独立ベンチマーク実績は Cohere が圧倒的に豊富

**vs. Voyage AI**
- GCP 外での利用を考える場合は Voyage が柔軟
- Voyage は Finance・Legal 等の専門ドメインで強みを持つ
- 独立リーダーボード（Agentset.ai）では Voyage が4位（ELO 1544）に対し Google は掲載なし

**vs. オープンソース（BGE, mxbai, Jina等）**
- OSS は自己ホスト可能でプロプライエタリ依存を排除できる
- mxbai-rerank-v2 はBEIRベンチマークでのSOTA実績あり（nDCG Large: 57.49）
- Google Vertex AI は管理コスト不要のマネージドサービスとして差別化

### 総合ポジショニング

```
精度 (独立評価)
高 ↑
    |  Cohere  Voyage
    |
    |  [Google VA] ← 独立評価未確認
    |
    |  OSS models
低 ↓
    ←————————————————→
  GCP専用           クラウド非依存
```

Google Vertex AI Ranking API は **GCP ユーザー向けコスト効率重視の統合ソリューション**として位置付けられるが、マルチクラウド・クラウド非依存環境では競合に対してアドバンテージが薄い。

---

## 参考リンク

### 公式ドキュメント
- [Launching our new state-of-the-art Vertex AI Ranking API | Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/launching-our-new-state-of-the-art-vertex-ai-ranking-api)
- [Improve search and RAG quality with ranking API | Google Cloud Docs](https://docs.cloud.google.com/generative-ai-app-builder/docs/ranking)
- [Reranking for Agent Platform RAG Engine | Vertex AI Docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/retrieval-and-ranking)
- [Vertex AI Search pricing | Google Cloud](https://cloud.google.com/generative-ai-app-builder/pricing)

### 技術ブログ・実装記事
- [Reranking (Google Cloud Community Medium) | Sascha Heyer](https://medium.com/google-cloud/reranking-3b5f351cb398)
- [Vertex AI + Elastic for semantic search & reranking | Elasticsearch Labs](https://www.elastic.co/search-labs/blog/vertex-ai-elasticsearch-open-inference-api)
- [Hybrid search and semantic reranking with Elasticsearch and GCP | Elastic](https://www.elastic.co/search-labs/blog/hybrid-search-semantic-reranking-gcp-elasticsearch)
- [Experiment with Google Vertex AI Ranking API: Here's What I Found | metehan.ai](https://metehan.ai/blog/google-vertex-ai-ranking-api/)
- [Google Cloud Vertex AI Ranking API | LangChain4j Docs](https://docs.langchain4j.dev/integrations/scoring-reranking-models/vertex-ai/)

### ベンチマーク・比較
- [BEIR Evaluation Notebook (Google) | GitHub](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/search/ranking-api/ranking_api_beir_evaluation.ipynb)
- [Best Rerankers for RAG | Agentset.ai Leaderboard](https://agentset.ai/rerankers)
- [Top 7 Rerankers for RAG | Analytics Vidhya](https://www.analyticsvidhya.com/blog/2025/06/top-rerankers-for-rag/)
- [Top 8 Rerankers: Quality vs Cost | Medium](https://medium.com/@bhagyarana80/top-8-rerankers-quality-vs-cost-4e9e63b73de8)
- [Ultimate Guide to Choosing the Best Reranking Model | ZeroEntropy](https://zeroentropy.dev/articles/ultimate-guide-to-choosing-the-best-reranking-model-in-2025/)

### ユーザーレビュー
- [Vertex AI Reviews 2026 | G2](https://www.g2.com/products/google-vertex-ai/reviews)
- [Vertex AI Reviews & Ratings | Gartner Peer Insights](https://www.gartner.com/reviews/product/vertex-ai)
