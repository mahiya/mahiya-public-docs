# Vald 市場調査レポート

**製品/サービス**: Vald（OSSのみ、マネージドサービスなし）
**開発元/提供元**: vdaas（LY Corporation / 旧Yahoo! JAPAN）
**公式URL**: https://vald.vdaas.org/
**ライセンス**: Apache-2.0
**調査時点**: 2026-04

---

## 1. 市場ポジション

### 概要
Valdは、Yahoo! JAPANが2019年に社内プロジェクトとして開発を開始し、後にOSSとして公開した分散型高速ANN（近似最近傍探索）ベクトル検索エンジンである。クラウドネイティブ設計（Kubernetes前提）が特徴で、「数十億規模のベクトルデータを水平スケールで検索する」用途に特化している。

### 市場シェア・コミュニティ規模
- **DB-Engines ランキング**: Vector DBMS部門 **19位**（総合スコア 0.24）
- **GitHub Stars**: 約 **1,700**（2025年時点）。Milvus（40,000+）、Qdrant（22,000+）、Weaviate（11,000+）と比較して大幅に少ない
- **フォーク数**: 約92
- **開発体制**: 専任OSS開発チーム6名 + 運用チーム5名（LY Corporation内）
- マネージドサービス（DBaaS）は提供なし。LY Corporation内部では「Managed Vald」としてプライベートクラウド上のPaaSとして運用

### 採用事例
| 組織 | ユースケース |
|---|---|
| **LY Corporation（旧LINE/Yahoo! JAPAN）** | 類似画像検索、広告配信、レコメンデーション等 **28以上の社内重要サービス**に本番導入。8,000 QPS を達成し、**40以上のサービス**を支援 |
| **国立国会図書館 JAPAN SEARCH** | 数百万枚規模の文化財・歴史資料のサムネイル画像類似検索（AWS EKS上のVald v1.1.2を利用） |
| **採用マッチングサービス（LY Corp系）** | CodeBERTでベクトル化したソースコードを用いたエンジニアと企業のマッチング |

- Vald採用はSoftBankグループ全体への展開も進んでいると報告されている
- 一方で、Yahoo! JAPAN / LY Corporation以外の外部企業による公開事例は非常に限定的であり、**特定の組織（LY Corporation系列）への採用が極端に集中**している点が市場ポジション上の特徴

### 競合との関係
- **Milvus / Zilliz Cloud**：大規模分散ベクトル検索では直接競合するが、Milvusは豊富な機能・大きなコミュニティ・マネージドサービスを有しており、市場プレゼンスで大きく差が開いている
- **Qdrant**：高性能フィルタ付き検索・ハイブリッド検索を重視するQdrantに対し、ValdはKubernetes分散スケールと運用自動化を強みとする異なるアプローチ
- **Weaviate / Elasticsearch**：ハイブリッド検索・RAGユースケースへの対応が手薄なため、RAG用途では比較対象になりにくい

---

## 2. 開発元のアピールポイント

### 公式が主張する主な差別化ポイント

**1. クラウドネイティブ・Kubernetes-Nativeアーキテクチャ**
- Kubernetesのオーケストレーション機能（水平スケーリング、自動復旧、ローリングアップデート）をフルに活用
- Helmチャートおよびvald-helm-operatorによる宣言的デプロイ
- Kubernetesクラスタのサイズがスケーラビリティの上限となる設計

**2. 分散インデックス（Distributed Indexing）**
- ベクトルデータとインデックスを複数のVald Agentに分散配置
- 全Agentが並列処理することでスループットを向上
- `index_replica`設定により複数Agentに同一インデックスのレプリカを保持し、耐障害性を確保

**3. 非同期自動インデックシング（Asynchronous Auto-Indexing）**
- インデックス構築中でも検索処理を継続可能（インデックス生成中のロック不要）
- ※ただし、Agent NGT はインデックス作成中のポッドへの検索リクエストを無視するという記述もあり、厳密な挙動は設定依存

**4. 自動バックアップ・自動リバランス**
- Agentダウン時にレプリカを自動的にリバランス
- バックアップ先: AWS S3 / GCS（S3互換）または Kubernetes PersistentVolume

**5. カスタマイズ可能なフィルタリング（Ingress / Egress Filter）**
- Ingress Filter: クエリベクトルの前処理（オブジェクト→ベクトル変換、ベクトルパディング等）
- Egress Filter: 検索結果の後処理（距離でのフィルタリング、カテゴリ除外等）
- ONNX / TensorFlow対応の公式フィルターコンポーネントを提供

**6. Read Replicaによるクエリスループット向上**
- 読み取り専用レプリカを追加デプロイすることで、レプリカ数N倍に対して約1.7〜1.8×N倍のQPS向上を実現
- HPA（Horizontal Pod Autoscaler）との組み合わせで自動スケール

**7. 多言語SDKとgRPC API**
- Go、Java、Python、Node.js、ClojureのSDKを公式提供
- LangChainとの統合（類似度検索、スコア付き検索、MMR検索対応）
- TLS暗号化・Athenz認証によるセキュアな接続

**8. NGTアルゴリズムによる高性能ANN検索**
- 最速クラスのANNアルゴリズム「NGT（Neighborhood Graph and Tree）」をデフォルト採用
- 別途Faissバックエンドへの切り替えも可能

---

## 3. 市場・調査会社が評価している強み

### サードパーティによる評価

**スケーラビリティとKubernetes親和性**
- 「Kubernetes-nativeアプローチにより、クラウドインフラを使用する組織に適している」（Nordic APIs）
- 分散インデックス、自動ヒーリング、動的スケーリングを備えた唯一無二のKubernetes-first設計として評価される

**NGTアルゴリズムの性能**
- ann-benchmarks.comにおいて、NGTのONNGバリアントが「世界最高水準の性能」を達成した時期がある
- NGT-QG（グラフベースインデックス + Product Quantizationの融合）は、ScaNN、HNSW、Annoyとの比較で多くのデータセットにおいて競争力のある性能を示す
- NGT-QGはann-benchmarksで95% Recall時に12データセット中2データセットで最高速度を達成

**運用自動化**
- 自己管理型のレプリカ自動リバランスにより、オペレーターの手動介入を削減
- 破損インデックスのバックアップ保持機能（`broken_index_history_limit`設定）

**可観測性スタックの充実**
- v1.6.0よりOpenTelemetryへ移行（v1.7.0で完全統合）
- Prometheus（メトリクス）、Jaeger（分散トレーシング）、Grafana（ダッシュボード、自動生成機能あり）を標準サポート
- Circuit Breaker機能（v1.6.0〜）によるマイクロサービス間の障害伝播を防止

**リアルタイムインデックス更新**
- ライブ推薦エンジンやIoTデータ処理など、検索を止めずにインデックスを更新できる用途に優れる

**実績に裏付けられた大規模運用**
- LY Corporation（旧Yahoo! Japan、LINE）での本番運用実績（8,000 QPS、28+サービス）は、大規模分散運用の実証データとして評価されている

---

## 4. 市場・調査会社が指摘している弱点・批判点

### コミュニティ規模と市場認知度の低さ
- GitHubスター数約1,700は、主要競合（Milvus: 40,000+、Qdrant: 22,000+、Weaviate: 11,000+）の数十分の一
- DB-Enginesランキングでベクトルデータベース部門19位（上位プレーヤーとの格差は大きい）
- RAGパイプライン向けの代表的な比較記事（ZenML、LiquidMetal AIなど）でValdが取り上げられない事例が多い
- 「RAGやGenAI用途の標準的な選択肢」として認知されていない

### マネージドサービス（DBaaS）が存在しない
- PineconeやZilliz Cloud、Qdrant Cloudのようなフルマネージドサービスがなく、セルフホスト運用のみ
- Kubernetesクラスタの調達・管理・監視をすべて利用者が担う必要がある
- 「インフラコストより運用オーバーヘッドの方が問題になりえる」と指摘される

### Kubernetes専用設計による参入障壁
- **Kubernetesなしでのデプロイは非対応**（Docker単体でのAgent Standaloneモードは存在するが、本番分散構成はKubernetes必須）
- Kubernetesの知識・インフラが前提となるため、中小チームやスタートアップには導入コストが高い
- 「急峻な学習曲線がある」との評価（Nordic APIs）

### gRPC専用API（REST非対応）
- gRPCプロトコルのみサポート。REST APIに慣れた開発者には追加の学習・対応コストが生じる
- 一方、Qdrant、Milvusなどは REST + gRPC の両対応を提供している

### スパースベクトル・ハイブリッド検索のネイティブ非対応
- Valdは**dense vectorに特化**しており、スパースベクトル（BM25、SPLADE等）のネイティブサポートがない
- RAGユースケースで重要なハイブリッド検索（dense + sparse）機能を持たない
- GitHub Issue #1180でスパースベクトルサポートのリクエストがあったが、実装には至っていない
- 「Sparse vectorを扱えるが、最大性能はdense vectorで発揮する」との公式見解があるものの、実用レベルの機能として整備されていない

### メタデータフィルタリングの方式
- メタデータフィルタリングは、ネイティブのインデックス統合型（filter-aware index）ではなく、**外部フィルターコンポーネント（Egress Filter）による後処理**ベース
- Qdrantの単一ステージフィルタ付きANNや、Milvusのハイブリッドフィルタと比べると、複雑なメタデータフィルタリングのパフォーマンスは不利になりやすい

### エンタープライズ向けセキュリティ・コンプライアンス機能の限定
- TLS暗号化とトークンベース認証（Athenz）は提供されているが、SOC 2、ISO 27001、HIPAAなどの第三者認証は公式に確認されていない
- RBAC（ロールベースアクセス制御）やマルチテナント分離など、エンタープライズ向けセキュリティ機能の明示的な仕様がドキュメント上で限定的

### 学習型スパース・Late Interaction・リランキングの非対応
- SPLADE、ColBERT、ColPaliなどの学習型検索手法は非対応
- Cross-Encoderリランカーの内蔵機能もなし
- これらを必要とする高精度RAGユースケースでは、外部コンポーネントで補完する必要がある

### 採用事例の集中
- 公開されている本番採用事例が実質的にLY Corporation（旧Yahoo! Japan）に集中しており、他の外部企業による検証事例が不足している
- 多様なユースケースへの適用実績がコミュニティに蓄積されていない

---

## 5. ベンチマーク・競合比較・その他

### ann-benchmarks.com でのNGT性能評価
- Valdが使用するNGTは、`vald(NGT-panng)`、`NGT-qg`、`NGT-onng`などの複数バリアントでann-benchmarks.comに登録されている
- **ONNG**（Optimized Nearest Neighbor Graph）バリアントは一時期「世界最高水準の性能」を達成
- **NGT-QG**（Quantized Graph）: グラフベースのインデックス探索 + Product Quantizationの融合により、高Recall時の高速検索を実現。ann-benchmarksで95% Recall時に12データセット中2データセットで最高速度を達成
- 「QGはすべてで最高ではないが、多くの図表で高性能を示す」（NGT開発者・Masajiro Iwasaki）
- 具体的なQPS・Recall数値はann-benchmarks.comの対話型グラフ上で参照可能（静的なスナップショット数値は未公表）

### 分散ベクトルDBとしての位置づけ（2025年の比較研究）
- HPC（高性能計算）プラットフォームでの分散ベクトルDBとして、Vespa、Vald、Weaviate、Milvus、Qdrantが並列評価される文脈がある
- 「GPU加速ANNをサポートする分散ベクトルデータベース」として、Vald、Weaviate、Milvusの3つが挙げられることがある（ただしValdのGPU対応の詳細な公式仕様は確認できず）

### LY Corporation内部ベンチマーク（公開値）
| 指標 | 値 |
|---|---|
| QPS（本番環境） | 8,000 QPS |
| 対応サービス数 | 40以上（LINE Yahoo Corporation内） |
| 本番稼働中の重要サービス | 28以上 |
| データ規模 | 数十億ベクトル（公称） |

※ 上記はLY Corporation内部環境での報告値。ハードウェア構成・次元数・量子化有無などの詳細条件は非公開

### 価格情報
- **OSSのみ提供**: 無償（Apache-2.0）
- マネージドサービス・エンタープライズライセンスは存在しない
- 実質的なコストはKubernetesインフラ費用（クラウド利用料）と運用人件費

### 競合プロダクトとの比較メモ

| 競合 | Valdが優る点 | Valdが劣る点 |
|---|---|---|
| **Milvus** | Kubernetes-native運用自動化、シンプルな設計 | 機能の豊富さ、コミュニティ規模、マネージドサービス、RAG/ハイブリッド検索対応 |
| **Qdrant** | 分散インデックスの自動管理、大規模インフラとの親和性 | フィルタ付きANN性能、スパースベクトル、ハイブリッド検索、REST API、管理UI |
| **Weaviate** | NGTによる純粋な高速ANN性能 | ハイブリッド検索、学習型スパース（SPLADE）、ColBERT、組み込みベクトル化、GraphQL API |
| **pgvector** | 分散スケール、耐障害性、Kubernetes自動化 | PostgreSQL統合、SQLクエリ、エコシステムの広さ、導入の容易さ |

### 最新動向（v1.7系列、2025年）
- **QUICプロトコル対応**（v1.7.15）：低レイテンシ通信の強化
- **インデックスエクスポーター実装**（v1.7.17）：インデックスの外部エクスポート機能
- **Grafanaダッシュボード自動生成**（v1.7.17）：可観測性の向上
- **タイムスタンプ付きインデックス**（v1.7.13）：インデックス管理の精緻化
- **Read Replica & Rotator**（v1.7.9〜）：検索QPSの向上機能
- **OpenTelemetry完全移行**（v1.7.0）：分散トレーシング・メトリクスの標準化

---

## まとめ表

| 項目 | 値 |
|---|---|
| 提供元 / ライセンス | vdaas（LY Corporation） / Apache-2.0 |
| 位置付け | Kubernetes-native 分散ベクトル検索エンジン（専用ベクトルDB） |
| 対応インデックス種類 | NGT（ONNG、PANNG、QG等）、Faiss（IVF-PQ確認済み） |
| 最大次元数 | ドキュメント上の明示なし（設定パラメータとして任意指定、NGTのオブジェクト型: float32 / uint8） |
| 量子化対応 | NGT-QG による Product Quantization（4-bit PQ）、uint8 スカラー量子化（object_type: uint8） |
| シャーディング / レプリケーション | 分散インデックス（Agent間でランダム分散） / index_replica設定によるマルチエージェントレプリカ、自動リバランス |
| コンピュート/ストレージ分離 | 非分離型（Agent内でインデックスをオンメモリ保持、S3/PV バックアップ）。Read Replica でクエリ系を分離可能 |
| 公称最大データ規模 | 数十億ベクトル（LY Corporation本番実績） |
| 公式ベンチマーク (QPS / Recall) | 8,000 QPS（LY Corporation本番環境、詳細条件非公開）。NGT-QGはann-benchmarks 95%Recall時に12件中2件で最速 |
| フィルタ付き検索 | Egress Filter（後処理ポストフィルタ）。ネイティブ統合型フィルタインデックスは非対応 |
| ハイブリッド検索 (BM25+Vector) | 非対応（dense vector専用） |
| SPLADE / 学習型スパース対応 | 非対応 |
| Late Interaction (ColBERT 等) 対応 | 非対応 |
| Cross-Encoder リランカー対応 | 非対応 |
| リコメンド API / 機能 | 専用 Recommend API はなし。SearchById（既存ベクトルIDをクエリに使用）で代替可能 |
| 提供形態 (OSS / Managed / Enterprise) | OSS のみ（Apache-2.0）。マネージドサービスなし |
| SLA / コンプライアンス | 記載なし（LY Corporation 内部では Managed Vald として運用実績あり） |
| 価格モデル | 完全無償（OSS）。インフラ費用・運用コストは利用者負担 |
| デプロイ手段 | Helm チャート、vald-helm-operator（Kubernetes 1.19以上必須）、Docker（Agent Standalone のみ） |
| マルチテナンシー | 明示的な仕様なし（Namespace レベルの分離はKubernetes側で対応） |
| 可観測性 | OpenTelemetry、Prometheus、Jaeger、Grafana（ダッシュボード自動生成）、Circuit Breaker |
| バックアップ / リストア | S3 / GCS（S3互換）または Kubernetes PV。Init ContainerによるS3からの自動復旧 |
| 特徴的な機能 | Kubernetes-native分散ANN、NGT-QG（Graph + PQ融合）、Ingress/Egressカスタムフィルター、Read Replica、QUIC対応 |
| DB-Engines ランキング | ベクトルDB部門 19位（スコア 0.24） |
| GitHub Stars（2025年時点） | 約 1,700 |

---

## 6. 参考URL

### 公式ドキュメント・リポジトリ
- [Vald 公式サイト](https://vald.vdaas.org/)
- [About Vald](https://vald.vdaas.org/docs/overview/about-vald/)
- [Vald Architecture](https://vald.vdaas.org/docs/overview/architecture/)
- [Vald Configuration Guide](https://vald.vdaas.org/docs/user-guides/configuration/)
- [Vald Filtering Configuration](https://vald.vdaas.org/docs/user-guides/filtering-configuration/)
- [Vald Filter Gateway Component](https://vald.vdaas.org/docs/overview/component/filter-gateway/)
- [Vald Search Config](https://vald.vdaas.org/docs/user-guides/search-config/)
- [Vald Backup Configuration](https://vald.vdaas.org/docs/user-guides/backup-configuration/)
- [Vald Read Replica and Rotator](https://vald.vdaas.org/docs/user-guides/read-replica-and-rotator/)
- [Vald Faiss Agent Tutorial](https://vald.vdaas.org/docs/tutorial/get-started-with-faiss-agent/)
- [Vald Observability Configuration](https://vald.vdaas.org/docs/user-guides/observability-configuration/)
- [Vald Changelog](https://vald.vdaas.org/docs/release/changelog/)
- [GitHub: vdaas/vald](https://github.com/vdaas/vald)
- [GitHub: yahoojapan/NGT](https://github.com/yahoojapan/NGT)

### 採用事例・プレゼンテーション
- [Tech-Verse 2022: Vald Introduction and Case Studies](https://tech-verse.me/en/sessions/172)
- [Speaker Deck: Vald OSS ANN Search Engine Case Studies](https://speakerdeck.com/techverse_2022/vald-oss-ann-nearest-neighbor-dense-vector-search-engine-introduction-and-case-studies)
- [Medium: Case Study - JAPAN SEARCH with Vald](https://vdaas-vald.medium.com/case-study-the-story-of-japan-search-with-vald-69ec0f3c3fc9)
- [Medium: Vald v1.6.0 Release Announcement](https://vdaas-vald.medium.com/release-announcement-vald-v1-6-0-6c9d2aa83a1e)
- [Medium: Vald Overview (Geek Culture)](https://medium.com/geekculture/vald-a-highly-scalable-distributed-fast-approximate-nearest-neighbour-dense-vector-search-engine-af1946a4a37)

### 技術記事・NGTベンチマーク
- [Medium: NGT-QG - Fusion of Graph-Based Indexing and Product Quantization](https://medium.com/@masajiro.iwasaki/fusion-of-graph-based-indexing-and-product-quantization-for-ann-search-7d1f0336d0d0)
- [ann-benchmarks.com: vald(NGT-panng) Results](http://ann-benchmarks.com/vald(NGT-panng).html)
- [ann-benchmarks.com Top Page](http://ann-benchmarks.com/)

### サードパーティ評価・比較記事
- [Nordic APIs: Comparing 10 Vector Database APIs for AI](https://nordicapis.com/comparing-10-vector-database-apis-for-ai/)
- [MarkTechPost: Meet Vald (2024)](https://www.marktechpost.com/2024/01/04/meet-vald-an-open-sourced-highly-scalable-distributed-vector-search-engine/)
- [LakeFS: Best 17 Vector Databases](https://lakefs.io/blog/best-vector-databases/)
- [DB-Engines: Vald System Properties](https://db-engines.com/en/system/Vald)
- [Zilliz: Qdrant vs Vald Comparison](https://zilliz.com/blog/qdrant-vs-vald-a-comprehensive-vector-database-comparison)
- [Zilliz: OpenSearch vs Vald Comparison](https://zilliz.com/blog/opensearch-vs-vald-comprehensive-vector-database-comparison)
- [Zilliz: Zilliz Cloud vs Vald Comparison](https://zilliz.com/blog/zilliz-cloud-vs-vald-a-comprehensive-vector-database-comparison)
- [GitHub Issue #1180: Sparse Vector Support Request](https://github.com/vdaas/vald/issues/1180)
- [LangChain: Vald Vector Store Integration](https://docs.langchain.com/oss/python/integrations/vectorstores/vald)
- [Fortune Business Insights: Vector Database Market Report](https://www.fortunebusinessinsights.com/vector-database-market-112428)
