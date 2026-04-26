# Vespa ベクトルデータベース調査レポート

**製品/サービス**: Vespa（OSS版 / Vespa Cloud マネージドサービス）
**開発元/提供元**: Vespa.ai（Yahoo から独立、ノルウェー AI 企業）
**公式URL**: https://vespa.ai/ / https://docs.vespa.ai/
**ライセンス**: Apache License 2.0（OSS 版）
**調査時点**: 2026-04

---

## 1. 市場ポジション

### 市場での位置づけ

Vespa は「AI 検索プラットフォーム」として位置付けられており、純粋なベクトルデータベースではなく、**ベクトル検索・全文検索（BM25）・機械学習ランキングを単一エンジンで統合した大規模検索プラットフォーム**という独自の立ち位置を占める。もともと Yahoo の社内システムとして 10 年以上の本番運用実績を持ち、2021 年に独立した企業として分社化。

### 規模感・収益

- 2025 年時点の年間売上: **$6.3M**（57 名規模）
- VC 資金調達の有無: 記載なし（ブートストラップ寄りの運営模様）

### アナリスト評価

| レポート | 評価 |
|---|---|
| GigaOm Radar for Vector Databases v3（2025 年 11 月）| **Leader & Outperformer**（17 製品中） |
| GigaOm Sonar for Vector Databases（2024 年）| **Leader & Forward Mover**（2 年連続） |
| GigaOm Sonar（2023 年）| Leader |

GigaOm はランキング統合・マルチモーダル AI 検索の能力を高く評価しており、3 年連続でリーダー認定を受けている。

### 主要採用企業と規模感

| 企業 | ユースケース | 規模 |
|---|---|---|
| Yahoo | 大規模パーソナライゼーション | 約 150 アプリ、10 億ユーザー、80 万 QPS |
| Perplexity | RAG / AI 検索エンジン | 週 1 億クエリ以上（2025 年 5 月時点で 2,200 万アクティブユーザー） |
| Spotify | ポッドキャスト・音声検索 | 記載なし |
| Vinted | eコマース推薦 | 記載なし |
| Qwant | プライバシー重視検索エンジン | 記載なし |
| Elicit | 科学論文検索 | 記載なし |
| RavenPack | 金融データ大規模ベクトル検索 | 記載なし |

### 競合との関係

- **Elasticsearch / OpenSearch**: 最大の競合。Lucene ベースのレガシー検索スタック。Vespa は「Elasticsearch より低レイテンシ・低インフラコスト」を主張し、公式ベンチマーク比較資料（vs Elasticsearch）を公開している。
- **Milvus / Qdrant / Weaviate**: 専用ベクトル DB との比較では「単機能 DB vs 統合プラットフォーム」という訴求で差別化。
- **Marqo**: Vespa をバックエンドに採用（Marqo chooses Vespa）しており、Vespa をインフラとして選ぶプロダクトも存在する。

---

## 2. 開発元のアピールポイント

### 統合プラットフォームとしての設計思想

Vespa の最大の差別化ポイントは「**検索・ランキング・ML 推論を単一エンジンで提供する**」点にある。従来の検索スタックは検索エンジン + ML 推論サーバを別々に維持するが、Vespa はコンテンツノード上でランキング推論（ONNX モデル実行含む）を直接行う。これにより：

- ネットワーク往復レイテンシを排除
- データとコンピュートの共存（Data-locality）による低レイテンシ
- スケールアップ時の一貫したサブ 100ms レスポンス

### テンソルネイティブアーキテクチャ

Vespa のデータモデルはスカラー・ベクトル・行列・任意次元テンソルを統一的に扱える。これにより：

- Dense vector（float, bfloat16, int8）
- Sparse vector（SPLADE 等の学習型スパース表現）
- Multi-vector（ColBERT 等の Late Interaction）
- 多次元テンソル

を単一スキーマで定義でき、専用フィールド型の切り替えや追加システム不要。

### マルチモーダル・ハイブリッド検索

単一クエリでベクトル＋テキスト（BM25/WAND）＋構造化フィルタを組み合わせた検索が可能。`nearestNeighbor()` + `weakAnd()` + フィルタ条件を `rank()` 演算子で統合する柔軟なクエリ言語を持つ。

### 大規模実績

- 10 年以上の Yahoo 本番運用履歴
- 毎秒 80 万クエリ（Yahoo 実績）
- 10 億件ベクトルのサービング実績

### ストリーミング検索モード（低コスト個人検索）

インデックスを作成せず、生データのみをディスクに圧縮保存する「**ストリーミング検索**」モードを提供。通常インデックスの約 **1/20 のコスト（メモリ 15% 程度）** で、個人データ・プライベート検索などのマルチテナント用途に最適。ドキュメントあたり 45 バイトのメモリで動作し、1 ノードで数十億ドキュメントを格納可能。

### 価格競争力（Matryoshka + Binary 量子化の例）

Vespa Cloud のメモリ料金 $0.01/GB/h をベースに：

- 10 億 × 1024 次元 float32: 3,814 GB → **$38.14/h**
- Matryoshka + Binary 量子化（64 次元 int8）: 60 GB → **$0.59/h**（約 98% 削減）

---

## 3. 市場・調査会社が評価している強み

### GigaOm（2025 年 Radar v3）の評価

- 複雑なデータ構造を大規模にリアルタイム処理する能力
- ネイティブテンソルサポートとスパース/デンスベクトル間の効率的な検索
- 統合ランキングパイプラインによるリアルタイム高関連性回答

### サードパーティが評価する強み

**1. 統合されたハイブリッド検索**
- BM25、学習型スパース（SPLADE）、Dense ベクトル、構造化フィルタを単一システムで処理
- `weakAnd()` + `wand()` による効率的なスパース Top-k 検索（動的枝刈り WAND アルゴリズム）
- 複数システムを組み合わせる必要がなく、運用複雑度が低い

**2. 大規模ランキング推論能力**
- コンテンツノードで ONNX モデルをランキング時にインライン実行
- 多段階ランキング（First-phase → Second-phase → Global-phase）のネイティブサポート
- GPU 推論にも対応（Vespa Cloud、`gpu-device` パラメータで設定）

**3. 実証済みスケーラビリティ**
- Yahoo: 80 万 QPS、10 億ユーザー規模の実績
- Perplexity: 週 1 億クエリの RAG ワークロード

**4. ColBERT / Late Interaction のネイティブサポート**
- Vespa 独自の ColBERT 埋め込み器（ColBERT embedder）を内蔵
- **32 倍圧縮**の非対称二値化スキームにより、ColBERT のストレージコストを大幅削減
- MaxSim スコアリングをネイティブ実装

**5. SPLADE / 学習型スパース のネイティブサポート（Vespa 8.321 以降）**
- `splade-embedder` 内蔵
- `wand()` 演算子による効率的なスパース Top-k 検索アクセラレーション

**6. 一貫性のある低レイテンシ**
- 50M ベクトルのあるベンチマークで Vespa が P50 16ms vs Milvus 140ms という比較報告あり（第三者 Medium 記事、方法論は未検証）
- 1M SIFT データセットでの Vespa HNSW は Annoy の 9 倍・RPLSH の 16 倍の QPS

**7. リアルタイムインデックス更新**
- 書き込みが即時に検索可能な状態となるリアルタイムインデックス更新

---

## 4. 市場・調査会社が指摘している弱点・批判点

### 急峻な学習曲線

- 独自のスキーマ言語・クエリ言語・グルーピング言語・テンソルフレームワークが存在し、**習得に数ヶ月かかる**との報告がある
- Qdrant や Weaviate のようなシンプルな REST API と比較して、初期セットアップのハードルが高い
- 「大規模スケーラブルなデプロイでは多くのチューニングパラメータがあり、習熟に時間がかかる」（ユーザーレビュー）

### ドキュメントとエラー体験

- ドキュメントは広範だが「構成とコンテキスト例が不足している箇所がある」との批判
- エラーメッセージが分かりにくい場合がある
- 「ドキュメントが改善されつつある」との言及もあり、改善進行中

### インフラ要件の重さ

- 分散アーキテクチャは大規模デプロイ向けに設計されており、**小規模ユースケースでも相応のリソースが必要**
- 小中規模アプリケーションには過剰な複雑性をもたらす可能性がある
- スタンドアロン設定でも複数の Java プロセスが起動するため、開発時のリソース消費が大きい

### 拡張性の制限

- **ネイティブ拡張は Java のみ**対応。Java ツールチェーンを持たないチームには障壁となる（Feedしたユーザーの証言）
- BigQuery からのデータ取り込みは「想定より困難だった」との報告

### 強い一貫性の欠如

- CAP 定理上は **AP（可用性優先）**として分類され、強一貫性（linearizability）は保証しない
- 検索時に部分的に更新されたドキュメントを観測する可能性がある（Get/Visit 操作は原子性保証あり）

### コミュニティ規模

- Milvus・Qdrant 等と比較して GitHub スター数・コミュニティ規模は小さい
- サードパーティのチュートリアル・記事の量が少ない

### ストリーミングモードの制限

- ストリーミング検索モードでは **HNSW（ANN）使用不可**（常に完全探索）
- 親子関係スキーマ・述語フィールド・ステミング 非対応

---

## 5. ベンチマーク・競合比較・その他

### 公式ベンチマーク（Vespa 発表）

**10 億スケール HNSW（ブログ記事: billion-scale-knn-part-two）**
- データセット: 10 億ベクトル（内部データセット）
- ハードウェア: コンテンツノード 256GB メモリ / 72 vCPU / 1TB 高速ディスク
- HNSW パラメータ: max-links=16、neighbors-to-explore=96
- レイテンシ: **4ms**（Brute Force 15,000ms の約 3,750 倍高速化）
- Recall@10: **90%**
- スループット: 単一コア 約 250 QPS、72 コアフル使用 約 **18,000 QPS**
- メモリ: HNSW なし 64GB → HNSW あり 約 90GB

**Matryoshka + Binary 量子化（ブログ記事: combining-matryoshka-with-binary-quantization）**
- バイナリ量子化（ハミング距離）: float32 比 **約 20 倍高速（2ms）**
- スループット: 10,000 QPS（100,000 ベクトル）、秒間 約 10 億ハミング距離計算
- MTEB 検索タスク: 90% 精度維持（再ランキング戦略込み）

**1M SIFT データセット（ブログ記事: approximate-nearest-neighbor-search-in-vespa-part-1）**
- Vespa HNSW vs Annoy: **9 倍高速 QPS**
- Vespa HNSW vs RPLSH: **16 倍高速 QPS**
- HNSW インデックスサイズ: 134MB（Annoy 387MB の約 35%）

**Vespa vs Elasticsearch（公式ベンチマーク比較）**
- 100 万商品の eコマース検索アプリケーションで比較
- スループット・レイテンシ・インフラコストの三指標で比較（詳細は PDF ダウンロード）
- 具体数値は PDF 内のため未取得

### 第三者ベンチマーク

| ソース | 内容 |
|---|---|
| Medium 記事（第三者、方法論不明） | 50M ベクトルで Vespa P50 16ms vs Milvus 140ms |
| datastores.ai / ann-benchmarks | Vespa 向けの ann-benchmarks 結果は限定的。Vespa 自身が `vespa-ann-benchmark` ライブラリを GitHub で公開 |
| GigaOm Radar v3 | 17 製品中で Leader & Outperformer |

※ vectordbbench.com（Zilliz 運営）での Vespa の公式掲載は確認できず。独立したベンチマークエビデンスは公式ブログ記事が中心。

### 競合比較まとめ

| 比較軸 | Vespa の優位 | Vespa の劣位 |
|---|---|---|
| vs Elasticsearch | ランキング推論能力、リアルタイム更新、低レイテンシ | 既存 Elasticsearch 資産の移行コスト |
| vs Milvus | 統合ハイブリッド検索、ColBERT/SPLADE ネイティブ対応 | クラウドネイティブアーキテクチャ（コンピュート/ストレージ分離）は Milvus が先行 |
| vs Qdrant | 大規模本番実績、ML ランキング統合、スパース検索の成熟度 | API のシンプルさ・学習コスト、Rust 実装のメモリ効率 |
| vs Weaviate | 実績規模、テンソルネイティブ柔軟性 | エコシステム・サードパーティ連携の豊富さ |

---

## プロダクト概要

- **位置付け**: AI 検索プラットフォーム（専用ベクトル DB + 全文検索エンジン + ML ランキングエンジンの統合）
- **代表的なユースケース**: RAG、eコマース検索、ニュース/コンテンツ推薦、パーソナライゼーション、プライベート検索、マルチテナント個人データ検索
- **直近のメジャーバージョン**: 毎週 Mon-Thu に新リリース（ローリングリリースモデル）

---

## サポートしているインデックスの種類

- **対応インデックス**: **HNSW のみ**（ANN）+ Brute-force（完全探索）
  - IVF、DiskANN、SCANN、Annoy 等は非対応（HNSW に一本化）
  - ストリーミングモードでは HNSW 不使用（常に完全探索）
- **チューニングパラメータ**:
  - `max-links-per-node`（ノードあたり最大リンク数、HNSW の M 相当）
  - `neighbors-to-explore-at-insert`（efConstruction 相当）
  - クエリ時: `hnsw.exploreAdditionalHits`（探索追加ノード数、ef 相当）
  - `targetHits`、`totalTargetHits`（ヒット数制御）
- **距離メトリック**: `angular`、`prenormalized-angular`、`euclidean`、`dotproduct` 等

---

## サポートしている最大次元数

- **記載なし**（公式ドキュメントに明示的な上限値は記載されていない）
- テンソルセルタイプ（量子化精度）:
  - `double`: 8 bytes/value
  - `float`: 4 bytes/value（デフォルト）
  - `bfloat16`: 2 bytes/value
  - `int8`: 1 byte/value
  - バイナリ（1 bit/value）: int8 フィールドを利用したハミング距離計算で実現

---

## サポートしている量子化技術

- **スカラー量子化（SQ int8）**: 対応。`int8` セルタイプでインデックス構築
- **bfloat16**: 対応（float32 の 50% メモリ削減）
- **バイナリ量子化**: 対応。int8 フィールドにパックしてハミング距離で検索 → 約 32 倍圧縮、float32 比約 20 倍高速
- **Matryoshka 表現学習（MRL）との組み合わせ**: 対応。MRL + BQ で最大 **98% メモリ削減**（10 億ベクトルで $38.14/h → $0.59/h）
- **PQ（積量子化）**: **記載なし**（未対応と推測）
- **RaBitQ**: **記載なし**
- **再ランキングによる精度回復**: バイナリ検索で候補取得後、float32 表現で再スコアリングし 95〜96% 精度を回復

---

## スケーラビリティ

- **シャーディング**: クエリはデータを保持するノードのサブセットに分散。コンテンツクラスタ内での自動パーティショニング
- **レプリケーション**: 複数ノード間でデータを複製。ノード障害時は自動修復。ノード喪失はサービスルーティングから自動除外
- **水平スケール**: ノード数変更はオンライン（ダウンタイムなし）で実施可能。**自動リバランシング**により設定冗長性を維持
- **最大データ規模**: Yahoo 実績で 10 億ユーザー規模・80 万 QPS。ストリーミングモードで 1 ノード数十億ドキュメント可能
- **コンピュート/ストレージ分離**: **非分離アーキテクチャ**（Milvus のような計算/ストレージ分離ではない）。コンテンツノードが計算とストレージを担当
- **アーキテクチャ構成**: ステートレスコンテナクラスタ（クエリ処理・データ操作）+ コンテンツクラスタ（データ保存・インデックス）+ 設定クラスタ（ZooKeeper 使用）

---

## パフォーマンス（QPS / Recall / レイテンシ）

- **公式ベンチマーク**（10 億スケール HNSW）:
  - データ: 10 億ベクトル、256GB/72vCPU ノード
  - HNSW: 4ms レイテンシ、Recall@10 90%、72 コアで約 18,000 QPS
  - Binary 量子化: 2ms、10,000 QPS（100K ベクトル）
- **第三者ベンチマーク**:
  - ann-benchmarks.com への正式掲載は限定的
  - 内部 Python バインディング（`vespa-ann-benchmark`）は GitHub 公開
  - Vespa HNSW は 1M SIFT で Annoy の 9 倍 QPS（ブログ記事より、条件: Annoy との比較）
- **ハイブリッド検索（BM25 + Vector）**: `weakAnd()` + `nearestNeighbor()` を `rank()` 演算子で統合。WAND アルゴリズムによるスパース Top-k 高速化
- **注意点**: 公式ベンチマークはほぼ自社測定。方法論・ハードウェア条件が異なるため他製品との直接比較には注意が必要

---

## 商用サポート

- **提供形態**:
  - OSS 版（Apache 2.0）: セルフホスト（Docker / Kubernetes）
  - **Vespa Cloud**: マネージドサービス（AWS / GCP）
  - エンタープライズオンプレは明示的な記載なし（営業対応）
- **価格モデル**: 従量制（Vespa Cloud）。メモリ $0.01/GB/h 等の細かい料金体系。Free Trial 提供あり。詳細は営業問い合わせ（Contact Sales）
- **SLA**: 記載なし（Vespa Cloud のドキュメントに明示的な SLA 数値なし）
- **サポート窓口**: コミュニティ（GitHub Issues、Slack）、Vespa Cloud サポート（詳細不明）
- **認証/コンプライアンス**: 記載なし
- **エンタープライズ採用事例**: Yahoo、Perplexity、Spotify 等の大手企業での実績

---

## デプロイ・運用面の優位点

- **デプロイ手段**: Docker、Kubernetes（StatefulSet）、Vespa Cloud（マネージド）。公式 Docker Image (`vespaengine/vespa`) 提供
- **マルチテナンシー**: ドキュメント ID のグループ値（`id:namespace:type:g=userId:localId`）でテナント分離。ストリーミングモードで低コスト多テナント運用
- **可観測性**: Prometheus API（`/prometheus/v1`）、メトリクスエンドポイント提供。専用ダッシュボードについては記載なし
- **バックアップ・リストア**: 「Data management and backup」ページが存在（詳細は未取得）
- **データ取り込み**: HTTP REST API、ドキュメント API。BigQuery 連携は設定が複雑との報告あり
- **アップグレード**: ローリング更新（ダウンタイムなし）。Mon-Thu の毎朝 CET に新リリースが master から自動ビルド
- **運用上の注意点**: 設定管理が ZooKeeper ベースで複雑。ネイティブ拡張は Java のみ対応

---

## 学習型スパース（SPLADE）のサポート

- **対応あり**（Vespa 8.321 以降）
- 専用の `splade-embedder` を内蔵。スパースベクトルフィールドとして格納
- `wand()` 演算子（動的枝刈り WAND アルゴリズム）によるスパース Top-k 検索アクセラレーション
- クエリ側推論: Vespa 内部でクエリ時に SPLADE モデルを実行可能（ONNX モデルとして組み込み）
- BM25 との違い: SPLADE は語彙拡張（クエリ/ドキュメントの拡張表現）を学習し、語彙不一致問題を緩和

---

## Late Interaction（ColBERT / ColPali 等）のサポート

- **対応あり**（ネイティブ ColBERT 埋め込み器内蔵）
- **表現方式**: 混合テンソル `tensor<cell-type>(dt{},x[dim])` でマルチベクトルを格納。`dt{}` がマップ次元で可変長パッセージに対応
- **MaxSim スコアリング**: ネイティブ実装
- **32 倍圧縮**: 非対称二値化スキームによりドキュメント側トークンベクトルを int8 圧縮（クエリ側は完全精度維持）
- **ColPali（マルチモーダル）**: マルチベクトル埋め込みとして対応可能（サンプルアプリあり）
- **ストレージ肥大化への対応**: 32 倍圧縮技術で従来の ColBERT ストレージコストを大幅削減

---

## リランキング（Cross-Encoder 等）のサポート

- **対応あり**（ネイティブ多段階ランキング）
- **統合方式**:
  - First-phase: コンテンツノード上での第 1 段階ランキング
  - Second-phase: コンテンツノード上での第 2 段階ランキング（`rerank-count` で対象件数制限）
  - Global-phase: コンテナノードでのグローバルランキング（デフォルト 100 件を再ランク）
- **対応モデル**: HuggingFace の任意 Cross-Encoder を ONNX 形式でエクスポートして組み込み可能（Optimum ライブラリ推奨）。Mixedbread.ai の cross-encoder サンプルあり
- **GPU 推論**: Vespa Cloud で GPU デバイス利用可能（`gpu-device` パラメータ）。30〜40M パラメータ以上のモデルでは GPU 推奨
- **ONNX モデル制限**: 2GB 以下の自己完結型 ONNX モデルのみサポート
- **対応フレームワーク**: TensorFlow、PyTorch、XGBoost、LightGBM（ONNX 経由）

---

## リコメンド用途の機能

- **ユーザー/アイテム ID 指定検索**: ユーザー埋め込みベクトルをクエリパラメータとして渡し、`nearestNeighbor()` で最近傍アイテムを検索（Qdrant の `recommend` API 相当の専用エンドポイントは非存在）
- **実装方式**: ニュース推薦チュートリアルではユーザー/アイテム双方にテンソルフィールドを定義し、ユーザー埋め込みを HNSW 検索クエリとして使用
- **フィルタリング統合**: ANN 探索中のフィルタリング（カテゴリ指定等）が可能
- **1st-class Recommend API**: 専用のレコメンデーション API は持たない（汎用 nearestNeighbor 演算子で代用）
- **MMR / 多様性サンプリング**: 記載なし
- **実績**: Spotify（ポッドキャスト推薦）、Vinted（eコマース推薦）、Yahoo（大規模パーソナライゼーション）

---

## その他の優位点

- **テンソルフレームワーク内蔵**: スカラー/ベクトル/行列/任意次元テンソルを統一モデルで処理。ランキング式内で任意のテンソル計算が可能
- **ML ランキングの本番統合**: XGBoost、LightGBM、TensorFlow、PyTorch モデルをランキングに直接組み込み可能
- **WAND アルゴリズム**: スパース検索の効率的な動的枝刈りにより、大規模スパースインデックスでも高速 Top-k 検索
- **ストリーミング検索**: 通常インデックスの 1/20 コストで個人データ検索を実現する独自機能
- **Apache 2.0 ライセンス**: 商用利用・ホスティングに制限なし（BSL / SSPL ではない）
- **10 年以上の本番実績**: Yahoo 社内システムとして洗練されたアーキテクチャ

---

## 競合プロダクトとの比較メモ

- **vs Elasticsearch**: ランキング推論・リアルタイム更新・低インフラコストで優位。学習コストと移行コストの高さが障壁。
- **vs Milvus**: ハイブリッド検索・ColBERT/SPLADE 成熟度・ML ランキング統合で優位。コンピュート/ストレージ分離アーキテクチャと Kubernetes ネイティブな運用性では Milvus が先行。
- **vs Qdrant**: 実績規模・ML ランキング統合・スパース検索の完成度で優位。API シンプルさ・学習コストの低さ・Rust 実装のメモリ効率では Qdrant が有利。

---

## まとめ表

| 項目 | 値 |
|---|---|
| 提供元 / ライセンス | Vespa.ai（旧 Yahoo）/ Apache 2.0 |
| 位置付け | AI 検索プラットフォーム（ベクトル + 全文 + ML ランキング統合） |
| 対応インデックス種類 | HNSW（ANN）、Brute-force（完全探索）のみ。IVF / DiskANN 等は非対応 |
| 最大次元数 | 記載なし（公式ドキュメントに明示なし） |
| 量子化対応（SQ / PQ / Binary 等） | SQ（int8, bfloat16）: 対応。Binary: 対応（32x 圧縮）。Matryoshka + BQ: 対応（98% 削減）。PQ / RaBitQ: 記載なし |
| シャーディング / レプリケーション | 自動シャーディング（コンテンツクラスタ内）、自動レプリケーション・リバランシング |
| コンピュート/ストレージ分離 | 非分離（コンテンツノードが計算+ストレージを担当） |
| 公称最大データ規模 | 10 億ベクトル以上（Yahoo 実績: 10 億ユーザー規模、ストリーミングモードで 1 ノード数十億ドキュメント） |
| 公式ベンチマーク（QPS / Recall） | 10B ベクトル: 72 コアで 18,000 QPS、Recall@10 90%、4ms レイテンシ |
| フィルタ付き検索 | 対応（ANN 探索中のフィルタリング統合） |
| ハイブリッド検索（BM25 + Vector） | ネイティブ対応（weakAnd + nearestNeighbor + rank 演算子） |
| SPLADE / 学習型スパース対応 | ネイティブ対応（v8.321 以降、splade-embedder 内蔵、wand() 演算子で高速化） |
| Late Interaction（ColBERT 等）対応 | ネイティブ対応（ColBERT embedder 内蔵、32x 圧縮、MaxSim スコアリング） |
| Cross-Encoder リランカー対応 | 対応（ONNX モデル、多段階ランキング、GPU 推論。2GB 以下のモデル制限あり） |
| リコメンド API / 機能 | 専用 API なし。nearestNeighbor 演算子で代用。Spotify / Vinted 実績あり |
| 提供形態（OSS / Managed / Enterprise） | OSS（Apache 2.0）+ Vespa Cloud（マネージド） |
| SLA / コンプライアンス | SLA 数値記載なし。コンプライアンス認証は不明 |
| 価格モデル | 従量制（Vespa Cloud）。Free Trial あり。詳細は営業問い合わせ |
| デプロイ手段 | Docker、Kubernetes（StatefulSet）、Vespa Cloud |
| マルチテナンシー | ドキュメント ID グループ値による分離。ストリーミングモードで低コスト多テナント |
| 可観測性 | Prometheus API（/prometheus/v1）対応 |
| バックアップ / リストア | Data management and backup 機能あり（詳細未取得） |
| 特徴的な機能 | ストリーミング検索（1/20 コスト個人検索）、テンソルネイティブランキング、WAND アルゴリズム、10 年以上の Yahoo 本番実績、GigaOm 3 年連続 Leader |

---

## 6. 参考 URL

- [Vespa 公式サイト](https://vespa.ai/)
- [Vespa ドキュメント](https://docs.vespa.ai/)
- [HNSW インデックスドキュメント](https://docs.vespa.ai/en/querying/approximate-nn-hnsw.html)
- [Cross-Encoder ランキングドキュメント](https://docs.vespa.ai/en/ranking/cross-encoders.html)
- [ONNX モデルランキングドキュメント](https://docs.vespa.ai/en/ranking/onnx.html)
- [ストリーミング検索ドキュメント](https://docs.vespa.ai/en/performance/streaming-search.html)
- [一貫性モデルドキュメント](https://docs.vespa.ai/en/content/consistency.html)
- [ColBERT Embedder ブログ](https://blog.vespa.ai/announcing-colbert-embedder-in-vespa/)
- [Matryoshka + Binary 量子化ブログ](https://blog.vespa.ai/combining-matryoshka-with-binary-quantization-using-embedder/)
- [10 億スケール HNSW ベンチマークブログ（Part 2）](https://blog.vespa.ai/billion-scale-knn-part-two/)
- [ハイブリッド検索解説ブログ](https://blog.vespa.ai/redefining-hybrid-search-possibilities-with-vespa/)
- [ストリーミング検索発表ブログ](https://blog.vespa.ai/announcing-vector-streaming-search/)
- [Vespa ケーススタディ一覧](https://vespa.ai/case-studies/)
- [GigaOm Radar v3 Leader 発表](https://vespa.ai/gigaom-radar-for-vector-databases-v3-positions-vespa-ai-as-a-leader-and-outperformer/)
- [GigaOm Sonar 2024 Leader 発表](https://vespa.ai/gigaom-sonar-for-vector-databases-positions-vespa-as-a-leader-and-forward-mover-for-the-second-consecutive-year/)
- [Perplexity 採用事例](https://vespa.ai/perplexity/)
- [vespa-ann-benchmark GitHub](https://github.com/vespa-engine/vespa-ann-benchmark)
- [Vespa GitHub](https://github.com/vespa-engine/vespa)
- [Vespa Docker Hub](https://hub.docker.com/r/vespaengine/vespa/)
- [Kubernetes デプロイドキュメント](https://docs.vespa.ai/en/operations/self-managed/using-kubernetes-with-vespa.html)
- [Getlatka Vespa.ai 収益情報](https://getlatka.com/companies/vespa.ai)
- [GigaOm Radar v3 ニュース（BusinessWire）](https://www.businesswire.com/news/home/20251120444017/en/GigaOm-Radar-for-Vector-Databases-v3-Positions-Vespa.ai-as-a-Leader-and-Outperformer)
