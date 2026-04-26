# Turbopuffer 市場調査レポート

**製品/サービス**: turbopuffer（クラウドマネージドサービスのみ、OSS版なし）
**開発元/提供元**: Turbopuffer Inc.（カナダ・オタワ）
**公式URL**: https://turbopuffer.com/
**ライセンス**: プロプライエタリ（クローズドソース）
**調査時点**: 2026-04

---

## 1. 市場ポジション

### 概要

turbopuffer は 2023 年に元 Shopify エンジニアの Simon Hørup Eskildsen（CEO）と Justine Li（CTO）が創業したスタートアップが提供するサーバーレス型ベクトル・全文検索エンジン。「**オブジェクトストレージネイティブ**」アーキテクチャを差別化軸とし、既存のベクトル DB と比較して圧倒的なコスト効率（最大 10x 安価）を訴求している。

### 規模・トラクション

| 指標 | 値 |
|---|---|
| 保存ドキュメント数 | 3.5 兆件以上（13PB+） |
| 書き込みスループット | 10M+ writes/秒（グローバル合計） |
| クエリスループット | 25k+ queries/秒 |
| ARR | 「数千万ドル台」（2025 年時点、非公開） |
| 従業員数 | 約 25 名（2026 年時点） |
| 投資家 | Lachy Groom、Thrive Capital（2025 年 12 月シード追加ラウンド） |

### 主な採用顧客

| 顧客 | 用途 | 成果 |
|---|---|---|
| **Cursor** | コードベースのセマンティック検索（80M+ ネームスペース、1T+ ドキュメント） | コスト 95% 削減、1M+ writes/秒 |
| **Notion** | AI ワークスペース検索（1M+ ネームスペース、10B+ ベクトル） | コスト 80% 削減・ユーザー単位 AI 課金廃止 |
| **Linear** | プロダクト管理の検索（1.5M+ ネームスペース、250M+ ドキュメント） | コスト 70% 削減、p50=13ms |
| **Anthropic** | 社内 RAG 基盤 | — |
| **Atlassian** | — | — |
| **Superhuman** | メール検索（9B+ ドキュメント） | コスト 20%+ 削減 |
| **Vercel** | AI コパイロット | $2M+ 増分収益（ROI 32x） |
| **TELUS** | 顧客サポート | p99 < 100ms、57k+ アクティブユーザー |

### 競合との関係

- **主要競合**: Pinecone（マネージドサービス）、Weaviate、Qdrant（OSS + クラウド）、Milvus
- **差別化軸**: ① オブジェクトストレージコスト（約 2 ¢/GB）による圧倒的安さ ② 無制限マルチテナント対応 ③ 運用負荷ゼロのサーバーレス
- **対象ユーザー**: SaaS 企業・AI ネイティブアプリ開発者（マルチテナント RAG 用途に特化）

---

## 2. 開発元のアピールポイント

### 2-1. オブジェクトストレージネイティブアーキテクチャ

- S3/GCS/Azure Blob をストレージの Source of Truth とする LSM 型設計
- 従来の SSD 複製型 DB（約 $60/GB/月）に対し、オブジェクトストレージは約 $2/GB/月 → **最大 100x のストレージコスト削減**
- 3 階層キャッシュ（RAM → NVMe SSD → Object Storage）で「ぬいぐるみ(pufferfish)効果」を実現：アクセスパターンに応じてデータが自動でコールドからホットに移動

### 2-2. 圧倒的なマルチテナント対応

- 1 ネームスペース = S3 上の 1 プレフィックス
- **無制限のネームスペース数**（Pinecone の上限 100,000 に対して制限なし）
- 1 ネームスペースあたり最大 **500M ドキュメント**
- Cursor は 8,000 万を超えるネームスペースを運用中

### 2-3. ANN v3 インデックスと量子化

- 独自の **SPFresh**（センtroid ベース ANN インデックス）を採用
  - HNSW・DiskANN のようなグラフ型より、オブジェクトストレージとの相性が良く、ラウンドトリップを最小化
  - インデックスの再構築なしに増分更新可能
- **RaBitQ バイナリ量子化**（ANN v3）：ベクトルを 16–32x 圧縮し、信頼区間ベースのリランクで Recall を維持
- 自動チューニングで **Recall@10: 90–100%** を保証

### 2-4. ハイブリッド検索

- ベクトル検索（ANN/kNN）と BM25 全文検索を同一クエリで実行可能
- 結果のマージ（RRF 等）はアプリ側で行う設計
- フィルタ付き検索：インバーテッドインデックスによるメタデータフィルタ（Eq/Gt/Glob/Regex 等）

### 2-5. サーバーレスと高可用性

- ステートフルな依存を持たない設計により、ノード障害時も自動フェイルオーバー
- 公称 **99.99% 稼働率**（エンタープライズプランでは SLA 99.95% を文書化）
- キャッシュウォームアップ API でコールドスタートを事前に緩和可能

### 2-6. コスト削減実績

- 2026 年 2 月にクエリ価格を最大 **94% 値下げ**
- 顧客サイドでも 70–95% のコスト削減を報告

---

## 3. 市場・調査会社が評価している強み

### 3-1. 価格競争力

ZenML・Liveblocks・Agentset 等の独立系比較記事が共通して「**大規模ベクトル検索で最もコスト効率が良いマネージドサービス**」と評価。競合（Pinecone 等）が in-memory ストレージ中心のコスト構造を持つのに対し、オブジェクトストレージの経済性を活かした設計。

### 3-2. マルチテナント SaaS への最適性

- 「Namespace ≒ テナント」の設計が SaaS アーキテクチャと自然にマッチ
- Pinecone のような「インデックス数上限」「ネームスペース上限」がなく、テナントごとに独立したインデックスを無制限に持てる
- Cursor・Notion・Linear のような大規模 SaaS の採用事例が強力なソーシャルプルーフとなっている

### 3-3. 運用負荷の低さ

- インフラ管理・スケーリング・レプリケーション設定が不要
- Pylon 社は「**3 日で本番稼働**」を達成
- Linear 社は「Elasticsearch・PGVector からの移行でインフラ運用から解放された」と証言

### 3-4. エンタープライズセキュリティを標準提供

- SOC 2 Type 2・GDPR・HIPAA BAA が標準プランから利用可能（Pinecone 等は上位プランのみ）
- 独立系レビュー記事でも「**エンタープライズ機能をエンタープライズ価格なしに提供**」と評価

### 3-5. 技術的信頼性

- ANN v3 ブログポスト（2026 年公開）で 1,000 億ベクトル規模での p99=200ms を実証
- Google Cloud のケーススタディとして取り上げられており、クラウドベンダーからの評価も高い

---

## 4. 市場・調査会社が指摘している弱点・批判点

### 4-1. コールドスタートレイテンシ

- **キャッシュなし時の p50: 285–444ms**（1M ドキュメント）、p999 は数百 ms〜数秒
- Zilliz ブログはコールド p99 が「最大 4 秒に達する可能性」を指摘（競合による批判）
- キャッシュヒット率が低いユースケース（ランダムアクセス多数、大規模コールドネームスペース）には不向き

### 4-2. 書き込みレイテンシ

- 書き込みが必ずオブジェクトストレージを経由するため **p50=285ms（500kB バッチ）**
- **1 ネームスペースあたり 1 WAL エントリ/秒** の制限（高頻度書き込みには複数ネームスペース分割が必要）
- リアルタイム性が求められる高頻度更新ワークロード（EC など）には不適

### 4-3. クローズドソース

- OSS 版なし → ベンダーロックインリスク
- 自社インフラへのデプロイ不可（BYOC は Enterprise プランのみ交渉ベース）
- 競合が OSS で機能を開示する中、内部実装の透明性が低い

### 4-4. 最小課金要件

- Launch プランで **$64/月の最低スペンド**
- 小規模プロジェクトや PoC 段階での利用コストがネック（フリーティア未提供）

### 4-5. 機能的な制限

- **組み込みの埋め込みモデルなし**（Weaviate の text2vec 等に相当する機能がない）
- **ネームスペース横断検索ができない**（コンプライアンス対応でのユーザーデータ一括削除が困難）
- **スパースベクトル（SPLADE 等）は未対応**（ロードマップには掲載）
- **Late Interaction（ColBERT 等）は未対応**（ロードマップには掲載）
- **リランカー（Cross-Encoder）の組み込みなし**（外部サービス連携推奨）
- **スキーマ変更が柔軟でない**（RDBMS のような ALTER TABLE 的操作が困難）
- **1 ネームスペースあたりのベクトル列数は最大 2 列**（複数ベクトルは 2026 年 3 月より対応）
- トランザクション（汎用 read-write）は未対応。条件付き書き込みのみ Serializable 相当

### 4-6. エコシステムの若さ

- 創業 2023 年とまだ新しく、Pinecone/Weaviate と比べると実績ドキュメントが少ない
- VectorDBBench・ann-benchmarks.com への公式参加実績が限定的で、第三者比較データが薄い

---

## 5. ベンチマーク・競合比較・その他

### 5-1. 公式ベンチマーク（ANN v3 ブログ、2026 年 2 月）

| 指標 | 値 | 条件 |
|---|---|---|
| p99 クエリレイテンシ | **200ms** | 1,000 億ベクトル |
| QPS | **1,000+ 本番**（理論値 10,000 QPS） | — |
| Recall@10 | **90–100%**（自動チューニング） | — |
| バイナリ量子化圧縮率 | **16–32x**（f16 比） | RaBitQ 使用 |

### 5-2. ウォーム/コールドレイテンシ詳細（公式ドキュメント）

| 状態 | p50 | p90 | 備考 |
|---|---|---|---|
| ウォーム（RAM キャッシュ） | **8ms** | 10–18ms | 1M ドキュメント |
| コールド（オブジェクトストレージ） | **343ms** | 444ms | 1M ドキュメント |
| 書き込み | **285ms** | — | 500kB バッチ |

### 5-3. 第三者テスト

Joe Sack（Substack）による 100k ベクトル（OpenAI text-embedding-3-small, 1536 次元）テスト：
- ホットキャッシュ時レイテンシ: **13ms**
- 975 クエリ中 **83%（809 件）が Recall@1 = 100%**
- 17%（166 件）は Recall が約 90%、6 件のみ 60%

### 5-4. 顧客実績ベースの性能数値

| 顧客 | レイテンシ | ドキュメント数 |
|---|---|---|
| Linear | p50 = 13ms | 250M+ |
| Pylon | p90 = 24ms | 300M+ |
| Superhuman | p90 = 60ms | 9B+ |
| TELUS | p99 < 100ms | — |

### 5-5. 競合との比較

| 比較軸 | turbopuffer | Pinecone | Weaviate | Qdrant |
|---|---|---|---|---|
| 提供形態 | マネージドのみ | マネージドのみ | OSS + Cloud | OSS + Cloud |
| ストレージ設計 | オブジェクトストレージ（コールド/ホット自動） | SSD/メモリ | SSD/メモリ | SSD/メモリ |
| ネームスペース制限 | **無制限** | 最大 100,000（標準） | 無制限（Collection） | — |
| ハイブリッド検索 | あり（BM25 + Vector） | あり | あり | あり |
| 組み込み埋め込み | **なし** | なし | あり（text2vec 等） | なし |
| ColBERT / Late Interaction | **なし**（ロードマップ） | なし | なし | なし |
| SPLADE / スパースベクトル | **なし**（ロードマップ） | あり | あり | あり |
| フリーティア | **なし** | あり | あり | あり |
| 最小月額 | $64 | 従量 | 従量 | 従量 |
| コスト（大規模） | **最安クラス** | 高め | 中程度 | 中程度 |
| SOC2/HIPAA | 標準提供 | 上位プランのみ | — | — |

### 5-6. 価格モデル

| プラン | 最低スペンド | 主な追加機能 |
|---|---|---|
| **Launch** | $64/月 | 全 DB 機能・マルチテナント・SOC2/GDPR |
| **Scale** | $256/月 | HIPAA BAA・SSO・監査ログ・Slack サポート（8-5） |
| **Enterprise** | $4,096/月以上（35% プレミアム） | シングルテナント・BYOC・CMEK・プライベートネットワーク・24/7 サポート・SLA 99.95% |

- 従量課金（ストレージ・クエリ・書き込み）はプランに応じた追加費用
- 2026 年 2 月にクエリ料金を最大 94% 値下げ
- コスト計算ツールを公式サイトに設置

### 5-7. 最新動向（2025–2026 年）

| 時期 | トピック |
|---|---|
| 2026 年 4 月 | ネームスペースピニング（高 QPS ユースケース向け安定コスト） |
| 2026 年 3 月 | 1 ドキュメントへの複数ベクトル対応・監査ログ（SIEM 連携）ベータ |
| 2026 年 2 月 | クエリ価格 94% 値下げ・正規表現インデックス・ANN v3 公開 |
| 2025 年 12 月 | Thrive Capital からの追加シード調達 |
| 2025 年 | 売上 10 倍・従業員 5 倍成長（CEO 発表） |
| ロードマップ | スパースベクトル対応・Late Interaction（ColBERT）対応・高度な全文検索（ハイライト等） |

### 5-8. 対応地域（2026 年 4 月時点）

- AWS: us-east-1、eu-west-1、ap-southeast-1 等（ロンドンリージョンを 2026 年 2 月追加）
- GCP、Azure Blob も対応（ストレージバックエンドとして）

---

## 6. 参考URL

- [turbopuffer 公式サイト](https://turbopuffer.com/)
- [turbopuffer アーキテクチャドキュメント](https://turbopuffer.com/docs/architecture)
- [turbopuffer トレードオフドキュメント](https://turbopuffer.com/docs/tradeoffs)
- [turbopuffer リミットドキュメント](https://turbopuffer.com/docs/limits)
- [turbopuffer セキュリティドキュメント](https://turbopuffer.com/docs/security)
- [turbopuffer 価格ページ](https://turbopuffer.com/pricing)
- [turbopuffer ロードマップ&変更履歴](https://turbopuffer.com/docs/roadmap)
- [turbopuffer 顧客事例](https://turbopuffer.com/customers)
- [turbopuffer ハイブリッド検索ドキュメント](https://turbopuffer.com/docs/hybrid)
- [ANN v3: 1000億ベクトルで p99=200ms（公式ブログ）](https://turbopuffer.com/blog/ann-v3)
- [turbopuffer: fast search on object storage（公式ブログ）](https://turbopuffer.com/blog/turbopuffer)
- [Jason Liu: TurboPuffer Object Storage-First Vector Database Architecture](https://jxnl.co/writing/2025/09/11/turbopuffer-object-storage-first-vector-database-architecture/)
- [ZenML: 10 Best Vector Databases for RAG Pipelines](https://www.zenml.io/blog/vector-databases-for-rag)
- [Liveblocks: What's the best vector database for building AI products?](https://liveblocks.io/blog/whats-the-best-vector-database-for-building-ai-products)
- [Amplify Partners: How Turbopuffer is Building The Future of Vector Databases](https://www.amplifypartners.com/barrchives/how-turbopuffer-is-building-the-future-of-vector-databases-with-ceo-simon-eskildsen)
- [Joe Sack: Testing Turbopuffer's Recall API](https://joesack.substack.com/p/testing-turbopuffers-recall-api-with)
- [Zilliz: Weaviate vs Turbopuffer Comparison](https://zilliz.com/comparison/weaviate-vs-turbopuffer)
- [PMF Show: How Simon Eskildsen Built TurboPuffer](https://www.pmf.show/blog/how-simon-eskildsen-built-turbopuffer-the-vector-db-powering-cursor-and-notion/)
- [Google Cloud Customer Story: turbopuffer](https://cloud.google.com/customers/turbopuffer)
- [BetaKit: Ex-Shopify engineers raise fresh financing to scale Turbopuffer](https://betakit.com/ex-shopify-engineers-raise-fresh-financing-to-scale-turbopuffers-ai-search/)

---

## まとめ表

| 項目 | 値 |
|---|---|
| 提供元 / ライセンス | Turbopuffer Inc. / プロプライエタリ（クローズドソース） |
| 位置付け | サーバーレス型ベクトル・全文検索エンジン（マネージドサービスのみ） |
| 対応インデックス種類 | SPFresh（センtroid ベース ANN）・BM25・属性インバーテッドインデックス・トライグラムインデックス |
| 最大次元数 | **10,752**（float32/float16、型ごとの差異は非公開） |
| 量子化対応 | **RaBitQ バイナリ量子化**（ANN v3、16–32x 圧縮）。スカラー量子化は最大 4x。PQ は記載なし |
| シャーディング / レプリケーション | 自動（オブジェクトストレージをソースとする任意ノードからの提供）。明示的シャーディング設定は不要 |
| コンピュート/ストレージ分離 | **完全分離**（オブジェクトストレージが Source of Truth） |
| 公称最大データ規模 | 1 NS あたり **500M ドキュメント / 2TB**。クロスネームスペース合計 **100B+ / 10TB** |
| 公式ベンチマーク (QPS / Recall) | 1,000+ QPS（本番）、p99=200ms @ 1,000億ベクトル、Recall@10=90–100% |
| フィルタ付き検索 | あり（インバーテッドインデックス型。Eq/Gt/Glob/Regex 等多数） |
| ハイブリッド検索 (BM25+Vector) | **あり**（クライアント側で融合ロジックを実装する設計） |
| SPLADE / 学習型スパース対応 | **未対応**（ロードマップに掲載） |
| Late Interaction (ColBERT 等) 対応 | **未対応**（ロードマップに掲載） |
| Cross-Encoder リランカー対応 | **組み込みなし**（Cohere/Voyage 等の外部サービス連携推奨） |
| リコメンド API / 機能 | **なし**（汎用 kNN クエリで代替） |
| 提供形態 (OSS / Managed / Enterprise) | マネージドのみ（Enterprise プランで BYOC オプションあり・交渉ベース） |
| SLA / コンプライアンス | SLA 99.95%（Enterprise）、SOC 2 Type 2・HIPAA BAA・GDPR・CCPA |
| 価格モデル | 従量課金＋最低スペンド（Launch: $64/月、Scale: $256/月、Enterprise: $4,096/月〜） |
| デプロイ手段 | マネージド API のみ（AWS/GCP/Azure バックエンド） |
| マルチテナンシー | **無制限ネームスペース**（1 ネームスペース = 1 テナントを推奨） |
| 可観測性 | 監査ログ（SIEM 連携ベータ）・ダッシュボード。Prometheus/OpenTelemetry の記載は公式ドキュメントに見当たらず |
| バックアップ / リストア | オブジェクトストレージが永続ストア（Backups ページあり、詳細は要確認） |
| 特徴的な機能 | ネームスペースピニング（高 QPS 向け）・Recall API（ユーザーデータでの正確性検証）・キャッシュウォームアップ API・Regex/Trigram インデックス |
| 距離メトリクス | cosine・euclidean・dotproduct |
| 1 ネームスペースあたりのベクトル列数 | 最大 **2 列**（2026 年 3 月対応） |
| 書き込み速度制限 | 1 ネームスペースあたり 1 WAL エントリ/秒（10k writes/s @ 32MB/s） |
