# Milvus / Zilliz Cloud 市場調査レポート

**調査時点**: 2026-04

---

## 1. 市場ポジション

### 概要

Milvusは2019年にZilliz社（中国発のスタートアップ）が開発・オープンソース化した専用ベクトルデータベースで、LF AI & Data Foundationのトップレベルプロジェクトとして採択されている。ライセンスはApache 2.0で、商用利用・フォーク・再配布がすべて自由に行える。

### GitHubスター数と採用規模

- **40,000+ GitHubスター**（2025年12月時点）。専用ベクトルDB OSS の中で最多スターを誇り、Qdrant・Weaviateを大きく上回る
- **10,000社以上のエンタープライズ**が本番AIシステムで利用（2025年12月時点）
- 代表的な採用企業: NVIDIA、Salesforce、eBay、Airbnb、DoorDash
- 2025年時点でのDockerプル数は約700,000/月（Weaviateの1M+より少ないが業界上位水準）

### 市場における位置付け

- **大規模ベクトル検索のデファクトスタンダード的 OSS**: 数十億ベクトルの本番運用実績を持つ製品として、PineconeやQdrantとともに最有力候補の一つ
- **Zilliz Cloud**: OSS版のマネージドサービスとして、AWS / Azure / Google Cloud上で提供
- 市場調査会社はベクトルDB市場が2030年までに数百億ドル規模に拡大すると予測しており、Milvusはその中核プレイヤーの一つと評価されている

### 競合との関係

| 競合製品 | ポジションの違い |
|---|---|
| Pinecone | フルマネージド・サーバーレスで運用負荷ゼロ。Milvusより開発者体験が簡単だがOSSではなく、大量ベクトルでコスト高 |
| Qdrant | Rustベースで低レイテンシ・高QPS。小〜中規模でQdrantが有利; Milvusは超大規模に強み |
| Weaviate | ハイブリッド検索とマルチモーダル対応に強み。マネージドクラウドあり |
| Elasticsearch | 全文検索の老舗。ベクトル検索は後付けでMilvusより性能で劣る場面が多い |

---

## 2. 開発元のアピールポイント

Milvus公式サイト・Zillizブログ・ドキュメントが主張している差別化ポイントを以下に整理する。

### 2-1. 大規模対応のクラウドネイティブアーキテクチャ

- **コンピュート・ストレージ分離**: 生ベクトルとインデックスをオブジェクトストレージ（MinIO / S3）に格納し、クエリノードは必要に応じてキャッシュ。ワーカーノードはステートレスで水平スケールが容易
- **マイクロサービス構成**: Access Layer / Coordinator Layer / Worker Layer / Storage Layer の4層アーキテクチャ。コンポーネントごとに独立スケール可能
- **Woodpecker WAL (v2.6)**: Kafka/Pulsarを置き換えるクラウドネイティブなWrite-Ahead Logを内蔵し、外部メッセージキューへの依存を排除。ディスクレスアーキテクチャを実現
- **Streaming Node (v2.6)**: リアルタイムデータ取り込み専用コンポーネント。新データは即座に検索可能になる（バッチ遅延なし）

### 2-2. 多様なインデックスと量子化技術

- **10種類以上のインデックス**: FLAT / IVF_FLAT / IVF_SQ8 / IVF_PQ / HNSW / DiskANN / SCANN (GPU_IVF_FLAT / GPU_IVF_PQ / GPU_CAGRA)
- **RaBitQ (v2.6新規)**: 1ビット量子化による最大72%メモリ削減。IVF_RABITQインデックスはIVF_FLATの1/32のメモリでRecall 94.7%を実現し、スループットは3.6倍以上
- **GPU加速 (CAGRA / cuVS)**: NVIDIA RAPIDS cuVSを使ったGPUインデックスで、CPU HNSW比最大50倍の検索速度を公称
- **mmap対応**: ローカルディスクをキャッシュとして活用し、メモリ容量を超えるデータセットを処理可能

### 2-3. ハイブリッド検索・全文検索の統合 (v2.5/2.6)

- **BM25フルテキスト検索**: v2.5でBM25をネイティブ統合。テキストを自動的にスパースベクトルに変換
- **多言語対応 (v2.6)**: `language_identifier`トークナイザーで自動言語検出。日本語・韓国語などアジア言語の高度なトークナイズを実装
- **スパースベクトルフィールド**: SPLADEなどの学習型スパースモデルのベクトルを直接格納可能
- **マルチベクトルハイブリッド検索**: Dense + Sparse + BM25 を1リクエストで並列実行し、RRFで融合

### 2-4. コスト削減とTCO最適化

- RaBitQ量子化 + 段階的ホット/コールドストレージにより、同等の性能を75%少ないサーバーで実現（公称）
- OpenSearchからの移行事例で最大8倍のコスト削減を報告
- Milvus 2.6は4倍高速 (Elasticsearch比) と72%メモリ削減を同時達成と主張

### 2-5. エンタープライズ機能 (主にZilliz Cloud)

- SOC 2 Type II・ISO/IEC 27001:2022取得
- GDPR完全対応・HIPAA対応・EU-U.S. Data Privacy Framework認証
- CMEK（顧客管理暗号化キー）GA対応（2026年3月）
- RBAC、TLS 1.2+暗号化、監査ログ

---

## 3. 市場・調査会社が評価している強み

### 3-1. 超大規模対応

- 数十億ベクトルの本番運用実績が業界で最も豊富なOSS製品の一つ
- PineconeやWeaviateが数百万〜数千万ベクトルを主戦場とする中、Milvusは10億規模を当たり前に扱う
- Walmart・eBay・Airbnbなどの大規模ECでの採用事例が市場での信頼性を高めている

### 3-2. インデックスの豊富さ・柔軟性

- IVF系・グラフ系（HNSW）・ディスク系（DiskANN）・GPU系（CAGRA）を全て揃えており、ユースケースに応じた最適化が可能
- G2評価（4.4/5）: 「スケーラビリティとエンタープライズ対応性で注目されている」

### 3-3. 取り込みスループット

- f22labsのベンチマークでは、データ取り込み速度でQdrant（41.27秒）比3.4倍高速（12.02秒）
- インデックス構築速度も0.60秒と非常に速い
- VectorDBBenchでの挿入スループット: 38,500 vectors/秒（100Mベクトルスケール）

### 3-4. フィルタ付きベクトル検索の安定性

- ACORNアルゴリズム（HNSWグラフの枝刈りをスキップしてフィルタ耐性を高める方式）をサポート
- Cohere 1Mテストで、MilvusはフィルタSelectivityが変化しても高いRecallを安定維持。OpenSearchはフィルタ条件変化で大きくRecallが揺れた

### 3-5. Apache 2.0ライセンス

- BSL（Weaviate）やSSPL（MongoDB系）と異なり、完全にオープンで商用利用・マネージドサービス構築も制限なし
- エンタープライズがセルフホストを選択しやすいライセンスポリシー

### 3-6. GPU加速

- CAGRA（NVIDIA製グラフアルゴリズム）+ cuVS統合により、CPU HNSWの最大50倍の高速化
- インデックス構築もGPUで高速化し、大量データの再インデックスコストを削減

---

## 4. 市場・調査会社が指摘している弱点・批判点

### 4-1. 運用の複雑さ（最大の批判点）

- **本番クラスタは膨大な依存関係**: etcd（メタデータ）+ MinIO/S3（オブジェクトストレージ）+ Kafka or Pulsar（v2.5以前）or Woodpecker（v2.6）+ 8マイクロサービスコンポーネント
- milvus.yamlの設定パラメータは500以上あり、適切なチューニングには深い知識が必要
- クラスタデプロイには120以上のパラメータ設定が必要（Kubernetesも必須）
- 「Standaloneモードは本番ではなくテスト用」という認識が広まっており、小規模チームには過剰

### 4-2. 急峻な学習曲線

- 分散セットアップ・インデックス選択・パフォーマンスチューニングへの習熟に数ヶ月かかるという利用者レビューあり
- gRPC中心のAPIのため、REST APIに慣れた開発者には敷居が高い
- Kubernetes未経験チームには「数週間〜数ヶ月の学習コスト」と指摘されている

### 4-3. 単一クエリレイテンシ

- f22labsの比較テストでは単一クエリ応答時間が250msと、Qdrant（低レイテンシが得意）より大幅に遅い
- tensorblue.comのp99比較ではMilvus 5ms対Qdrant 2ms
- 大規模・高スループットで真価を発揮する一方、低レイテンシが求められるシングルクエリ用途では必ずしも最適ではない

### 4-4. リソース要件の高さ

- 本番構成では相応のインフラコストが発生。「スタンドアロン版は本番向けでない」というコミュニティ認識
- etcd・MinIOなどの追加インフラが必要でトータルの運用コストが上がる
- GPUによる最大性能を引き出すにはGPUノードが追加コストとなる

### 4-5. バージョン互換性と運用上の罠

- milvus-backup・helm chart・milvus-operatorでバージョンの不一致が問題になる事例が多報告
- GitHubイシューに「Woodpeckerを使ったクラスタモードでのupsertタイムアウト」「外部S3との接続問題」などの既知バグが存在（2025年時点）
- アップグレード時に試行錯誤が必要との報告

### 4-6. 推薦API の欠如

- Qdrant専用の`recommend` APIのような、positive/negativeサンプルを指定したアイテムベースレコメンドエンドポイントは存在しない
- レコメンドは汎用kNN検索で実現する必要があり、アプリケーション側での実装が必要

---

## 5. ベンチマーク・競合比較・その他

### 5-1. パフォーマンスベンチマーク

**inductivee.com ベンチマーク（2025年、100Mベクトル・768次元）**

| 指標 | 値 |
|---|---|
| 挿入スループット | 38,500 vectors/秒 |
| p50レイテンシ | 4.1ms |
| p99レイテンシ | 24.7ms |
| フィルタ付きRecall@10 | 0.94 |
| セルフホスト月額コスト（EC2）| 約$310 |

スケール別p99レイテンシ:
- 10Mベクトル: 7.8ms
- 100Mベクトル: 24.7ms
- 500Mベクトル: 61.8ms（Qdrant 47.2ms、Weaviate 89.4ms）

**tensorblue.com比較（2025年）**

| 製品 | p99レイテンシ | スループットQPS |
|---|---|---|
| Qdrant | 2ms | 12,000 |
| Milvus | 5ms | 8,000 |
| Pinecone | 8ms | 5,000 |
| Weaviate | 10ms | 4,000 |

**f22labs QdrantとMilvusの比較**

| 指標 | Milvus | Qdrant |
|---|---|---|
| データ取り込み時間 | 12.02秒 | 41.27秒 |
| スループット（QPS） | 46.33 QPS | 4.70 QPS |
| インデックス構築 | 0.60秒 | - |
| 単一クエリレイテンシ | 250ms | 低い |

**IVF_RABITQ ベンチマーク（Milvus公式・v2.6）**

- IVF_RABITQ（SQ8クエリ + SQ8リファイン）: Recall 94.7%、864 QPS（IVF_FLATの3.6倍以上）
- メモリ使用量: IVF_FLATの1/4

**GPU CAGRA（Zilliz公式）**

- CPU HNSWと比較して最大50倍の検索速度向上（公称、ハードウェア・データセット依存）

### 5-2. 競合比較での位置づけ

| 比較軸 | Milvus | Qdrant | Pinecone | Weaviate |
|---|---|---|---|---|
| 適正規模 | 億〜十億単位 | 百万〜数億 | 百万〜数千万 | 百万〜数千万 |
| 運用負荷 | 高（K8s必須） | 中 | 低（フルマネージド）| 中 |
| OSS | Apache 2.0 | Apache 2.0 | なし | BSD-3 |
| 取り込みスループット | 最高クラス | 中 | 中 | 中 |
| 低レイテンシ | 中（5ms p99） | 高（2ms p99）| 中（8ms p99） | 低（10ms p99） |
| GPU対応 | あり（CAGRA） | なし（OSS） | なし | なし |
| BM25ハイブリッド | あり（v2.5〜） | あり | あり | あり |
| 推薦API | なし（汎用kNN）| あり | なし | 一部あり |
| 価格（100Mベクトル）| $310/月（AWS自己ホスト）| $100〜250/月 | $200〜400/月 | $150〜300/月 |

### 5-3. 価格情報

**OSS版（セルフホスト）**: Apache 2.0で無料。インフラ・運用コストのみ

**Zilliz Cloud（マネージドサービス）**

| プラン | 価格 | 特徴 |
|---|---|---|
| 無料 | $0/月 | 5GB・250万vCU・コレクション5個（開発用） |
| サーバーレス | $4/百万vCU | 自動スケーリング・従量課金、コレクション100個まで |
| Dedicated | $99〜/月（開始価格）| 専有環境・本番向け・高度な監視ツール |
| Business Critical | 要問い合わせ | 99.95% SLA・SOC2 Type II・ISO 27001・HIPAA対応 |

**2025年10月の価格変更**:
- コンピュートコスト25%削減
- ストレージコスト87%削減（$0.30 → $0.04/GB/月）
- 10TBデータセットの月額ストレージコスト: $3,000 → $400

**AWS Marketplaceでも提供**（従量課金）

### 5-4. 最新動向（2025〜2026）

- **Milvus v2.6.0 (2025年6月)**: RaBitQ量子化・Woodpecker WAL・Streaming Node・多言語BM25・フレーズマッチ・MinHash LSH・スキーマ進化・INT8ベクトル対応
- **Milvus v2.6.15 (2026年4月)**: 最新の安定版（2026年4月時点）
- **Zilliz Cloud CMEK (2026年3月)**: 顧客管理暗号化キーのGA対応
- **GitHubスター40,000突破 (2025年12月)**: 年間で最大の成長スパート

---

## 6. 参考URL

- [Milvus公式サイト](https://milvus.io/)
- [Zilliz Cloud公式サイト](https://zilliz.com/)
- [MilvusドキュメントトップP](https://milvus.io/docs)
- [Milvus GitHub](https://github.com/milvus-io/milvus)
- [Zilliz Cloud料金ページ](https://zilliz.com/pricing)
- [Milvus インデックス説明ページ](https://milvus.io/docs/index-explained.md)
- [Milvus スパースベクトルドキュメント](https://milvus.io/docs/sparse_vector.md)
- [Milvus フルテキスト検索ドキュメント](https://milvus.io/docs/full-text-search.md)
- [Milvus マルチベクトルハイブリッド検索](https://milvus.io/docs/multi-vector-search.md)
- [Milvus リランカーOverview](https://milvus.io/docs/rerankers-overview.md)
- [Milvus Cross-Encoderリランカー](https://milvus.io/docs/rerankers-cross-encoder.md)
- [Milvus アーキテクチャOverview](https://milvus.io/docs/architecture_overview.md)
- [Milvus マルチテナンシー実装](https://milvus.io/docs/multi_tenancy.md)
- [Milvus バックアップOverview](https://milvus.io/docs/milvus_backup_overview.md)
- [Milvus GPUインデックス](https://milvus.io/docs/gpu_index.md)
- [VectorDBBench（Zilliz製ベンチマークツール）](https://github.com/zilliztech/VectorDBBench)
- [Milvus 2.6 リリースノート（GlobeNewswire）](https://www.globenewswire.com/news-release/2025/06/12/3098386/0/en/Milvus-2-6-Built-for-Scale-Designed-to-Reduce-Costs.html)
- [RaBitQ量子化の詳細ブログ](https://milvus.io/blog/bring-vector-compression-to-the-extreme-how-milvus-serves-3%C3%97-more-queries-with-rabitq.md)
- [Zilliz Cloud エンタープライズセキュリティ発表（PRNewswire）](https://www.prnewswire.com/news-releases/zilliz-powers-the-next-wave-of-ai-adoption-with-unmatched-enterprise-security-and-compliance-302527126.html)
- [Zilliz Cloud CMEKリリース](https://hitechnectar.com/news-post/zilliz-cloud-launches-customer-managed-encryption-keys/)
- [ColPali + Milvus マルチモーダルRAG（Hugging Face）](https://huggingface.co/blog/saumitras/colpali-milvus-multimodal-rag)
- [Milvus 40,000スター達成（PRNewswire）](https://www.prnewswire.com/news-releases/milvus-surpasses-40-000-github-stars-reinforcing-leadership-in-open-source-vector-databases-302646510.html)
- [Milvus vs Pinecone vs Qdrant vs Weaviate比較2025（tensorblue）](https://tensorblue.com/blog/vector-database-comparison-pinecone-weaviate-qdrant-milvus-2025)
- [Qdrant vs Milvus 比較（f22labs）](https://www.f22labs.com/blogs/qdrant-vs-milvus-which-vector-database-should-you-choose/)
- [Milvus 価格ガイド（Airbyte）](https://airbyte.com/data-engineering-resources/milvus-database-pricing)
- [Milvus ユーザーが2024年に教えてくれたこと（公式ブログ）](https://milvus.io/blog/what-milvus-taught-us-in-2024.md)
- [Milvus GitHub Stars達成（Yahoo Finance）](https://finance.yahoo.com/news/milvus-surpasses-40-000-github-010000562.html)
- [Milvus ベンチマーク2025（inductivee）](https://inductivee.com/blog/vector-database-performance-benchmarks-2025)

---

## 付録: まとめ表

| 項目 | 値 |
|---|---|
| 提供元 / ライセンス | Zilliz / Apache 2.0 (OSS)、Zilliz Cloud (マネージド) |
| 位置付け | 専用ベクトルDB（クラウドネイティブ分散型）。超大規模向けデファクトOSS |
| 直近バージョン | v2.6.15（2026年4月17日）|
| 対応インデックス種類 | FLAT / IVF_FLAT / IVF_SQ8 / IVF_PQ / HNSW / DiskANN / SCANN / IVF_RABITQ / GPU_IVF_FLAT / GPU_IVF_PQ / GPU_CAGRA（10種類以上）|
| 最大次元数 | float32: 32,768次元（FLAT/HNSW)、float16/int8も対応。DiskANNなどインデックスにより制限が変わる |
| 量子化対応 (SQ / PQ / Binary / RaBitQ等) | SQ8 / PQ（IVF_PQ）/ バイナリ量子化あり / RaBitQ 1bit（v2.6新規）/ CAGRA-Q（GPU） |
| シャーディング / レプリケーション | ハッシュベースシャーディング（自動）/ Raftベースレプリケーション。ノード追加時に自動リバランス |
| コンピュート/ストレージ分離 | あり（完全分離アーキテクチャ。ストレージはS3/MinIO、コンピュートはステートレスノード） |
| 公称最大データ規模 | 数十億ベクトル（本番事例あり） |
| 公式ベンチマーク (QPS / Recall) | IVF_RABITQ: 864 QPS @ Recall 94.7%（IVF_FLATの3.6倍スループット、メモリ1/4）|
| フィルタ付き検索 | あり（Pre-filter方式 + ACORNアルゴリズムでHNSWグラフのフィルタ耐性強化） |
| ハイブリッド検索 (BM25+Vector) | あり（v2.5〜）。BM25 + Dense + Sparseの3方向並列検索 + RRFフュージョン |
| SPLADE / 学習型スパース対応 | スパースベクトルフィールドとして格納可能（外部でのSPLADE推論が必要。DB内推論は非対応）|
| Late Interaction (ColBERT等) 対応 | ネイティブ対応なし。汎用マルチベクトル格納（doc_id + seq_idスキーマ）+ アプリケーション側MaxSimでColPali/ColBERT実装可能 |
| Cross-Encoder リランカー対応 | あり（pymilvus.model.reranker.CrossEncoderRerankFunction。SDK側処理、DB内推論は非対応）|
| リコメンド API / 機能 | 専用推薦APIなし。汎用kNN検索でレコメンドを実装する形 |
| 提供形態 (OSS / Managed / Enterprise) | OSS（Apache 2.0）/ Zilliz Cloud Serverless / Dedicated / Business Critical |
| SLA / コンプライアンス | Business Critical: 99.95% SLA / SOC2 Type II / ISO 27001 / GDPR / HIPAA対応 / CMEK対応 |
| 価格モデル | OSS無料 / Zilliz Cloud: Serverless $4/M vCU、Dedicated $99〜/月 |
| デプロイ手段 | Docker / Helm Chart / Milvus Operator（Kubernetes）/ Zilliz Cloud（ワンクリック） |
| マルチテナンシー | DB単位（最大64テナント）/ Collection単位（最大65,536）/ Partition単位（最大1,024）。RBAC対応（Collection単位）|
| 可観測性 | Prometheus + Grafana / Milvus WebUI（組み込みGUI）/ OpenTelemetry連携 |
| バックアップ / リストア | milvus-backup（CLI / API / gRPC）でスナップショット。RBAC設定含むバックアップも対応。Zilliz CloudはクロスリージョンバックアップをBC Planで提供 |
| 特徴的な機能 | RaBitQ 1bit量子化（v2.6）/ GPU CAGRA加速 / Woodpecker WAL / 多言語BM25 / MinHash LSH重複排除 / スキーマオンライン進化 / INT8ベクトル対応 |
