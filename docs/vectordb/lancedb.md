# LanceDB 市場調査レポート

**製品/サービス**: LanceDB OSS / LanceDB Cloud (Public Beta) / LanceDB Enterprise
**開発元/提供元**: LanceDB, Inc.（米国、旧社名 EtoAI）
**公式URL**: https://lancedb.com/ / https://docs.lancedb.com/
**ライセンス**: Apache-2.0（OSS コア）
**調査時点**: 2025-06（資金調達・製品発表時点）〜 2026-04

---

## 1. 市場ポジション

### 位置付け
LanceDB は「AI-Native Multimodal Lakehouse」を標榜する組み込み型ベクトルデータベースであり、独立したサーバープロセスを不要とするライブラリとしてアプリケーションに組み込んで使用できる点が最大の特徴。ChromaDB と同様の組み込みカテゴリに属するが、より大規模（100万ベクトル以上）のワークロードと、テキスト・画像・動画・点群などマルチモーダルデータの管理・検索を主戦場とする。

### ファンディング・財務指標
- **累計調達額**: $41M（3ラウンド）
  - 2024年5月: シード〜Series A 前（Y Combinator）
  - 2025年6月: **$30M Series A**（Theory Ventures リード、CRV・Databricks Ventures・Runway・YC 参加）
- **2024年12月時点の ARR**: 約 $2.3M
- OSS ダウンロード数: **2,000万回超**（2025年6月時点）
- GitHub スター: **10,100+**（lancedb/lancedb）

### 採用企業（公表分）
- **Midjourney**（画像生成 AI）: ペタバイト規模のトレーニングデータ管理
- **Runway**（動画生成 AI）: 数十億ベクトルの検索
- **Character.ai**: 大規模エージェント検索基盤
- **Uber**: Uber-scale ストレージ（マルチバケット構成）への採用
- **Netflix**: （公式ウェブサイトで顧客として掲載）
- **Harvey AI**: RAG システムのスケーリング

### 市場での競合関係
- **主要競合**: Pinecone、Qdrant、Weaviate、Milvus（フル機能型ベクトル DB）
- **近接競合（組み込み型）**: ChromaDB（シンプルさで競合）、FAISS（ライブラリとして競合）
- **データ基盤系**: Databricks（Lance フォーマット統合）、DuckDB（SQL レイヤー連携）

---

## 2. 開発元のアピールポイント

### 1. Lance コロンナ形式によるディスクファーストアーキテクチャ
- Apache Parquet を超える「**100x faster random access**」を謳う独自カラム形式 Lance フォーマットを基盤とする
- Lance フォーマットは別リポジトリ（lance-format/lance）で独立 OSS として公開
- Pandas・DuckDB・Polars・PyArrow・PyTorch と直接統合可能（Parquet からの変換はコード 2 行）

### 2. サーバーレス組み込み型
- ライブラリとして in-process 動作するためインフラ管理ゼロ
- ローカル SSD から S3/GCS/Azure Blob まで同一 API で透過的に動作

### 3. マルチモーダルデータの第一級サポート
- テキスト・画像・動画・点群を同一テーブルで管理・検索
- 「Multimodal Lakehouse」として、Curation（データ精製）、Feature Engineering（特徴量生成）、Search & Analytics、Training（学習）の 4 機能を統合（Enterprise 版）

### 4. スケーラビリティ
- **100K QPS** を水平スケールで実現
- **100億行以上**の単一テーブルに対応
- **ペタバイト規模**のデータ管理実績（Midjourney・Runway の事例）

### 5. データバージョニングと再現性
- 全変更を自動バージョン管理（Git ライクな Branching・Shallow Clone 対応）
- スキーマ変更に際してデータコピーが不要なスキーマ進化機能

### 6. GPU インデックス構築
- CUDA（Linux）と MPS（Apple Silicon）による GPU アクセラレーション
- 「数十億ベクトルを 4 時間以内にインデックス化」（1〜8 GPU クラスタ）
- CPU 比で最大 20〜26 倍の速度向上（IVF/PQ トレーニング段階）

### 7. DuckDB・SQL 統合
- 2026年1月発表の Lance × DuckDB エクステンションにより、SQL でベクトル検索・FTS・ハイブリッド検索をテーブル関数として呼び出し可能
- 「Lance-native SQL retrieval」で RAG パイプラインをフル SQL で記述可能

### 8. Lance フォーマット v2.2 の性能改善
- ストレージを 50%+ 削減
- Parquet より優れた圧縮率
- Blob 読み取りで最大 **68x 高速化**
- 1.5M IOPS のベンチマーク（2026年1月発表）

---

## 3. 市場・調査会社が評価している強み

### ディスクベースでメモリ制限を超えた大規模検索
- メモリ搭載量を超えるデータセットを「パフォーマンスの崖なし」で処理（4xxi 社比較記事）
- IVF_PQ をディスク上で実行するため、インメモリ DB では困難な億〜数十億規模のローカル運用が可能

### 組み込みの簡潔さ + 大規模対応
- ChromaDB（最も簡単）と Qdrant（高機能）の中間的ポジション
- 「1M ベクトル以上・自己ホスト・頻繁な更新」のユースケースで ChromaDB より優位（encore.dev 比較ガイド）

### 高速全文検索との統合
- 独自 FTS（BM25 ベース）を内蔵し、ハイブリッド検索に直接組み合わせ可能
- サードパーティ研究（prrao87/lancedb-study）では **FTS 1534 QPS**（256 次元、1000 クエリ・並行 16 時）

### 豊富なリランカー統合
- RRF（デフォルト）、Cohere、CrossEncoder、ColBERT など複数リランカーを内蔵または公式サポート
- 41M ドキュメントの Wikipedia FTS ベンチマークを公開（WikiSearch 記事）

### ライセンスの明快さ
- **Apache-2.0** はベクトル DB 市場で珍しい（Qdrant も Apache-2.0 だが、Pinecone はプロプライエタリ、Weaviate は BSD-3）

### LangChain・LlamaIndex との統合
- 主要 LLM フレームワークのベクトルストアとして公式サポート済み

### 価格の安さ（OSS 版）
- 自己ホストは実質ストレージコストのみ（月額 $30 未満が目安）

---

## 4. 市場・調査会社が指摘している弱点・批判点

### 1. 並行書き込みの制限（最も深刻な批判）
- **「LanceDB does not support concurrent independent writes to the same table」**（公式 FAQ）
- 並行書き込みが多すぎるとコミット競合でリトライ上限に達し書き込み失敗が発生
- Python でのマルチプロセシングに `fork` 不可（Lance は内部でマルチスレッド動作するため）
- 2026年3月の GitHub Issue: S3 + DynamoDB 構成で複数 ECS タスクが同一テーブルに同時操作すると一貫性が崩れてスタック状態になる事例が報告

### 2. エコシステムの成熟度不足
- 「younger project with a smaller community」（encore.dev）
- LLM フレームワークとの統合が限定的（2024〜2025年時点）
- ドキュメントのエッジケース対応が不十分
- 監視・バックアップユーティリティが未成熟

### 3. ネイティブ RBAC・細粒度アクセス制御の欠如
- 行レベルアクセス制御は非対応（2025年時点）
- テーブル単位の暗号化キー設定は可能だが、RBAC 機能は「設計検討中」状態（GitHub Discussion #2158）
- アクセス制御はアプリケーション層または API ゲートウェイで実装する必要

### 4. マルチプロセス・高スループット書き込みシナリオでの信頼性
- delete / update / merge_insert の並行操作で頻繁に競合（GitHub Issue #1597、2024年9月）
- Take 操作での過剰 I/O 並行度問題（GitHub Issue #2977、2024年10月）

### 5. クラウド版がまだ Public Beta
- LanceDB Cloud は 2026年4月時点でも Public Beta 段階
- 本番 SLA 保証は Enterprise 版に限られる

### 6. ACORN フィルタリング非対応
- Weaviate の ACORN（グラフ内フィルタリング）のような「in-algorithm フィルタリング」は未実装
- pre-filter/post-filter 方式のため、高選択率フィルタ時に Recall 低下や性能劣化リスク

### 7. 本番運用実績の浅さ（大規模フルマネージド）
- Pinecone・Weaviate・Milvus と比較して本番大規模高スループット事例が少ない
- 「15人チームで ARR $2.3M」は依然スタートアップ規模（2024年12月時点）

### 8. TypeScript SDK の機能格差
- TypeScript は現在 `IvfSq` インデックスタイプ非対応
- Rust SDK はまだ機能が限定的（Python SDK が最も機能豊富）

---

## 5. ベンチマーク・競合比較・その他

### 公式ベンチマーク

| データセット | ベクトル数 | 次元数 | インデックス | QPS | Recall@1 | レイテンシ |
|---|---|---|---|---|---|---|
| GIST-1M | 100万 | 960 | IVF(256パーティション) + PQ(120サブ) | 〜178 QPS(@Recall 0.95) | >0.95 | <5ms |
| Enterprise | 記載なし | 記載なし | 記載なし | 100K QPS（水平スケール時） | 記載なし | 25ms（メタフィルタ込み 50ms 以内） |
| GPU インデックス構築 | 数十億 | 記載なし | IVF_PQ | N/A | N/A | 4時間以内（1〜8 GPU） |
| Lance v2.2 ストレージ | 記載なし | 記載なし | N/A | 1.5M IOPS | N/A | Blob 読み取り 68x 高速 |

- **注記**: GIST-1M ベンチマーク（2024年、M2 MacBook Pro Max 上）は公式ブログ（Chang She 著）による。FAISS（in-memory HNSW）の約 978 QPS に比べると単スレッドでは低速だが、ディスクベースでの動作であることを考慮。

### サードパーティベンチマーク（prrao87/lancedb-study）

| 指標 | LanceDB FTS | Elasticsearch FTS | LanceDB ベクトル | Elasticsearch ベクトル |
|---|---|---|---|---|
| QPS（直接） | 1,534 | 5,949 | 97 | 98 |
| P50 レイテンシ | 10.18ms | 2.59ms | 134.55ms | 110.37ms |
| P95 レイテンシ | 14.28ms | 4.07ms | 170.47ms | 212.83ms |

- **条件**: ワインレビューデータセット、256次元（nomic-ai/modernbert-embed-base）、並行 16、1000クエリ×3試行
- **考察**: FTS の QPS は Elasticsearch の 1/4 程度。ベクトル検索は互角（レイテンシは若干 LanceDB が高い）。ただし「実用的な差異は小さい」と著者は指摘。

### 競合比較での位置付け

| 比較軸 | LanceDB vs Chroma | LanceDB vs Qdrant | LanceDB vs Pinecone |
|---|---|---|---|
| セットアップ容易性 | Chroma が簡単（API シンプル） | LanceDB が簡単（組み込み） | LanceDB が簡単（サーバー不要） |
| 大規模スケール | LanceDB が優位（ディスク効率） | Qdrant が優位（動的シャーディング） | Pinecone が優位（フルマネージド） |
| フィルタリング性能 | LanceDB がやや優位 | Qdrant が大幅優位（ACORN） | Pinecone が優位（単一ステージ） |
| 本番運用負荷 | 同等（どちらも軽量） | Qdrant がやや高機能 | Pinecone がゼロ運用 |
| コスト | LanceDB が安価 | LanceDB が安価 | LanceDB が大幅安価 |
| マルチモーダル | LanceDB が圧倒的優位 | Qdrant は非対応 | Pinecone は非対応 |

### 価格情報

| プラン | 価格 | 主な制限/特徴 |
|---|---|---|
| OSS（Self-Hosted） | 無料（Apache-2.0） | コミュニティサポートのみ |
| Cloud（Public Beta） | 使用量ベース（ストレージのみ）、月額最低料金なし、現在無料 | Serverless、アイドル時ゼロスケール |
| Enterprise | 要見積（年間コミット）、AWS Marketplace 掲載 | 専任サポート、SLA、プライベートネットワーク |
- 参考価格帯: 中規模用途で $0〜$1,000/月（costbench.com 推計）

### コンプライアンス（Enterprise 版）
- SOC 2 Type II 取得済み
- HIPAA 準拠
- GDPR 対応（進行中）
- データの暗号化（保存時）、ストレージ・キャッシュ全体

### 最新動向（2025〜2026）
- **2025年6月**: $30M Series A 調達、Multimodal Lakehouse 発表（Search / EDA / Feature Engineering / Training の 4 機能）
- **2026年1月**: Lance × DuckDB エクステンション発表（Lance-native SQL retrieval）、Uber-scale マルチバケットストレージ、1.5M IOPS ベンチマーク
- **2026年4月**: v0.28.0-beta.9（最新リリース）、Hugging Face Hub でのネイティブ Lance サポート、Arrow ネイティブ地理空間サポート（R-Tree インデックス）、Git スタイルのブランチング・浅いクローン機能

---

## まとめ表

| 項目 | 値 |
|---|---|
| 提供元 / ライセンス | LanceDB, Inc. / Apache-2.0（OSS コア） |
| 位置付け | 組み込み型（in-process）マルチモーダルベクトル DB / AI Lakehouse |
| 対応インデックス種類 | IVF_FLAT、IVF_PQ、IVF_SQ、IVF_RQ（RaBitQ）、IVF_HNSW_PQ、IVF_HNSW_SQ |
| 最大次元数 | 明示的記載なし（実用上の制限は未公開） |
| 量子化対応 (SQ / PQ / Binary / RaBitQ 等) | SQ（float32→4倍圧縮）、PQ（8〜32倍圧縮）、RaBitQ（1bit量子化）、None(FLAT) |
| ACORN サポート | 非対応（pre-filter/post-filter 方式） |
| シャーディング / レプリケーション | OSS は明示的なシャーディングなし。オブジェクトストレージ経由での水平スケールが基本。Enterprise は水平スケールで 100K QPS |
| コンピュート/ストレージ分離 | 対応（設計思想のコア。S3/GCS/Azure Blob を第一級ストレージとして採用） |
| 公称最大データ規模 | 単一テーブル 100 億行超、ペタバイト規模（Midjourney・Runway 実績） |
| 公式ベンチマーク (QPS / Recall) | GIST-1M: Recall@1 >0.95 で ~5ms（M2 MacBook Pro）；Enterprise: 100K QPS（水平スケール） |
| フィルタ付き検索 | pre-filter（デフォルト）/ post-filter 選択可。スカラーインデックス（BTree・Bitmap・LabelList）対応 |
| ハイブリッド検索 (BM25+Vector) | 対応（内蔵 FTS + ベクトル検索 + RRF/Cohere/CrossEncoder/ColBERT リランカー） |
| SPLADE / 学習型スパース対応 | 記載なし（汎用スパースベクトルフィールドで代用の可能性はあるが専用サポート未確認） |
| Late Interaction (ColBERT 等) 対応 | ColBERT Reranker として外部推論（Hugging Face 経由）をサポート。マルチベクトルストレージは記載なし |
| Cross-Encoder リランカー対応 | 対応（CrossEncoder、Cohere Rerank、ColBERT を内蔵 / API 統合で利用可能） |
| リコメンド API / 機能 | 専用 recommend API なし（汎用 kNN + フィルタで実装する前提） |
| 提供形態 (OSS / Managed / Enterprise) | OSS（Apache-2.0）、Cloud（Public Beta / Serverless）、Enterprise（年間コミット） |
| SLA / コンプライアンス | Enterprise: SOC 2 Type II、HIPAA、GDPR 対応。Cloud(Beta): SLA 未公開 |
| 価格モデル | OSS 無料；Cloud はストレージ従量課金（月額最低なし）；Enterprise はカスタム年間コミット |
| デプロイ手段 | Python/TypeScript/Rust SDK で in-process 組み込み、または Docker。Enterprise は分散マネージド |
| マルチテナンシー | Lance Namespace 仕様あり。ネイティブ RBAC は未実装（API ゲートウェイ層での実装が推奨） |
| 可観測性 | Dynatrace 統合対応。内蔵ダッシュボードは記載なし。データバージョニングと監査ログはネイティブ対応 |
| バックアップ / リストア | 自動バージョニングによる任意時点へのロールバック（データ複製なし）。ストレージ側スナップショット機能との組み合わせ |
| 特徴的な機能 | GPU インデックス構築（CUDA/MPS）、データバージョニング（Git スタイル）、DuckDB SQL 統合、マルチモーダル Lakehouse（Enterprise）、Lance フォーマット（100x 高速ランダムアクセス）、Arrow ネイティブ地理空間インデックス |
| 主なユーザー | Midjourney、Runway、Character.ai、Uber、Netflix、Harvey AI |

---

## 6. 参考URL

- [LanceDB 公式サイト](https://lancedb.com/)
- [LanceDB 公式ドキュメント](https://docs.lancedb.com/)
- [LanceDB GitHub リポジトリ](https://github.com/lancedb/lancedb)
- [Lance フォーマット GitHub](https://github.com/lance-format/lance)
- [LanceDB インデックス種類ドキュメント](https://docs.lancedb.com/indexing)
- [LanceDB ハイブリッド検索ドキュメント](https://docs.lancedb.com/search/hybrid-search)
- [LanceDB メタデータフィルタリング](https://docs.lancedb.com/search/filtering)
- [LanceDB ストレージアーキテクチャ](https://docs.lancedb.com/storage)
- [LanceDB GPU インデックス構築](https://docs.lancedb.com/indexing/gpu-indexing)
- [LanceDB Enterprise セキュリティ](https://docs.lancedb.com/enterprise/security)
- [LanceDB FAQ (OSS)](https://docs.lancedb.com/faq/faq-oss)
- [Lance × DuckDB SQL 統合ブログ](https://www.lancedb.com/blog/lance-x-duckdb-sql-retrieval-on-the-multimodal-lakehouse-format)
- [LanceDB Series A 発表ブログ](https://www.lancedb.com/blog/series-a-funding)
- [LanceDB ベンチマーク公式ブログ（Chang She）](https://medium.com/etoai/benchmarking-lancedb-92b01032874a)
- [LanceDB ベンチマーク研究（prrao87）](https://github.com/prrao87/lancedb-study)
- [DeepWiki: LanceDB ベクトルインデックス詳細](https://deepwiki.com/lancedb/lancedb/7.2-vector-indexes)
- [4xxi: ベクトルDB比較（LanceDB含む）](https://4xxi.com/articles/vector-database-comparison/)
- [encore.dev: ベクトルDB比較 2026](https://encore.dev/articles/best-vector-databases)
- [Zilliz: Qdrant vs LanceDB 比較](https://zilliz.com/comparison/qdrant-vs-lancedb)
- [Y Combinator: LanceDB プロファイル](https://www.ycombinator.com/companies/lancedb)
- [TechCrunch: LanceDB Midjourney 採用記事](https://techcrunch.com/2024/05/15/lancedb-which-counts-midjourney-as-a-customer-is-building-databases-for-multimodal-ai/)
- [LanceDB 2026年1月ニュースレター（1.5M IOPS）](https://lancedb.com/blog/newsletter-january-2026/)
- [LanceDB Fine-Grained Access Controls 議論](https://github.com/lancedb/lancedb/discussions/2158)
- [並行書き込み制限 Issue](https://github.com/lancedb/lancedb/issues/213)
- [Lance フォーマット v2.2 ベンチマーク](https://www.lancedb.com/blog/lance-format-v2-2-benchmarks-half-the-storage-none-of-the-slowdown)
