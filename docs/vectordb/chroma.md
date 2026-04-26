# Chroma 市場調査レポート

**製品/サービス**: Chroma (ChromaDB) — OSS (Apache 2.0) / Chroma Cloud (Managed Serverless) / BYOC
**開発元/提供元**: Chroma, Inc.（共同創業者: Jeff Huber, Anton Troynikov、本社: サンフランシスコ）
**公式URL**: https://www.trychroma.com/ / https://docs.trychroma.com/
**ライセンス**: Apache License 2.0
**調査時点**: 2026-04

---

## 1. 市場ポジション

### 位置づけ

Chromaは「AI向けオープンソース検索インフラ」として自らを定義し、RAG（Retrieval-Augmented Generation）システムや LLM アプリケーション向けのベクトルデータベースとして広く採用されている。特に**開発者体験（DX）と高速プロトタイピング**を最大の強みとし、SQLite 的な組み込み（embedded）動作で「ゼロコンフィグ・ゼロネットワークレイテンシ」を実現する点が特徴。

### 採用状況・規模

- **GitHubスター数**: 約 27,600（2026年4月時点）。オープンソースベクトルDB市場では Milvus（~25k）と拮抗し上位に位置する
- **月次ダウンロード数**: 約 1,100〜1,500万回（PyPI）。Pythonエコシステムでの認知度は非常に高い
- **他リポジトリからの利用**: 90,000以上のオープンソースリポジトリで採用
- **LangChain連携**: LangChainユーザーの約40%がChromaDBを統合しているとされる
- **商用実績**: Capital One、Weights & Biases、UnitedHealthcare、Live Nation、Cisco、Intel、Sony等が公式に掲載されているユーザー企業

### 競合との関係

| 競合製品 | 市場セグメント | Chromaとの関係 |
|---|---|---|
| Pinecone | フルマネージド商用 | 企業向け本番環境。Chromaよりも高価だが SLA・スケールは優位 |
| Qdrant | OSS+商用クラウド | 本番向けOSS。高度フィルタリング・分散構成でChromaを上回る |
| Weaviate | OSS+商用クラウド | GraphQL・マルチモーダル強化。エンタープライズ寄り |
| Milvus/Zilliz | OSS+クラウド | 大規模ベクトル検索。Chromaより高機能だが運用複雑度が高い |
| pgvector | PostgreSQL拡張 | 既存DB統合を重視するユーザー向け |

Chromaは「プロトタイプ〜数百万ベクトル規模のMVP」として支持されており、スケールアウトが必要になった段階で Qdrant・Pinecone・Milvus へ移行するケースが多いと複数のサードパーティ分析で指摘されている。

### 資金調達・企業背景

- 2022年5月: プレシード（AIX Ventures、Bloomberg Beta、AI Grant主導）
- 2023年4月: シード $18M（Quiet Capital主導。Naval Ravikant、Max/Jack Altman、Jordan Tigani、Guillermo Rauch等の著名エンジェルが参加）
- 2025年8月: **Chroma Cloud が一般提供（GA）開始**

---

## 2. 開発元のアピールポイント

### コアバリュープロポジション（公式サイト・ドキュメントより）

1. **10倍のコスト効率**: オブジェクトストレージ（S3/GCS）を基盤とするインテリジェントティアリングアーキテクチャにより、従来のインメモリ重視DBと比較して大幅にコスト削減
2. **ゼロ運用負荷**: 「No engineering ops」—サーバーレス、自動スケール、手動チューニング不要
3. **統合検索インターフェース**: ベクトル検索・BM25・SPLADE・全文検索・正規表現・メタデータフィルタリングを単一 API で統合

### 主な技術的差別化ポイント

- **組み込み（Embedded）動作**: Pythonプロセス内で動作し、ゼロネットワークレイテンシを実現。開発環境では `pip install chromadb` だけで即起動
- **マルチランゲージネイティブサポート**: v1.0 Rustコアにより Python、JavaScript、TypeScript、Ruby、Swift、WebAssembly（ブラウザ）をファーストクラスサポート
- **4倍高速化（v1.0, 2025年）**: Python GILのボトルネックを排除した Rust コアにより、書き込み・クエリとも 3〜5倍高速化。真のマルチスレッド処理を実現
- **ハイブリッド検索（RRF）**: dense ベクトル + sparse（BM25/SPLADE）を Reciprocal Rank Fusion で統合
- **データセットバージョニング・フォーク**: コレクションのコピーオンライト高速複製、A/Bテスト、ロールアウト機能
- **マルチモーダル対応**: OpenCLIP組み込みにより画像・テキストの cross-modal 検索をサポート

### Chroma Cloud のアピールポイント

- サーバーレス・自動スケール（課金は使用量ベース）
- オブジェクトストレージ $0.02/GB/月 vs インメモリDBのコスト差
- BYOC（VPC内デプロイ）・マルチリージョンレプリケーション・ポイントインタイムリカバリ（PITR）
- SOC 2 準拠（Team プラン以上）
- p50 クエリレイテンシ 20ms（ウォーム）、p99 57ms（384次元、100kベクトル時）

---

## 3. 市場・調査会社が評価している強み

### 開発者体験の卓越性

多数のサードパーティ比較記事（DataCamp、Firecrawl、AltexSoft等）が共通して評価するのは、**学習コストの低さと即座に動く体験**。「NumPy ライクなAPI」「インストールから5分で動作」「設定ゼロ」といった表現が繰り返し登場する。LangChain・LlamaIndex等の主要RAGフレームワークとの統合がファーストクラスで提供される点も評価が高い。

### 2025年 Rust コアリライトによる性能向上

v1.0（2025年初頭リリース）でのRustコアへの移行は、独立した複数のブログ・テック記事でポジティブに評価されている:
- 書き込み・クエリとも 3〜5倍高速化
- 真のマルチスレッド（Python GIL排除）
- Apache Arrow フォーマットによる効率的なディスク永続化
- 2025年8月の追加最適化（base64ベクトルエンコード）でスループットをさらに70%向上

### コスト効率

自己ホスト（VPS、4GB RAM）で月額$30未満の運用が可能であり、RAGシステムの数百万チャンク規模に対して十分なコストパフォーマンスを持つと複数の技術ブログが評価している。

### 多様な検索モダリティの統合

- dense + sparse ハイブリッド（RRF）
- BM25 および SPLADE（学習型スパース）ネイティブ対応
- 全文検索（trigram、regex）
- メタデータフィルタリング
これらを単一コレクション・単一APIで扱える点は、別途検索エンジンを立てる必要がなくなるとして評価される。

### オープンソースコミュニティとの連携

Apache 2.0 ライセンスでベンダーロックインがなく、90,000以上のOSSリポジトリで使用されており、エコシステムの広がりが認められている。

---

## 4. 市場・調査会社が指摘している弱点・批判点

### スケーラビリティの限界

- **シングルノードアーキテクチャ**: OSS版は基本的に単一ノード動作。分散モードは実験的（experimental）な位置づけにとどまる
- **実用限界は〜10〜15Mベクトル**: 高スペックサーバー（64GB RAM）で最大約1,500万エンベディングとされ、大規模なプロダクションには不向き
- **高同時実行時の性能劣化**: 単一クエリでは高速だが、100クエリ同時実行テストで QPS が 112 まで低下するケースが報告されており、pgvector・Pinecone に比べて同時実行性能が劣る
- **10M件超のデータ**: 複数の比較記事が「10M ベクトルを超えたら Qdrant/Pinecone/Milvus への移行を推奨」と明示

### セキュリティ上の重大な懸念

- **デフォルト認証なし**: ChromaDB はデフォルトで認証を要求しない。手動で有効化が必要
- **実際の被害事例**: 2025年4月の調査（UpGuard）で、インターネット上に公開された 1,170のChromaDBインスタンスのうち406件がデータを漏洩。個人情報（Canva Creators情報等）が含まれる事例も確認
- **データポイズニングリスク**: 認証なしに外部からコレクションに書き込みが可能であることから、RAGシステムのデータ汚染攻撃が可能

### インデックス管理の問題

- **HNSWインデックスが縮小しない**: ドキュメントを削除してもHNSWインデックスのメモリ使用量は削減されない。5,000件追加→4,000件削除後もインデックスは5,000件分のメモリを保持。新コレクション作成によるフルリビルドが唯一の解決策
- **チューニングオプションの制限**: HNSW の `ef_construction`、`ef_search`、`M` のみが設定可能で、競合（Milvus等）に比べて細かいチューニング自由度が低い

### エンタープライズ機能の不足

- RBAC（ロールベースアクセス制御）の欠如（OSS版）
- 監査ログの未整備
- Azure など一部クラウドプラットフォームでネイティブサポートなし（Dockerコンテナ化と独自スケーリングが必要）
- バックアップ・リストアのネイティブ機能が弱く、APIエクスポート・ファイルシステムスナップショット等の手動対応が必要（PITR は Chroma Cloud のみ）

### ドキュメント・統合例の不足

- 複数のリソースが「実世界のデプロイシナリオや統合パターンに関するドキュメントが薄い」と指摘
- エラー処理・モニタリング・運用ノウハウに関する公式情報が限定的

---

## 5. ベンチマーク・競合比較・その他

### 公式パフォーマンスデータ（Chroma 公式ドキュメントより）

| 指標 | 値 | 条件 |
|---|---|---|
| クエリレイテンシ p50（ウォーム） | 20ms | 384次元、100kベクトル |
| クエリレイテンシ p99（ウォーム） | 57ms | 384次元、100kベクトル |
| クエリレイテンシ p50（コールド） | 650ms | 同上 |
| クエリレイテンシ（一般） | 4〜8ms（mean） | 1024次元、小規模ドキュメント |
| p99.9 レイテンシ | 7〜29ms | ハードウェアによる |
| 書き込みスループット | 30 MB/s | — |
| バッチ挿入レイテンシ | 112〜231ms（batch=32） | — |
| 最大コレクションサイズ | 〜1,500万件 | 64GB RAM |
| 推奨最大 | 〜5M件/コレクション | 公称値 |

※ 公式ベンチマークはハードウェア・データセット・量子化有無の条件が不明確な部分があり、完全な再現性検証は困難。

### 第三者ベンチマーク・比較評価

- **同時実行テスト（LiquidMetal AI 2026）**: 単一クエリではトップクラスの速度を示すが、100並列クエリでは QPS が約112に低下。目的特化型DBに比べて高同時実行での性能差が顕著
- **VectorDBBench（Zilliz）**: Chroma は同ベンチマークに含まれることがあるが、結果の詳細は公開されていない。Milvus や Qdrant を優先評価する傾向がある
- **ANN-Benchmarks**: Chroma は ann-benchmarks.com の公式測定対象外（2026年4月時点）

### 競合比較サマリー

| 比較軸 | Chroma | Qdrant | Pinecone | Weaviate |
|---|---|---|---|---|
| プロトタイプ速度 | ◎ 最速 | ○ | ○ | △ |
| 本番スケール（10M+） | △ 限定的 | ◎ | ◎ | ◎ |
| 同時実行性能 | △ | ◎ | ◎ | ○ |
| フィルタ付きANN | ○ ポストフィルタ | ◎ フィルタ認識HNSW | ◎ | ○ |
| ハイブリッド検索（BM25+dense） | ○ RRF | ◎ | ◎ | ◎ |
| SPLADE対応 | ○ Cloud | ◎ | ◎ | ○ |
| ColBERT/マルチベクトル | 記載なし | ◎ | △ | △ |
| 量子化 | 記載なし（詳細不明） | ◎ 24x圧縮 | △ | △ |
| 分散/水平スケール | △ 実験的 | ◎ | ◎ マネージド | ◎ |
| エンタープライズセキュリティ | △ Cloud のみ | ◎ RBAC/SOC2 | ◎ | ○ |
| 運用コスト（自己ホスト） | ◎ <$30/月 | ○ $30〜50/月 | × $100〜 | △ |
| ライセンス | Apache 2.0 | Apache 2.0 | Proprietary | BSD-3 |

### インデックス・量子化・技術仕様

- **サポートインデックス**: HNSW のみ（OSS）。FLAT（小規模）は内部バッファとして使用
- **最大次元数**: 記載なし（公式ドキュメントに明示的な上限値なし）
- **量子化**: 公式ドキュメントに量子化（SQ/PQ/Binary）のサポートについて明確な記述なし。競合（Qdrant の 24x 圧縮等）と比較して遅れている
- **フィルタ方式**: ポストフィルタ（ANN後にメタデータフィルタ適用）。フィルタ認識型HNSWトラバーサル（Qdrant方式）ではない点に注意
- **SPLADE対応**: Chroma Cloud で `ChromaCloudSpladeEmbeddingFunction` として提供。OSS版でも BM25 は利用可能
- **ColBERT/Late Interaction**: ネイティブサポートなし（マルチベクトルフィールドの概念が存在しない）
- **Cross-Encoderリランカー**: ネイティブ組み込みなし
- **レコメンドAPI**: Qdrant の recommend API に相当する専用エンドポイントなし

### 価格情報（Chroma Cloud）

| プラン | 月額固定費 | 含まれるクレジット | 主な機能 |
|---|---|---|---|
| Starter | $0 | $5 | 10DB、10メンバー、コミュニティSlack |
| Team | $250 | $100 | 100DB、30メンバー、Slackサポート、SOC2 |
| Enterprise | カスタム | — | 専用クラスター、BYOC、SLA保証 |

使用量課金:
- 書き込み: $2.50/GiB
- ストレージ: $0.33/GiB/月
- クエリ: $0.0075/TiB
- ネットワーク: $0.09/GiB（返送分）

典型ワークロード（1M件書込、6M件保存、10Mクエリ）の試算: 約$79/月（Starterプラン）

### 最新動向（2025年）

- **2025年初頭**: Rust コアへの全面リライト（v1.0）。3〜5倍のパフォーマンス向上
- **2025年7月**: 正規表現検索サポート追加（新演算子）
- **2025年8月**: Chroma Cloud GA（一般提供開始）。スパースベクトル検索（BM25/SPLADE）リリース。base64エンコード最適化でスループット70%向上
- **2026年4月**: 最新バージョン v1.5.8。週次リリース（毎週月曜）継続中

---

## 6. 参考URL

### 公式リソース
- [Chroma 公式サイト](https://www.trychroma.com/)
- [Chroma 製品ページ（ChromaDB）](https://www.trychroma.com/products/chromadb)
- [Chroma 公式ドキュメント](https://docs.trychroma.com/)
- [Chroma GitHub リポジトリ](https://github.com/chroma-core/chroma)
- [Chroma 価格ページ](https://www.trychroma.com/pricing)
- [Chroma v1.0 リリースノート（4x高速化）](https://www.trychroma.com/project/1.0.0)
- [Chroma スパースベクトル検索発表](https://www.trychroma.com/project/sparse-vector-search)
- [Chroma パフォーマンスガイド（公式Docs）](https://docs.trychroma.com/guides/deploy/performance)
- [Chroma スパースベクトル検索 Docs](https://docs.trychroma.com/cloud/schema/sparse-vector-search)

### 市場分析・比較記事
- [The Good and Bad of ChromaDB for RAG（AltexSoft）](https://www.altexsoft.com/blog/chroma-pros-and-cons/)
- [Best Vector Databases 2026: Pinecone, Chroma, Qdrant & More（DataCamp）](https://www.datacamp.com/blog/the-top-5-vector-databases)
- [Best Vector Databases in 2025（Firecrawl）](https://www.firecrawl.dev/blog/best-vector-databases)
- [Vector Database Comparison 2026（4xxi）](https://4xxi.com/articles/vector-database-comparison/)
- [ChromaDB vs Qdrant（Airbyte）](https://airbyte.com/data-engineering-resources/chroma-db-vs-qdrant)
- [Vector Database Comparison 2025（LiquidMetal AI）](https://liquidmetal.ai/casesAndBlogs/vector-comparison/)
- [ChromaDB Wikipedia](https://en.wikipedia.org/wiki/Chroma_(vector_database))

### セキュリティ・リスク情報
- [Open Chroma Databases: A New Attack Surface for AI Apps（UpGuard）](https://www.upguard.com/blog/open-chroma-databases-ai-attack-surface)
- [ChromaDB Library Mode = Stale RAG Data（Medium）](https://medium.com/@okekechimaobi/chromadb-library-mode-stale-rag-data-never-use-it-in-production-heres-why-b6881bd63067)

### ベンチマーク関連
- [VectorDBBench（Zilliz/GitHub）](https://github.com/zilliztech/VectorDBBench)
- [Chroma Cookbook（コミュニティ）](https://cookbook.chromadb.dev/)

---

## まとめ表

| 項目 | 値 |
|---|---|
| 提供元 / ライセンス | Chroma, Inc. / Apache 2.0 |
| 位置付け | 組み込み型ベクトルDB（RAG・LLMアプリ向けプロトタイピング〜中規模本番） |
| 対応インデックス種類 | HNSW（単一。内部ブルートフォースバッファ併用） |
| 最大次元数 | 公式記載なし |
| 量子化対応（SQ / PQ / Binary） | 公式ドキュメント記載なし（競合と比較して未成熟） |
| シャーディング / レプリケーション | シングルノードOSS（分散は実験的）/ Chroma Cloud はマルチリージョンレプリケーション |
| コンピュート/ストレージ分離 | Chroma Cloud はオブジェクトストレージ（S3/GCS）ベースの分離アーキテクチャ |
| 公称最大データ規模 | 〜5M件/コレクション（推奨）、〜15M件（64GB RAM最大） |
| 公式ベンチマーク（クエリレイテンシ） | p50: 20ms、p99: 57ms（384次元、100kベクトル、ウォーム） |
| フィルタ付き検索 | ポストフィルタ方式（フィルタ認識型HNSWではない） |
| ハイブリッド検索（BM25+Vector） | 対応（RRF。BM25 + dense ベクトル統合） |
| SPLADE / 学習型スパース対応 | BM25は OSS、SPLADE は Chroma Cloud のみ（ChromaCloudSpladeEmbeddingFunction） |
| Late Interaction（ColBERT等）対応 | 非対応（マルチベクトルフィールド概念なし） |
| Cross-Encoderリランカー対応 | 非対応（組み込みリランカーなし） |
| リコメンドAPI / 機能 | 非対応（専用エンドポイントなし） |
| 提供形態 | OSS（Apache 2.0）/ Chroma Cloud（Serverless Managed）/ BYOC |
| SLA / コンプライアンス | SOC 2（Team プラン以上）/ Enterprise はカスタムSLA |
| 価格モデル | 使用量ベース。書込 $2.50/GiB、ストレージ $0.33/GiB/月、クエリ $0.0075/TiB |
| デプロイ手段 | pip / npm / Docker（OSS）/ Serverless（Cloud）/ BYOC（VPC） |
| マルチテナンシー | コレクション単位の分離（テナント分離は限定的。OSS版はRBAC未対応） |
| 可観測性 | 詳細記載なし（公式 Prometheus/OTel サポートは未確認） |
| バックアップ / リストア | OSS: APIエクスポートまたはファイルシステムスナップショット（手動）/ Cloud: PITR対応 |
| データセットバージョニング | コレクションフォーク（CoW）、A/Bテスト、ロールアウト機能 |
| マルチモーダル対応 | 対応（OpenCLIP組み込み。テキスト・画像のcross-modal検索） |
| 特徴的な機能 | 組み込み動作、Rust v1.0コア（3〜5倍高速化）、WASM対応（ブラウザ実行）、デフォルト認証なし（セキュリティ注意） |
| セキュリティ上の懸念 | デフォルト認証無効。2025年4月時点で1,170公開インスタンス中406件がデータ漏洩 |
| 主な弱点 | 10M+ベクトルでのスケール限界、高同時実行での性能劣化、量子化未対応、ColBERT未対応 |
