# pgvector 市場調査レポート

**製品/サービス**: pgvector (PostgreSQL 拡張機能、OSS)
**開発元/提供元**: Andrew Kane (個人開発・OSSコミュニティ維持)
**公式 URL**: https://github.com/pgvector/pgvector
**ライセンス**: PostgreSQL License (寛容なオープンソースライセンス)
**調査時点**: 2026-04

---

## 1. 市場ポジション

### 概要

pgvector は PostgreSQL の拡張機能として提供されるベクトル類似検索ライブラリであり、独立したベクトルデータベース製品ではなく「既存の PostgreSQL をベクトル DB として機能させる拡張」という独自のポジションを占める。

### 採用状況・エコシステム

- **GitHub スター数**: 2025年時点で 15,000 超（ベクトル DB 拡張の中でトップクラス）
- **マネージドサービスへの標準搭載**: AWS RDS/Aurora、Google Cloud SQL/AlloyDB、Azure Database for PostgreSQL、Supabase、Neon、Tembo など、主要マネージド PostgreSQL サービスが標準でバンドル
- **Supabase の事例**: 新規サインアップの約 30% が pgvector を使用する AI ビルダー（2025年報告）
- **Instacart の移行事例**: 2025年5月に Elasticsearch から PostgreSQL + pgvector へ移行し、ストレージ・インデックスコストを 80% 削減、ゼロ結果検索を 6% 改善
- **PostgreSQL 自体の拡大**: 2025年に PostgreSQL の採用率が 55.6% に達し（前年比 7ポイント増）、AI ユースケースが主な牽引力

### 市場における位置づけ

- AI アプリ開発において「専用ベクトル DB を追加導入せずに、既存 Postgres をそのままベクトル検索に使う」という運用簡素化ニーズに応える
- 特に「すでに Postgres を使っているチーム」「スタートアップ・中小規模のワークロード（〜数千万ベクトル）」「コスト最適化重視のユーザー」にフィットする
- 2022〜2025 年に専用ベクトル DB が急増した反動として、2026 年には「リレーショナル DB 拡張への回帰」トレンドが顕著化。2025年だけで PostgreSQL エコシステムへの大型買収が相次ぐ（Databricks が Neon を $10 億で買収、Snowflake が Crunchy Data を $2.5 億で買収）

---

## 2. 開発元のアピールポイント

### 2-1. サポートするインデックス種類

| インデックス | 特徴 | チューニングパラメータ |
|---|---|---|
| HNSW | 多層グラフ構造。クエリ性能が高い | `m` (デフォルト 16)、`ef_construction` (デフォルト 64)、クエリ時 `hnsw.ef_search` (デフォルト 40) |
| IVFFlat | ベクトルをリストに分割。ビルドが速くメモリ消費が少ない | `lists` (推奨: 行数/1000〜√行数)、クエリ時 `ivfflat.probes` (デフォルト 1) |

### 2-2. 最大次元数

| 型 | 最大次元数 | ストレージサイズ |
|---|---|---|
| `vector` (float32) | 16,000 次元 | `4 × 次元数 + 8` バイト |
| `halfvec` (float16) | 16,000 次元 | `2 × 次元数 + 8` バイト |
| `bit` (バイナリ) | 64,000 次元 | `次元数 / 8 + 8` バイト |
| `sparsevec` | 16,000 非ゼロ要素 | `8 × 非ゼロ要素数 + 16` バイト |

### 2-3. サポートする距離メトリクス

- L2 距離 (Euclidean)
- 内積 (Inner Product)
- コサイン距離
- L1 距離 (Taxicab、v0.7.0〜)
- Hamming 距離（バイナリベクトル向け）
- Jaccard 距離（バイナリベクトル向け）

### 2-4. 量子化・データ型

- **Half-precision ベクトル (`halfvec`)**: スカラー量子化の一形態。float16 でメモリを半減。4,000 次元までインデックス対応
- **バイナリ量子化**: `binary_quantize()` 関数で 1 ビットへ変換。最大 64,000 次元まで対応
- **スパースベクトル (`sparsevec`)**: 非ゼロ要素のみ格納。TF-IDF・BM25・SPLADE の出力を効率的に格納可能（v0.7.0〜）

### 2-5. 主要アピールポイント

1. **ゼロ追加コスト**: 既存 PostgreSQL インフラに追加ライセンス費・クエリ課金なしで導入可能
2. **SQL との統合**: 標準 SQL でベクトル検索とリレーショナルクエリを組み合わせ可能（JOINs、集計、フィルタリング等）
3. **ACID トランザクション**: ベクトルデータと通常のリレーショナルデータにわたるトランザクション一貫性保証
4. **PostgreSQL エコシステムの活用**: Prometheus エクスポーター、バックアップ・レプリケーション、ORM 連携など既存ツールをそのまま利用
5. **PITR (Point-in-Time Recovery)**: WAL ベースのレプリケーションとポイントインタイム復元
6. **iterative_scan (v0.8.0〜)**: フィルタ付き検索の「過剰フィルタリング」問題を解消するインデックスの反復スキャン機能

---

## 3. 市場・調査会社が評価している強み

### 3-1. コスト競争力

- 既存 Postgres インフラ上でインクリメンタルコスト実質ゼロ
- AWS での自己ホスト比較: Pinecone 同等ワークロードの約 75% コスト削減（各種比較記事より、2025年推定）
- TCO (総所有コスト) が専用ベクトル DB 比 40〜60% 低減という評価あり（ベンダー系記事）

### 3-2. pgvectorscale との組み合わせによる高スループット

- Timescale が開発する `pgvectorscale` 拡張（StreamingDiskANN インデックス実装）と組み合わせた場合、50M ベクトルで 99% リコール時に **471.57 QPS** を達成（Qdrant の 41.47 QPS の 11.4 倍）— Timescale 公開ベンチマーク、2025年
- Pinecone の s1 ストレージ最適化インデックスと比較して **p95 レイテンシが 28 倍低く**、クエリスループットが **16 倍高い** — Timescale 公開ベンチマーク

### 3-3. バージョン進化による性能向上

- pgvector 0.5.0 (HNSW 初期実装) → 0.7.0 でインデックスビルド時間が最大 **150 倍**改善（7,479秒 → 49秒、dbpedia-openai-1000k-angular データセット）
- QPS が IVFFlat 比 **31.6 倍**（8 QPS → 253 QPS）、p99 レイテンシが **28 倍**改善（150ms → 5.51ms）
- v0.8.0 でバイナリ量子化により基本検索が最大 **9.4 倍**高速化、メモリフットプリント **32 倍**削減で 95% 精度維持

### 3-4. 運用統合性

- 新規サービス追加不要（シングルシステム運用）
- ACID 保証・WAL レプリケーション・PITR など成熟した PostgreSQL 運用基盤
- Kubernetes 上での CloudNativePG による宣言的デプロイ対応
- 主要クラウドのマネージドサービスが pgvector をバンドル済み

### 3-5. ハイブリッド検索

- `tsvector` を使った全文検索と pgvector の意味検索を SQL で組み合わせ可能
- `sparsevec` を使って SPLADE/BM25 のスパース表現を格納、デンスベクトルとのハイブリッド検索を実現
- ParadeDB（BM25 対応 Postgres 拡張）との組み合わせで本格的な BM25+ベクトルハイブリッド検索が可能

---

## 4. 市場・調査会社が指摘している弱点・批判点

### 4-1. スケールの天井

- **推奨上限**: 多くの評価レポートが「快適に運用できるのは 5,000万〜1億ベクトルまで」と指摘
- それ以上のスケールでは PostgreSQL のリレーショナルストレージモデルが壁となり、Milvus・Pinecone 等の専用ベクトル DB に劣る
- 水平スケーリングには Citus 拡張またはアプリケーション層のシャーディングが必要（専用ベクトル DB のように組み込みシャーディングは持たない）

### 4-2. フィルタ付き検索の性能劣化

- 旧来の pgvector はプリフィルタリング機能を欠いており、フィルタが適用されると ANN インデックスを使わずに逐次スキャンにフォールバックするケースがあった
- フィルタの選択性が低い場合（広い範囲のフィルタ）は性能が著しく低下: カテゴリフィルタで追加オーバーヘッドが 2.30 倍のケースも（Achilles Heel of Vector Search, 2025）
- v0.8.0 の `iterative_scan` 機能で改善されたが、設定が必要であり、全ての状況でベストとはいえない

### 4-3. クエリプランナーの限界

- PostgreSQL のクエリプランナーはベクトル類似検索のコストモデルに最適化されていない
- フィルタ付きベクトルクエリでプランナーが適切な実行計画を選択できない場合がある
- v0.8.0 でコスト推定が改善されたが、根本的なアーキテクチャ上の制約は残る

### 4-4. HNSW インデックスのメモリ圧迫

- 数百万ベクトルの HNSW インデックスビルドに 10GB 以上の RAM を消費する場合がある
- 本番データベース上でのインデックスビルドは長時間（数時間単位）の高メモリ負荷を発生させる
- OLTP ワークロードと同一 Postgres インスタンス上で ANN 検索を実行すると、共有バッファプールを競合してパフォーマンスが低下するリスク

### 4-5. リアルタイム更新の難しさ

- IVFFlat: 時間経過とともにクラスタ分布が最適でなくなり、定期的なインデックス再構築が必要
- HNSW: 頻繁な INSERT 時のロック競合によるライトスループットのボトルネック
- 新規に挿入されたドキュメントが検索可能になるまでに遅延が生じるケースあり

### 4-6. 高度なベクトル専用機能の不足

- **Late Interaction / ColBERT**: ネイティブ非対応（VectorChord 等の別拡張で対応可能）
- **組み込みリランカー**: Cross-Encoder 等のリランカーは外部推論サービスへの依存が必要
- **Recommend API**: Qdrant の `recommend` エンドポイントのような専用レコメンド API は存在せず、SQL で自前実装が必要
- **ACORN フィルタ付き ANN 最適化**: 記載なし（他製品に比べフィルタ戦略の柔軟性が低い）
- **GPU インデックスビルド**: 非対応（cuVS/RAFT 等の GPU 加速なし）

### 4-7. ベンチマーク数値の注意点

- pgvectorscale との組み合わせ結果を「pgvector」として引用するケースがあり、素の pgvector とは性能が大きく異なる場合がある（The New Stack, "Why pgvector Benchmarks Lie"）
- 古いベンチマーク（IVFFlat 時代）と現在（HNSW + 量子化）では性能特性が全く異なる

---

## 5. ベンチマーク・競合比較・その他

### 5-1. 主要ベンチマーク結果

#### pgvector 0.7.0 (HNSW + バイナリ量子化) — Instaclustr / Jonathan Katz ベンチマーク

| 条件 | 結果 |
|---|---|
| データセット | dbpedia-openai-1000k-angular (100万ベクトル、1536次元) |
| ハードウェア | r7gd.16xlarge (64 vCPU / 512 GiB RAM)、r7i.16xlarge |
| 99% リコール時スループット | 253 QPS (r7gd) |
| p99 レイテンシ | 5.51ms (IVFFlat 比 28倍改善) |
| インデックスビルド時間 | 49秒 (v0.5.0 比 150倍改善) |
| 比較 (IVFFlat) | 8 QPS、150ms p99 |

#### pgvectorscale + pgvector — Timescale ベンチマーク (2025年)

| 条件 | pgvector+pgvectorscale | Qdrant |
|---|---|---|
| データセット | 5,000万ベクトル |  |
| 99% リコール時 QPS | **471.57 QPS** | 41.47 QPS |
| 90% リコール時 QPS | **1,589 QPS** | 360 QPS |
| p95 レイテンシ | 60.42ms | 36.73ms (39% 低い) |
| p99 レイテンシ | 74.60ms | 38.71ms (48% 低い) |
| インデックスビルド時間 | 11.1時間 | 3.3時間 |

> **注意**: Timescale 社が自社製品 pgvectorscale のベンチマークを公表したもの。中立的な第三者ベンチマークではない。

#### datastores.ai ベンチマーク (100万ベクトル / 128次元 / HNSW / 8 vCPU / 32GB)

| 指標 | pgvector |
|---|---|
| QPS | 1,800 QPS |
| P50 レイテンシ | 4.2ms |
| P99 レイテンシ | 15ms |
| Recall@10 | 95% |
| メモリ使用量 | 1.2 GB / 100万ベクトル |

> 同サイトのテストでは pgvector は 10 製品中最下位圏だが、「1,000〜5,000 QPS は多くのアプリに十分」とのコメントあり。

#### pgvector vs Qdrant — Nirant Kasliwal ベンチマーク (1M OpenAI ベクトル、t3.2xlarge)

- pgvector (IVFFlat 時代): Qdrant比でスループット **1/15**、精度が **18% 低い**
- p95 レイテンシ: pgvector 4.02s〜45.46s (最悪値) vs Qdrant 2.85s

> **注意**: このベンチマークは HNSW 実装以前の IVFFlat 時代のもの。現在は大幅に改善済み。

### 5-2. 競合との比較

| 観点 | pgvector の優位点 | pgvector の劣位点 |
|---|---|---|
| **vs. Qdrant** | pgvectorscale 併用時はスループットで勝る場合あり。SQL 統合・運用コスト・ACID 保証が強み | 単体でのレイテンシ (p95/p99) は Qdrant が優位。フィルタ付き検索・横展開スケーリング・専用ベクトル機能は Qdrant が充実 |
| **vs. Pinecone** | 自己ホストでコスト 75% 削減。SQL 統合・ベンダーロックインなし | Pinecone のフルマネージドゼロ運用・グローバル分散・自動スケーリングに劣る |
| **vs. Milvus/Zilliz** | 既存 Postgres チームへのシームレス導入。インフラ追加不要 | 数億〜数十億ベクトル規模では Milvus の分散アーキテクチャが必要 |
| **vs. Weaviate** | コスト・SQL 親和性が高い | マルチモーダル対応、組み込みベクタライザー、ハイブリッド検索の成熟度で劣る |

### 5-3. 価格情報

- **OSS 版**: 無償（PostgreSQL License）
- **pgvectorscale**: 無償 OSS（Timescale 提供）
- **マネージドサービス経由**: 各プラットフォームの PostgreSQL 料金のみ（pgvector 追加課金なし）
  - AWS RDS/Aurora: 既存料金に含む
  - Supabase: Free プランから pgvector 利用可能
  - Neon: サーバーレス PostgreSQL として従量課金
- **専用 SaaS/Enterprise サポート**: pgvector 単体の商用サポート契約は存在しない（各マネージドサービスのサポート体制に依存）

### 5-4. 最新動向

| バージョン | リリース日 | 主な変更 |
|---|---|---|
| **0.8.2** | 2026年2月25日 | 並列 HNSW インデックス構築時のバッファオーバーフロー修正、Postgres 18 対応強化 |
| **0.8.1** | 2025年9月4日 | Postgres 18 rc1 対応、`binary_quantize` 関数のパフォーマンス最適化 |
| **0.8.0** | 2024年10月30日 | iterative_scan 導入（フィルタ付き検索の過剰フィルタリング解消）、コスト推定改善、HNSW インサート/スキャン高速化 |
| **0.7.0** | 2024年4月29日 | `halfvec`・`sparsevec`・`bit` 型追加、`binary_quantize`・`l2_normalize`・`subvector` 関数追加、L1 距離インデックス対応 |

### 5-5. 周辺エコシステム

- **pgvectorscale** (Timescale): StreamingDiskANN インデックスによる大規模向けパフォーマンス強化
- **ParadeDB**: BM25 フルテキスト検索を追加し pgvector と組み合わせたハイブリッド検索を実現
- **VectorChord**: ColBERT/Late Interaction 対応を PostgreSQL に追加
- **CloudNativePG**: Kubernetes 上での宣言的 pgvector デプロイを支援

---

## 6. 参考URL

### 公式・一次情報

- [pgvector GitHub リポジトリ](https://github.com/pgvector/pgvector)
- [pgvector CHANGELOG](https://github.com/pgvector/pgvector/blob/master/CHANGELOG.md)

### ベンチマーク・性能比較

- [The 150x pgvector speedup: a year-in-review | Jonathan Katz](https://jkatz05.com/post/postgres/pgvector-performance-150x-speedup/)
- [pgvector performance: Benchmark results and 5 ways to boost performance | Instaclustr](https://www.instaclustr.com/education/vector-database/pgvector-performance-benchmark-results-and-5-ways-to-boost-performance/)
- [Vector Database Benchmarks — Latency, QPS, Recall Compared | datastores.ai](https://datastores.ai/benchmarks)
- [pgvector vs Qdrant — 1M OpenAI Benchmark | Nirant Kasliwal](https://nirantk.com/writing/pgvector-vs-qdrant/)
- [Pgvector vs. Qdrant: Open-Source Vector Database Comparison | TigerData](https://www.tigerdata.com/blog/pgvector-vs-qdrant)
- [Supercharging vector search performance with pgvector 0.8.0 on Amazon Aurora | AWS](https://aws.amazon.com/blogs/database/supercharging-vector-search-performance-and-relevance-with-pgvector-0-8-0-on-amazon-aurora-postgresql/)

### 批判・限界・弱点分析

- [The Case Against pgvector | Alex Jacobs](https://alex-jacobs.com/posts/the-case-against-pgvector/)
- [Start with pgvector: Why You'll Outgrow It Faster Than You Think | Qdrant](https://qdrant.tech/blog/pgvector-tradeoffs/)
- [The Achilles Heel of Vector Search: Filters | Bits & Backprops](https://yudhiesh.github.io/2025/05/09/the-achilles-heel-of-vector-search-filters/)
- [Vector Database Performance Compared: pgvector vs Pinecone vs Qdrant vs Weaviate | DEV Community](https://dev.to/kencho/vector-database-performance-compared-pgvector-vs-pinecone-vs-qdrant-vs-weaviate-2b4h)

### 市場分析・採用動向

- [Debunking 6 common pgvector myths | The Nile](https://www.thenile.dev/blog/pgvector_myth_debunking)
- [PostgreSQL Dominates 2025: 55% Adoption | byteiota](https://byteiota.com/postgresql-dominates-2025-55-adoption-crushes-mysql-as-all-databases-migrate/)
- [Best Vector Databases in 2025: A Complete Comparison | Firecrawl](https://www.firecrawl.dev/blog/best-vector-databases)
- [What's Changing in Vector Databases in 2026 | DEV Community](https://dev.to/actiandev/whats-changing-in-vector-databases-in-2026-3pbo)
- [Why AI Startups Choose PostgreSQL: Supabase, Neon, pgVector | Medium](https://medium.com/@takafumi.endo/why-ai-startups-choose-postgresql-supabase-neon-pgvector-7d1e1383b3dd)

### ハイブリッド検索

- [Hybrid Search in PostgreSQL: The Missing Manual | ParadeDB](https://www.paradedb.com/blog/hybrid-search-in-postgresql-the-missing-manual)
- [Hybrid search with PostgreSQL and pgvector | Jonathan Katz](https://jkatz05.com/post/postgres/hybrid-search-postgres-pgvector/)

---

## まとめ表

| 項目 | 値 |
|---|---|
| 提供元 / ライセンス | Andrew Kane (OSSコミュニティ) / PostgreSQL License (無償・商用利用可) |
| 位置付け | PostgreSQL 拡張機能（RDBMS 拡張型ベクトル検索）、独立した DB サーバーではない |
| 対応インデックス種類 | HNSW、IVFFlat の 2 種のみ |
| 最大次元数 | float32: 16,000次元 / halfvec (float16): 16,000次元 / bit: 64,000次元 / sparsevec: 16,000 非ゼロ要素 |
| 量子化対応 | halfvec (SQ fp16相当) ○ / バイナリ量子化 ○ / PQ ✕ / RaBitQ ✕ / int8 SQ ✕ |
| シャーディング / レプリケーション | WAL ベースレプリケーション ○ / シャーディングは Citus 等が必要（ネイティブ非対応） |
| コンピュート/ストレージ分離 | なし（Neon の pgvector 利用時は Neon 自体が分離アーキテクチャ） |
| 公称最大データ規模 | 快適運用 ～5,000万ベクトル / pgvectorscale 使用時 ～5,000万ベクトルで高性能 / 1億+ は専用 DB 推奨 |
| 公式ベンチマーク (QPS / Recall) | HNSW: 253 QPS @ 99% recall、1M ベクトル (Instaclustr; r7gd.16xlarge) |
| フィルタ付き検索 | v0.8.0 で iterative_scan 追加。post-filter が基本。pre-filter 専用最適化は記載なし |
| ハイブリッド検索 (BM25+Vector) | SQL で tsvector と組み合わせ可能。BM25 スコアリングは ParadeDB 等の追加拡張が必要 |
| SPLADE / 学習型スパース対応 | sparsevec 型で格納可能 (v0.7.0〜)。DB 内推論機能はなし。外部生成したスパースベクトルを格納 |
| Late Interaction (ColBERT 等) 対応 | ネイティブ非対応。VectorChord 拡張で対応可 |
| Cross-Encoder リランカー対応 | 非対応（外部推論サービスとの連携が必要） |
| リコメンド API / 機能 | 専用 API なし。SQL の kNN クエリで代替実装が必要 |
| 提供形態 | OSS のみ（商用サポート契約なし）。各マネージド PostgreSQL サービス経由で事実上マネージド利用可 |
| SLA / コンプライアンス | pgvector 単体では規定なし。各マネージドサービス (AWS, Google, Azure 等) の SLA に依存 |
| 価格モデル | 無償 (PostgreSQL License)。追加ライセンス費・クエリ課金なし |
| デプロイ手段 | PostgreSQL 拡張として追加（`CREATE EXTENSION vector`）。Docker / Helm / CloudNativePG / Kubernetes 対応 |
| マルチテナンシー | PostgreSQL のスキーマ/テーブル分離を利用。専用マルチテナント機能はなし |
| 可観測性 | PostgreSQL 標準の pg_stat_* ビュー / Prometheus エクスポーター / EXPLAIN による実行計画確認 |
| バックアップ / リストア | WAL ベース PITR ○ / スナップショットはホスティング基盤依存 |
| 特徴的な機能 | SQL との完全統合 (JOIN・集計・フィルタを自由に組み合わせ可能)、PostgreSQL 全エコシステム活用、追加コストゼロ、ACID 保証 |
