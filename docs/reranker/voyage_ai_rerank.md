# Voyage AI Rerank 市場調査レポート

> 調査日: 2026年4月25日

---

## 基本情報

| 項目 | 内容 |
|------|------|
| プロダクト名 | Voyage AI Rerank |
| 開発元 | Voyage AI（2025年2月にMongoDBが買収） |
| 公式サイト | https://www.voyageai.com/ |
| ドキュメント | https://docs.voyageai.com/docs/reranker |
| MongoDB統合ページ | https://www.mongodb.com/products/platform/ai-search-and-retrieval |
| 最新モデル | `rerank-2.5`、`rerank-2.5-lite`（2025年8月11日リリース） |

### 利用可能なモデル一覧

| モデル | コンテキスト長 | 価格（/1M tokens） | 無料枠 | 特徴 |
|--------|--------------|-----------------|------|------|
| `rerank-2.5` | 32,000 tokens | $0.050 | 2億トークン | 最高精度、命令追従機能搭載 |
| `rerank-2.5-lite` | 32,000 tokens | $0.020 | 2億トークン | レイテンシ最適化、コスト効率重視 |
| `rerank-2` | 16,000 tokens | $0.050 | なし | 第二世代、多言語対応 |
| `rerank-2-lite` | 8,000 tokens | $0.020 | なし | 第二世代、レイテンシ・品質バランス |

**価格計算式**: `(クエリトークン数 × ドキュメント数) + 全ドキュメントのトークン合計`

**推定コスト**: 100ドキュメント・クエリ+各ドキュメント計500トークンの場合、`rerank-2.5`は約$0.0025/リクエスト、`rerank-2.5-lite`は約$0.001/リクエスト

**Batch API**: 標準エンドポイント比33%割引

---

## 市場ポジション

### 企業背景・市場立ち位置

- **MongoDB傘下**: 2025年2月24日、MongoDBがVoyage AIを買収。Voyage AIの埋め込み・リランキングモデルをMongoDB Atlasに統合予定
- **Anthropicのデフォルト採用**: Voyage AIのモデルはAnthropicの推奨埋め込みモデル。Anthropicが「Contextual Retrieval」手法の公式ブログでVoyage AIのリランカーを推奨
- **Hugging Faceコミュニティ評価**: 埋め込みモデルはHugging Faceの「最高評価のゼロショットモデル」として認識
- **主要エンタープライズ採用事例**: Anthropic、LangChain、Harvey（Am Law 100の97%が利用する法律AI）、Replitなど

### リーダーボード上の順位（Agentset調べ、2025年）

全12モデル中4位（ELO: 1544）。`rerank-2.5`は品質指標（nDCG@10）では2位の高水準。

| 順位 | モデル | ELO | nDCG@10 | レイテンシ | 価格/1M tokens |
|------|--------|-----|---------|-----------|--------------|
| 1 | Zerank 2 | 1638 | 0.079 | 265ms | $0.025 |
| 2 | Cohere Rerank 4 Pro | 1629 | 0.095 | 614ms | $0.050 |
| 3 | Zerank 1 | 1573 | 0.082 | 266ms | $0.025 |
| **4** | **Voyage AI Rerank 2.5** | **1544** | **0.110** | **613ms** | **$0.050** |
| 5 | Voyage AI Rerank 2.5 Lite | 1520 | - | - | $0.020 |
| - | Cohere Rerank 4 Fast | 1510 | 0.094 | 447ms | $0.050 |

- **勝率**: 58.0%（全12モデル中1位）
- **nDCG@10精度**: 0.110（全モデル中2位）
- 総評価件数3,300件中、勝利1,915件（58.0%）、敗北1,270件（38.5%）

---

## 開発元のアピールポイント

### 1. 命令追従（Instruction-Following）機能（rerank-2.5で初搭載）

- 自然言語指示でリランキング挙動を動的に制御可能
- 例: 「学術論文検索では論文タイトルを優先し、要約は無視すること」
- MAIR（Massive Instructed Retrieval Benchmark）で命令追従時の精度向上:
  - `rerank-2.5`: 実世界アプリケーションで +11.48%
  - `rerank-2.5-lite`: 実世界アプリケーションで +7.83%

### 2. 業界最大級のコンテキスト長

- **32,000 tokens**: Cohere Rerank v3.5の8倍、`rerank-2`の2倍
- 長文ドキュメントを切り詰めなしでリランキング可能

### 3. LLMリランカーとの比較優位（2025年10月公式ブログ発表）

| 指標 | rerank-2.5 | Claude Sonnet 4.5 | GPT-5 | Gemini 2.5 Pro |
|------|-----------|------------------|-------|---------------|
| NDCG@10 | 84.32% | 優位 | 優位 | 優位 |
| 速度 | 基準 | 9x遅い | 36x遅い | 48x遅い |
| コスト | $0.05/1M | ~$3/1M | ~$3/1M | ~$1.25/1M |

- LLMと比較して最大60x安く、48x高速、15% nDCG@10向上を実現
- Gemini 2.0 Flashの100万トークンウィンドウでの単一パス処理より、スライディングウィンドウ方式のリランカーが26.6%以上精度で上回ることを実証

### 4. コスト効率の向上（rerank-2比較）

- `rerank-2.5`: 同価格でrerank-2比+1.85%精度向上
- `rerank-2.5-lite`: 同価格でrerank-2-lite比+3.40%精度向上

### 5. クロスエンコーダーアーキテクチャ

- クエリとドキュメントを個別にエンコードせず、ペアを同時処理
- 埋め込みモデルや BM25/TF-IDF などの第一段階検索を補完・精度向上

---

## 第三者評価：強み

### 精度・品質面

- **Analytics Vidhya（2025年6月）**: 「State-of-the-art relevance, potentially the most accurate option available」（純粋な関連性精度でベンチマークをリードすることが多い）と評価
- **Medium（Mudassar Hakim氏）**: 深いセマンティック理解、推論型クエリへの対応力、長文文書内の根本原因箇所の発見能力を高評価
- **Agentset評価**: nDCG@10で0.110と全モデル中2位の精度スコア（Cohere Rerank 4 Proの0.095を上回る）

### 速度・バランス面

- **Agentset評価**: 「品質とレイテンシーのバランスが最も優れた選択肢」として位置付け
- Cohere v3.5と比較して約2倍低いレイテンシーで同等品質を実現（「RAGパイプラインの実用的なスイートスポット」）
- 勝率58.0%は全評価モデル中トップ

### 安定性・汎用性

- 金融、ビジネス、エッセイ、ウェブ、事実、科学の6ドメインで安定したパフォーマンス
- 「信頼できる汎用的なモデル」として認識（Agentset評価）

### 弱い第一段階検索との組み合わせ効果

- `voyage-3-lite`（弱い埋め込み検索）との組み合わせで+15.02%向上
- BM25等の語彙検索との組み合わせで+47.57%向上
- リランカーとしての底上げ効果が特に大きい

### エコシステム統合

- LangChain、LlamaIndex、Milvus、LanceDB、KDB.AI 等の主要フレームワークが公式統合をサポート
- AWSマーケットプレイスでも提供（`rerank-lite-1`）
- AnthropicのContextual Retrieval手法の推奨モデルとして採用

---

## 第三者評価：弱点・批判点

### 1. ELOスコアでは新興勢力に後れを取る

- Agentset ELOランキングでは Zerank 2（1638）、Cohere Rerank 4 Pro（1629）、Zerank 1（1573）に次ぐ4位（1544）
- 特にZerank系モデルはELOでは明確に上回るため、ELO重視の選定では不利

### 2. レイテンシがトップクラスではない

- 613ms と、競合の Cohere Rerank 4 Fast（447ms）や Zerank 2（265ms）より遅い
- レイテンシ重視のアプリケーションでは不利な位置付け

### 3. クローズドAPIのみの提供（オープンソースなし）

- オープンソースモデルを提供していないため、オンプレミス・エアギャップ環境への展開不可
- BGE Reranker v2-M3 などのオープンソース競合と比較して運用コストの透明性が低い

### 4. 一部データセットでのパフォーマンス格差

- Agentset評価でDBPedia等の特定データセットでnDCG@10 = 0.000と極端に低いスコア
- FiQa（金融）ではCohere Rerank 4 Fast（0.138）に対してVoyage（0.119）と劣後

### 5. 命令追従機能の有効性はユースケース依存

- 命令追従機能はドメイン固有データで+8.13%改善するが、効果は用途によって大きく異なる
- 命令の設計・チューニングに追加コストが発生する可能性

### 6. MongoDB傘下移行による不確実性

- 2025年2月のMongoDB買収後、Voyage AI独立製品としての開発方針が不透明
- MongoDB AtlasへのロックインリスクがAPIユーザーへの懸念材料になる可能性

---

## ベンチマーク結果

### 標準ベンチマーク（93データセット・4種の第一段階検索平均）

| 比較対象 | rerank-2.5の優位 | rerank-2.5-liteの優位 |
|---------|--------------|-----------------|
| vs Cohere Rerank v3.5 | +7.94% | +7.16% |
| vs Qwen3-Reranker-8B | +2.34% | - |
| vs rerank-2 | +1.35% | - |

### MAIR（Massive Instructed Retrieval Benchmark・命令追従ベンチマーク）

| 比較対象 | rerank-2.5の優位 | rerank-2.5-liteの優位 |
|---------|--------------|-----------------|
| vs Cohere Rerank v3.5 | +12.70% | +10.36% |

### 第一段階検索との組み合わせ効果

| 第一段階検索 | リランキング後の改善 |
|------------|----------------|
| voyage-3-large + rerank-2.5 | NDCG@10: 84.32% |
| voyage-3-lite + rerank-2.5 | +15.02% |
| BM25（語彙検索）+ rerank-2.5 | +47.57% |

### LLMリランカーとの比較（rerank-2.5基準）

| 指標 | rerank-2.5 | vs LLM全般 |
|------|-----------|-----------|
| 速度 | 最速クラス | 最大48倍高速 |
| コスト | $0.05/1M | 最大60倍安価 |
| NDCG@10改善 | 基準 | 最大+15% |

### Agentset ELOリーダーボード（2025年）

| モデル | ELO | nDCG@10 | レイテンシ |
|--------|-----|---------|-----------|
| Zerank 2 | 1638 | 0.079 | 265ms |
| Cohere Rerank 4 Pro | 1629 | 0.095 | 614ms |
| Zerank 1 | 1573 | 0.082 | 266ms |
| **Voyage AI Rerank 2.5** | **1544** | **0.110** | **613ms** |
| Voyage AI Rerank 2.5 Lite | 1520 | - | - |
| Cohere Rerank 4 Fast | 1510 | 0.094 | 447ms |

---

## 競合比較

### 主要リランカーの総合比較

| 項目 | Voyage AI rerank-2.5 | Cohere Rerank 4 Pro | Zerank 2 | Jina Reranker | ZeroEntropy |
|------|---------------------|--------------------|---------|--------------|-----------:|
| **ELO** | 1544（4位） | 1629（2位） | 1638（1位） | - | - |
| **nDCG@10** | 0.110（2位） | 0.095 | 0.079 | - | - |
| **レイテンシ** | 613ms | 614ms | 265ms | - | - |
| **価格/1M tokens** | $0.050 | $0.050 | $0.025 | - | - |
| **コンテキスト長** | 32,000 | 4,096 | - | - | - |
| **命令追従** | あり | なし | - | なし | - |
| **OSS** | なし | なし | なし | あり | なし |
| **多言語対応** | あり | あり | - | あり | - |

### vs Cohere Rerank

- **Voyage優位点**: nDCG@10精度（0.110 vs 0.095）、コンテキスト長（32K vs 4K）、命令追従機能、弱い第一段階検索との組み合わせ効果が大きい
- **Cohere優位点**: ELOスコア（Rerank 4 Pro: 1629 > Voyage: 1544）、Cohere Rerank 4 Fastはレイテンシ優位（447ms vs 613ms）、技術文書・ビジネス文書での強み
- **価格**: 同等（どちらも$0.050/1M）

### vs Zerank（ZeroEntropy）

- **Zerank優位点**: ELOスコアでトップ（Zerank 2: 1638）、レイテンシが約2.3倍高速（265ms vs 613ms）、価格も半額（$0.025 vs $0.050）
- **Voyage優位点**: nDCG@10精度が高い（0.110 vs 0.079）、命令追従機能、実績・信頼性（MongoDB/Anthropic等のエンタープライズ採用）

### vs Jina Reranker

- **Jina優位点**: オープンソース版あり（オンプレ展開可能）、BEIR（Large: 57.49、Base: 55.57）でCohereやVoyageを上回るとの一部報告
- **Voyage優位点**: API品質の安定性、エコシステム統合の幅広さ、命令追従機能

### vs BGE Reranker（オープンソース）

- **BGE優位点**: 完全オープンソース、自己ホスト可能、データプライバシー確保、ゼロ追加コスト
- **Voyage優位点**: 精度面で一般的に優位、マネージドAPI、スケーラビリティ

### ユースケース別推奨

| ユースケース | 推奨モデル | 理由 |
|------------|-----------|------|
| 最高精度重視（法律・金融） | Voyage rerank-2.5 または Cohere Rerank 4 Pro | 高nDCG@10 |
| 速度最優先 | Zerank 2 | 265ms、高ELO |
| コスト最小化 | Voyage rerank-2.5-lite（$0.020） | 低コスト・無料枠2億トークン |
| 長文ドキュメント | Voyage rerank-2.5 | 32Kコンテキスト（業界最大） |
| 命令・エージェント型RAG | Voyage rerank-2.5 | 唯一の命令追従リランカー（商用API） |
| オンプレ・エアギャップ | Jina / BGE Reranker | OSSモデル |
| MongoDB Atlas統合 | Voyage rerank-2.5 | ネイティブ統合予定 |

---

## 参考リンク

### 公式ドキュメント・ブログ

- [Voyage AI 公式サイト](https://www.voyageai.com/)
- [Voyage AI リランカー ドキュメント](https://docs.voyageai.com/docs/reranker)
- [rerank-2.5 リリースブログ（2025年8月）](https://blog.voyageai.com/2025/08/11/rerank-2-5/)
- [rerank-2 リリースブログ（2024年9月）](https://blog.voyageai.com/2024/09/30/rerank-2/)
- [The Case Against LLMs as Rerankers（2025年10月）](https://blog.voyageai.com/2025/10/22/the-case-against-llms-as-rerankers/)
- [Voyage AI 価格ページ](https://docs.voyageai.com/docs/pricing)
- [MongoDB Voyage AI モデル一覧](https://www.mongodb.com/docs/voyageai/models/rerankers/)

### MongoDB関連

- [MongoDB による Voyage AI 買収発表](https://investors.mongodb.com/news-releases/news-release-details/mongodb-announces-acquisition-voyage-ai-enable-organizations)
- [MongoDB Voyage AI 製品ページ](https://www.mongodb.com/products/platform/ai-search-and-retrieval)
- [rerank-2.5 MongoDB ブログ](https://www.mongodb.com/company/blog/product-release-announcements/rerank-2-5-and-rerank-2-5-lite-instruction-following-rerankers)

### 第三者評価・比較

- [Best Rerankers for RAG Leaderboard（Agentset）](https://agentset.ai/rerankers)
- [Best Reranker for RAG テストレポート（Agentset Blog）](https://agentset.ai/blog/best-reranker)
- [Voyage AI Rerank 2.5 詳細（Agentset）](https://agentset.ai/rerankers/voyage-ai-rerank-25)
- [Voyage vs Cohere 比較（Agentset）](https://agentset.ai/rerankers/compare/voyage-ai-rerank-25-vs-cohere-rerank-4-fast)
- [Ultimate Guide to Reranking Models 2026（ZeroEntropy Blog）](https://zeroentropy.dev/articles/ultimate-guide-to-choosing-the-best-reranking-model-in-2025/)
- [Top 7 Rerankers for RAG（Analytics Vidhya）](https://www.analyticsvidhya.com/blog/2025/06/top-rerankers-for-rag/)
- [Why Re-Rankers Decide RAG Quality（Medium）](https://medium.com/@mudassar.hakim/why-re-rankers-decide-rag-quality-choosing-between-open-source-cohere-and-voyage-1536fe4ca808)

### エコシステム統合

- [LangChain VoyageAI Reranker](https://python.langchain.com/docs/integrations/document_transformers/voyageai-reranker/)
- [Milvus Voyage AI Ranker](https://milvus.io/docs/voyage-ai-ranker.md)
- [LanceDB VoyageAI Reranker](https://docs.lancedb.com/integrations/reranking/voyageai)
- [KDB.AI Voyage AI Reranker](https://docs.kx.com/1.7/KDB_AI/How_to/use-rerankers-in-KDB_AI.htm)
- [AWS SageMaker + Voyage AI RAG アーキテクチャ](https://aws.amazon.com/blogs/machine-learning/rag-architecture-with-voyage-ai-embedding-models-on-amazon-sagemaker-jumpstart-and-anthropic-claude-3-models/)
