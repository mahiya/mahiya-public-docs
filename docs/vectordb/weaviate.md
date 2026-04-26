# Weaviate 市場調査レポート

**製品/サービス**: Weaviate（OSS / Weaviate Cloud / Enterprise Cloud）
**開発元/提供元**: Weaviate B.V.（オランダ、アムステルダム）
**公式URL**: https://weaviate.io / https://docs.weaviate.io
**ライセンス**: BSD 3-Clause（コアOSS）
**調査時点**: 2026-04

---

## 1. 市場ポジション

### 概要

Weaviate はオープンソースのベクトルデータベースとして 2019 年にスタートし、現在は「AI-native vector database」から「agentic platform」へと立ち位置を拡張している。セマンティック検索・RAG・AIエージェント開発を主要ユースケースとして訴求しており、Pinecone・Qdrant・Milvus とともに専用ベクトル DB の四強に位置づけられる。

### 資金調達・企業規模

- 累計調達額: 約 $67.6M
- 直近ラウンド: Series C $50M（2025年10月、Battery Ventures・Zetta Venture Partners が主導）
- 推定評価額: $200M
- GitHub スター数: 13,000+（2026年4月時点）

### 採用状況

- G2・Gartner Peer Insights でレビューが増加中（Gartner 評価 4/5、サンプル数はまだ限定的）
- 医療・ヘルスケア企業を対象とした HIPAA 準拠クラウドを訴求し、エンタープライズ拡大中
- Dify、LangChain、LlamaIndex、Haystack などの主要 AI フレームワークとの統合を公開

### 競合との関係

| 競合 | Weaviate との差異 |
|------|-----------------|
| Pinecone | Pinecone は完全マネージド特化、Weaviate はOSS+クラウドの両立 |
| Qdrant | Qdrant は Rust 実装で低レイテンシ優位。Weaviate は機能多様性とエコシステムで対抗 |
| Milvus | Milvus は数億ベクトル超の超大規模で優位。Weaviate は中規模〜大規模でシンプルな運用を訴求 |

---

## 2. 開発元のアピールポイント

### ハイブリッド検索の第一級サポート

BM25F（フィールド重み付き BM25）によるキーワード検索とベクトル検索を組み合わせたハイブリッド検索をネイティブにサポート。フュージョンアルゴリズムは Relative Score Fusion（v1.24 以降のデフォルト）と Ranked Fusion（RRF）の2種類を提供。アルファ値（0〜1）で比率を調整可能。

### マルチテナンシーの設計思想

マルチテナンシーをコアアーキテクチャに組み込んでおり、テナントごとに専用シャードを割り当てることで論理的・物理的な分離を実現。遅延ローディング（Lazy Loading）によりテナントが使用されるまでメモリにロードしないため、数百万テナントの規模にも対応すると主張。

### モジュラーな AI 統合

ベクトル化・生成 AI・リランカーを「モジュール」として統合。OpenAI、Cohere、Google、Anthropic、Mistral、Voyage AI などの主要 API をモジュール設定で呼び出せる。外部埋め込みサービスに加え、自社の Weaviate Embeddings サービス（クラウド向け）も提供。

### エージェントプラットフォームへの拡張

2025 年後半より Query Agent（自然言語でデータ探索）・Transformation Agent・Personalization Agent を順次リリース。2026 年 2 月に Agent Skills を公開し、Claude Code・Cursor・GitHub Copilot などの AI コーディングエージェントと Weaviate を直接連携できるオープンソースリポジトリを提供。

### 豊富な量子化オプション

SQ・PQ・BQ に加え、v1.32 で Rotational Quantization（RQ）を追加。8-bit RQ は 4x 圧縮で 98〜99% Recall を維持（社内測定）、1-bit RQ は約 32x 圧縮。PQ/SQ は Recall 低下をリスコアリング（上位候補を元ベクトルで再計算）により緩和。

### マルチベクトル（Late Interaction）対応

v1.29 以降、ColBERT・ColPali 等のマルチベクトル埋め込みをネイティブサポート。MaxSim スコアリングを用いたレイト・インタラクション検索が可能。JinaAI の `jina-colbert-v2` モデルとの公式統合あり。

---

## 3. 市場・調査会社が評価している強み

### ハイブリッド検索の成熟度

複数の比較記事で「ハイブリッド検索（BM25+ベクトル）の実装が最も洗練されている」と評価される。フュージョンアルゴリズムの選択肢、アルファパラメータの柔軟性、フィールド重み付けなど、実運用に即した設定が可能な点が高評価。

### マルチモーダル対応

テキスト・画像・音声・動画など複数モダリティを単一コレクションで扱える。`multi2vec-google` モジュール（v1.37 で音声対応を追加）、CLIP ベースの画像ベクトル化など。マルチモーダル検索が必要な EC・メディア系ユースケースで強みを持つ。

### 優れた開発者体験（DX）

- GraphQL および REST/gRPC API を提供
- Python・TypeScript・Java・Go・C#（v1.34 より）のクライアント SDK を公式サポート
- Weaviate Embedded（ライブラリとして埋め込む軽量モード）も提供
- ドキュメントとサンプルコードが充実しており、学習コストが比較的低いという開発者評価が多い

### フィルタ付きベクトル検索（ACORN）

v1.34 から ACORN フィルタ戦略がデフォルト化。フィルタ条件が厳しい場合でも精度・速度のバランスが崩れにくい設計。事前フィルタ（Pre-filter）・後処理フィルタ（Post-filter）のいずれとも異なる、HNSW グラフ上でのインテリジェントなフィルタ適用。

### 可観測性とモニタリング

Prometheus メトリクス（/metrics エンドポイント）・Grafana ダッシュボードをネイティブサポート。v1.34 で 30 以上の新メトリクスを追加。クラウドネイティブな observability スタックとの親和性が高い。

---

## 4. 市場・調査会社が指摘している弱点・批判点

### レイテンシ・スループット性能

複数のサードパーティ比較において、Qdrant や FAISS に比べてレイテンシが高い傾向が指摘される。
- TensorBlue 比較記事（2025）: p99 レイテンシ 10ms（Qdrant 2ms、FAISS 3ms）、スループット 4,000 QPS（Qdrant 12,000 QPS）
- これらの数値はハードウェア・設定・データセットの条件が明記されておらず、正確な比較としては使用に注意が必要だが、「Weaviate は最速ではない」という評価は一致している

### メモリ使用量が多い

Go 実装の特性とインメモリ HNSW グラフの性質から、Qdrant（Rust 実装）と比べてメモリ効率が劣るとの指摘。特に大量のベクトルを保持する場合はコストが高くなりやすい。v1.36 の HFresh インデックス（ディスクベース）はこの問題への対応策だが Preview 段階。

### リシャーディングのコスト

HNSW インデックス構造の性質上、シャード数の変更（リシャーディング）が非常にコストが高い操作であることを公式ドキュメントが明記している。スケールアウト計画を事前に綿密に立てる必要があり、動的なリシャーディングには未対応。

### フリートライアルの制限

フリートライアルは 14 日間のみのサンドボックスで、その後は課金プランへの移行が必要。Qdrant（永続的な無料 OSS＋クラウド無料枠あり）と比較して、評価・検証フェーズでの導入障壁が高いという指摘がある。

### SPLADE 等の学習型スパースへの対応がない

ハイブリッド検索のキーワード側は BM25F に限定されており、SPLADE・ELSER・uniCOIL といった学習型スパース検索モデルのネイティブサポートはない（2026年4月時点）。ハイブリッド検索において Elasticsearch（ELSER）と比較した場合の差別化ポイントとして批判される場合がある。

### セルフホスト時の運用複雑性

マネージドクラウドと比べて、OSS セルフホストではレプリケーション設定・バックアップ・アップグレード管理を手動で行う必要がある。Milvus ほどではないが、専門知識が必要との声がある。

---

## 5. ベンチマーク・競合比較・その他

### 公式 ANN ベンチマーク（Weaviate ドキュメント掲載）

ハードウェア: GCP `n4-highmem-16`（16 vCPU、128 GB RAM）、クライアント 8 スレッド

| データセット | 次元 | 件数 | Recall@10 | QPS | 平均レイテンシ | p99 レイテンシ |
|------------|------|------|-----------|-----|-------------|-------------|
| DBPedia（OpenAI） | 1,536 | 1M | 97.24% | 5,639 | 2.80ms | 4.43ms |
| SIFT1M | 128 | 1M | 98.35% | 10,940 | 1.44ms | 3.13ms |
| MSMARCO（Snowflake） | 768 | 8.8M | 97.36% | 7,363 | 2.15ms | 3.69ms |
| Sphere DPR | 768 | 10M | 96.06% | 3,523 | 4.49ms | 7.73ms |

注意: 上記はエンドツーエンドのレイテンシ（ネットワーク往復・オブジェクト取得含む）。推奨設定でのパレート最前線値であり、最大 QPS ではない。

### インデックス種類と特性

| インデックス | 状態 | 特性 |
|------------|------|------|
| HNSW | GA | デフォルト。大規模データセットで高速。グラフベースで対数時間計算量 |
| Flat | GA | 小規模コレクション向け（マルチテナンシーなど）。線形探索 |
| Dynamic | GA | Flat から HNSW への自動遷移（閾値デフォルト: 10,000 件） |
| HFresh | Preview（v1.36〜） | ディスクベース。高次元大規模データのメモリ効率を重視。クラスタベース HNSW |

### 量子化サポート一覧

| 手法 | 状態 | 圧縮率 | Recall 影響 |
|------|------|--------|------------|
| Scalar Quantization（SQ, 8-bit int） | GA | 4x | 低損失 |
| Product Quantization（PQ） | GA | 最大 24x | 中損失（リスコア可） |
| Binary Quantization（BQ, 1-bit） | GA | 32x | 高損失（特定モデルと相性あり） |
| Rotational Quantization（RQ 8-bit） | GA（v1.32〜） | 4x | 98〜99% Recall 維持（社内値） |
| Rotational Quantization（RQ 1-bit） | GA（v1.35〜 flat/v1.32〜 HNSW） | 32x | BQ より高精度 |

### 価格・提供形態

| プラン | 月額 | SLA | サポート |
|--------|------|-----|---------|
| Free Trial | 無料（14日） | なし | フォーラムのみ |
| Flex | $45〜 | 99.5% | メール、翌営業日 Sev1 |
| Premium | $400〜 | 99.95% | Slack・電話・TAM、1時間 Sev1 |

- 価格変数: ベクトル次元数・ストレージ量・バックアップ容量・リージョン
- セルフホスト（OSS）は無償（BSD 3-Clause）

### セキュリティ・コンプライアンス

- SOC 2 Type II: 取得済み
- HIPAA: AWS 上の Enterprise Cloud で対応済み、Azure は近日対応予定
- ISO 27001:2022: Phase 1 監査完了、本認定は 2026 年予定
- エンドツーエンド暗号化（TLS/mTLS + AES-256 at rest）
- Premium プランのみ: SSO/SAML、PrivateLink（AWS）、カスタマーキー暗号化ボリューム

### デプロイ・運用

- Docker / Docker Compose（開発・テスト向け）
- Helm チャート（v17.8.0）/ Kubernetes
- Weaviate Embedded（Python/Node.js ライブラリとして埋め込み可）
- バックアップ: スナップショットに加え、v1.37 から増分バックアップ（Incremental Backup）対応
- Apache Parquet 形式でのコレクションエクスポート（v1.37、クラウドストレージ・ローカル対応）
- アップグレード: Shared Cloud では「versionless cluster」（自動アップグレード）を提供

### マルチテナンシー

- テナント = コレクション内の専用シャード
- テナント単位でのアクティブ/非アクティブ切り替え（オフロード機能）
- 遅延ローディングにより非アクティブテナントはメモリ非消費
- 各テナントの独立した flat + RQ インデックス対応（v1.34）
- 課題: テナント間のデータ量差が大きい場合の不均一シャーディング（GitHub Issue あり）

### ハイブリッド検索・スパース・Late Interaction

- **BM25F ハイブリッド**: GA。フュージョンアルゴリズム（Relative Score Fusion / RRF）、アルファ調整、フィールド重み付けに対応
- **SPLADE 等の学習型スパース**: 未サポート（2026年4月時点）
- **ColBERT / ColPali マルチベクトル**: v1.29 以降でサポート。MaxSim スコアリングを実装。JinaAI `jina-colbert-v2` との公式統合あり
- **MMR（Maximum Marginal Relevance）多様性検索**: v1.37 でプレビュー追加

### リランカー

- Hugging Face Transformers の Cross-Encoder モデル（ms-marco-MiniLM 系）を外部コンテナとして連携（セルフホストのみ、WCD 非対応）
- Cohere Rerank、Voyage AI Reranker との API 連携（クラウド・セルフホスト共通）
- Contextual AI リランカー統合（v1.34 追加）
- 外部推論サービスとの 2 段階パイプライン（Bi-Encoder 検索 → リランカー）として構成

### 最新リリース動向

| バージョン | 主要トピック |
|-----------|------------|
| v1.34 | ACORN フィルタデフォルト化、Flat + RQ Preview、30+ 新メトリクス、C# クライアント |
| v1.35 | Object TTL、zstd 圧縮、Flat RQ GA、マルチモーダル Embeddings |
| v1.36 | HFresh インデックス Preview、Server-side Batching GA、非同期レプリケーション改善 |
| v1.37 | MCP サーバー Preview、MMR 多様性検索 Preview、増分バックアップ、クエリプロファイリング |
| 2026/02 | Agent Skills 公開（Claude Code・Cursor・Copilot との統合） |

---

## 6. 参考URL

### 公式ドキュメント

- [Weaviate 概要ドキュメント](https://docs.weaviate.io/weaviate)
- [ベクトルインデックスの概念](https://docs.weaviate.io/weaviate/concepts/vector-index)
- [量子化（Vector Quantization）の概念](https://docs.weaviate.io/weaviate/concepts/vector-quantization)
- [ハイブリッド検索ガイド](https://docs.weaviate.io/weaviate/search/hybrid)
- [レプリケーションアーキテクチャ](https://docs.weaviate.io/weaviate/concepts/replication-architecture)
- [公式 ANN ベンチマーク](https://docs.weaviate.io/weaviate/benchmarks/ann)
- [マルチベクトル埋め込みチュートリアル](https://docs.weaviate.io/weaviate/tutorials/multi-vector-embeddings)
- [リランカー（Transformers）](https://docs.weaviate.io/weaviate/model-providers/transformers/reranker)
- [Kubernetes デプロイガイド](https://docs.weaviate.io/deploy/installation-guides/k8s-installation)

### 公式ブログ

- [Weaviate 1.34 リリースノート](https://weaviate.io/blog/weaviate-1-34-release)
- [Weaviate 1.37 リリースノート](https://weaviate.io/blog/weaviate-1-37-release)
- [Weaviate in 2025: 基盤強化の一年](https://weaviate.io/blog/weaviate-in-2025)
- [ハイブリッド検索解説](https://weaviate.io/blog/hybrid-search-explained)
- [8-bit Rotational Quantization 解説](https://weaviate.io/blog/8-bit-rotational-quantization)
- [マルチテナンシーアーキテクチャ解説](https://weaviate.io/blog/weaviate-multi-tenancy-architecture-explained)
- [Agent Skills 発表](https://weaviate.io/blog/weaviate-agent-skills)
- [Late Interaction モデル概観](https://weaviate.io/blog/late-interaction-overview)
- [Cross-Encoder リランカー解説](https://weaviate.io/blog/cross-encoders-as-reranker)
- [HIPAA 準拠クラウド発表](https://weaviate.io/blog/weaviate-hipaa-compliant)
- [スケーリング解説](https://weaviate.io/blog/scaling-and-weaviate)
- [プロダクション監視ガイド](https://weaviate.io/blog/monitoring-weaviate-in-production)

### 価格・セキュリティ

- [料金ページ](https://weaviate.io/pricing)
- [セキュリティページ](https://weaviate.io/security)

### サードパーティ比較・評価

- [Gartner Peer Insights - Weaviate](https://www.gartner.com/reviews/market/search-and-product-discovery/vendor/weaviate/product/weaviate)
- [TensorBlue: 4製品比較 2025](https://tensorblue.com/blog/vector-database-comparison-pinecone-weaviate-qdrant-milvus-2025)
- [Cipher Projects: Weaviate vs Qdrant 2025](https://cipherprojects.com/blog/posts/weaviate-vs-qdrant-vector-database-comparison-2025/)
- [VectorDBBench GitHub](https://github.com/zilliztech/VectorDBBench)
- [Series C 資金調達 PR](https://www.prnewswire.com/news-releases/weaviate-raises-50-million-series-b-funding-to-meet-soaring-demand-for-ai-native-vector-database-technology-301803296.html)
- [Agent Skills 発表（GlobeNewswire）](https://www.globenewswire.com/news-release/2026/02/21/3242244/0/en/Weaviate-Launches-Agent-Skills-to-Empower-AI-Coding-Agents.html)

### GitHub

- [weaviate/weaviate](https://github.com/weaviate/weaviate)
- [weaviate/weaviate-helm](https://github.com/weaviate/weaviate-helm)
- [weaviate/agent-skills](https://github.com/weaviate/agent-skills)

---

## まとめ表

| 項目 | 値 |
|------|---|
| 提供元 / ライセンス | Weaviate B.V. / BSD 3-Clause（OSS） |
| 位置付け | AI-native 専用ベクトル DB + Agentic Platform |
| 最新バージョン | v1.37（2026年1月頃リリース） |
| 対応インデックス種類 | HNSW（デフォルト）、Flat、Dynamic（自動遷移）、HFresh（Preview） |
| 最大次元数 | 記載なし（実用例では最大 1,536 次元、型による制限の公式文書なし） |
| 量子化対応（SQ / PQ / Binary / RQ 等） | SQ（8-bit）/ PQ（最大24x）/ BQ（1-bit, 32x）/ RQ 8-bit（4x）/ RQ 1-bit（32x） |
| シャーディング / レプリケーション | 自動シャーディング（Murmur-3ハッシュ）+ リーダーレス分散レプリケーション（Raft でメタ管理） |
| コンピュート/ストレージ分離 | 部分的（HFresh インデックスがディスクベース、フルの C/S 分離アーキテクチャは記載なし） |
| 公称最大データ規模 | 公式の上限値は記載なし（10M ベクトルの公式ベンチあり、マルチテナント時は数百万テナント対応と主張） |
| 公式ベンチマーク（QPS / Recall） | SIFT1M: 10,940 QPS / 98.35% Recall@10、DBPedia-1M: 5,639 QPS / 97.24% Recall@10（GCP n4-highmem-16） |
| フィルタ付き検索 | ACORN（v1.34 デフォルト化）。HNSW グラフ上でインテリジェントフィルタ適用 |
| ハイブリッド検索（BM25+Vector） | BM25F ネイティブ対応。Relative Score Fusion / RRF、アルファパラメータ調整可 |
| SPLADE / 学習型スパース対応 | 未サポート（BM25F のみ） |
| Late Interaction（ColBERT 等）対応 | v1.29 以降で ColBERT / ColPali マルチベクトル対応（MaxSim スコアリング） |
| Cross-Encoder リランカー対応 | あり（Hugging Face cross-encoder / Cohere / Voyage AI / Contextual AI）。セルフホストは外部コンテナ、クラウドは API 連携 |
| リコメンド API / 機能 | MMR 多様性検索（v1.37 Preview）。Qdrant の recommend API 相当の専用エンドポイントは記載なし |
| 提供形態（OSS / Managed / Enterprise） | OSS（BSD 3-Clause）/ Weaviate Cloud（Flex $45〜、Premium $400〜）/ Enterprise Cloud |
| SLA / コンプライアンス | Flex 99.5% / Premium 99.95%。SOC 2 Type II、HIPAA（AWS Premium）、ISO 27001 Phase 1 完了 |
| 価格モデル | 次元数・ストレージ・バックアップ・リージョン従量。セルフホスト無償 |
| デプロイ手段 | Docker / Docker Compose / Helm（v3+）/ Kubernetes / Weaviate Embedded（ライブラリ組込み）|
| マルチテナンシー | テナント=専用シャード。遅延ローディング、数百万テナント対応、テナント単位 flat+RQ 対応 |
| 可観測性 | Prometheus /metrics エンドポイント、Grafana 統合、Datadog エージェント対応、v1.37 クエリプロファイリング |
| バックアップ / リストア | スナップショット + 増分バックアップ（v1.37 GA）。Parquet エクスポート（v1.37） |
| 特徴的な機能 | Agent Skills（Claude Code/Cursor/Copilot 統合）、MCP サーバー（Preview）、Query/Transformation/Personalization Agent、RQ 量子化、HFresh ディスクインデックス |
