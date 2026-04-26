# Marqo 市場調査レポート

**製品/サービス**: Marqo（OSS版 / Marqo Cloud / エンタープライズ向けエコマース検索プラットフォーム）
**開発元/提供元**: Marqo（オーストラリア発・本社サンフランシスコ移転済み）
**公式URL**: https://www.marqo.ai / https://docs.marqo.ai
**ライセンス**: Apache-2.0（OSS版・現在は廃止）
**調査時点**: 2026-04

---

## 1. 市場ポジション

### 1-1. 全体的な位置づけ

Marqoはもともと「エンドツーエンドのベクトル検索エンジン」としてOSSで登場した製品だが、現在は**AIネイティブなエコマース検索・プロダクトディスカバリープラットフォーム**へと大きくピボットしている。

- **創業**: 2022年、元Amazon社員のTom Hamer（CEO）とJesse Clark（元Amazon Robotics AI リードサイエンティスト、元StitchFix主席科学者）がメルボルンで創業
- **本社**: 現在はサンフランシスコ
- **主要投資家**: Lightspeed Venture Partners（Series A リード）、Blackbird Ventures（シード）、Cohere共同創業者Ivan Zhang・Aidan Gomezが参加

### 1-2. 資金調達状況

| ラウンド | 時期 | 金額 | リード投資家 |
|---|---|---|---|
| Pre-seed | 2022年 | $840K | - |
| Seed | 2023年8月 | $5.2M | Blackbird |
| Series A | 2024年2月 | $12.5M | Lightspeed Venture Partners |
| **合計** | | **約$18.4M** | |

### 1-3. 市場における競合関係

- **主要競合**: Pinecone、Weaviate、Milvus、Qdrant、Vespa（現在のバックエンド）、エコマース特化ではSearchHub.io等
- **TechCrunchによる文脈**: Pineconeが$100M、Weaviateが$50Mを調達する中で、Marqoはより小規模ながらエコマース特化のニッチを確立
- **市場シェア**: 公開情報なし。G2での評価は「Marqo Cloud」として掲載されているが、レビュー数は限定的
- **OSS廃止による立場変化**: GitHubのOSSリポジトリには「Marqo's Open Source project is deprecated and will no longer receive updates」と明記されており、クローズドなクラウドサービスへの移行が完了している

### 1-4. 主な採用事例

| 顧客 | 成果指標 |
|---|---|
| Redbubble | $9.3M増収、検索収益+3.85%、add-to-cart+30% |
| Mejuri | 検索収益+19.8% |
| KICKS CREW | コンバージョン+17.7% |
| Temple & Webster | サインアップから本番投入まで5日 |
| $11M revenue growth（詳細非公開） | 別顧客の事例 |

---

## 2. 開発元のアピールポイント

### 2-1. コアコンセプト: エンドツーエンドのベクトル検索

Marqoの最大の差別化訴求は「**ベクトル化・ストレージ・検索を単一APIで提供するall-in-oneアプローチ**」である（旧OSS時代の中核メッセージ）。

- ユーザーは埋め込みモデルを別途調達・管理する必要がない
- ドキュメントを入力すると自動的にベクトル化・インデックス化される
- 検索はプレーンテキストまたは画像URLを渡すだけで結果が返る

### 2-2. マルチモーダル検索能力

- テキスト・画像・音声・動画を統合した検索システム
- text-to-image、image-to-image、image-to-text検索をネイティブサポート
- 独自のマルチモーダル組み合わせフィールドでテキストと画像を1フィールドにまとめて横断スコアリング可能

### 2-3. エコマース特化の独自埋め込みモデル

Marqoは自社のエコマース向け埋め込みモデルを開発・公開しており、これが最大の技術的差別化ポイントとして訴求されている。

**Marqo-Ecommerce-B**（Apache-2.0で公開）:
- 次元数: 768
- 推論時間: テキスト5.1ms、画像5.7ms

**Marqo-Ecommerce-L**（Apache-2.0で公開）:
- 次元数: 1024
- パラメータ数: 652M
- Amazon Titan Multimodal Embeddingより**最大88%向上**
- ViT-SO400M-14-SigLIP（最良OSSモデル）より**最大31%向上**（MRR +17.6%、nDCG@10 +20.5%）

ファッション特化モデルも提供:
- **Marqo-FashionCLIP**: text-to-image検索で既存モデル比+57%
- **Marqo-FashionSigLIP**: category-to-product検索で+11%

### 2-4. Vespaバックエンド（V2以降）の性能優位性

V2でバックエンドをOpenSearchからVespaに移行した（Marqo社のエンジニアリングブログ参照）。Vespaを選定する際に評価した競合:

- Milvus、OpenSearch、Weaviate、Redis、Qdrant を比較
- **50Mベクトルでの比較**: VespaのP50レイテンシ 16ms vs Milvus 140ms（同等インフラコスト）

**V1→V2の性能改善（10M DBPedia文書、768次元）**:

| 指標 | V1 | V2 | 改善率 |
|---|---|---|---|
| Recall@10 | 0.81 | 0.97 | +20% |
| Recall 標準偏差 | 0.16 | 0.05 | -69% |
| QPS | 147.8 | 157.7 | +6.7% |
| 平均レイテンシ | 171.98ms | 72.11ms | -58% |
| P50レイテンシ | 170ms | 70ms | -59% |
| P99レイテンシ | 250ms | 140ms | -44% |
| フィルタ付き検索レイテンシ | - | - | -60〜65% |

### 2-5. エコマース向け製品機能

現在のMarqoはベクトルDBというよりエコマースSaaSとして以下を提供:

1. **Product Search**: セマンティック理解によるオンサイト検索
2. **Merchandising**: マルチモーダルコンテンツマッチング
3. **Smart Category & Listing Pages**: AIチャットボット・エージェントによるプロダクトディスカバリー
4. **Recommendations**: 類似商品・補完商品APIによるパーソナライズドレコメンド
5. **Generative AI Shopping**: エージェント型プロダクトディスカバリー体験

### 2-6. インテグレーション

- **ECプラットフォーム**: Shopify、Adobe Commerce、Salesforce Commerce Cloud（ワンクリック統合）
- **MAツール**: Klaviyo連携（レコメンド結果のメール・SMS配信自動化）
- **LLMフレームワーク**: LangChain、Haystack、Griptapeとの統合（旧OSS時代）
- **AWS Marketplace**: 出品済み

---

## 3. 市場・調査会社が評価している強み

### 3-1. 第三者レビューサイト・比較記事での評価

**Firecrawl / Best Vector Databases 2026**:
- マルチモーダルAIに特化した目的特化型データベースとして評価
- 独自エコマースモデルがAmazon Titan Multimodal Embeddingを最大88%上回る点を評価
- ただし「newer/less proven」として成熟度の限界を指摘

**Simplyblock / Glossary**:
- ゼロ設定での埋め込み生成をネイティブML統合の優位点として評価
- Kubernetes対応のコンテナデプロイ（Helmチャート）を評価

**Hacker News コミュニティ（Show HN投稿への反応）**:
- 70Mベクトル768次元で100ms未満というパフォーマンス指標に対して具体的なフィードバックが行われた
- チームの技術的なフィードバックへの対応力を評価するコメントあり

### 3-2. 技術的な強みとして評価される点

- **迅速な導入**: 数行のコードで検索開始（Temple & Websterは5日でサインアップから本番稼働）
- **スケーラビリティ**: 水平シャーディングにより数億ドキュメントのインデックスに対応
- **ハイブリッド検索**: セマンティック検索 + 字句検索の組み合わせをネイティブサポート
- **構造化/非構造化インデックスの2択**: プロトタイプ向けの柔軟なスキーマレスと本番向けの高性能スキーマ定義を選べる設計
- **リコメンドAPI**: 類似商品（similar）・補完商品（complementary）の専用エンドポイントをネイティブ提供

---

## 4. 市場・調査会社が指摘している弱点・批判点

### 4-1. OSSの廃止という重大な問題

**最大の批判点**: GitHubリポジトリに「Marqo's Open Source project is deprecated and will no longer receive updates」と明記されている。

- セルフホストを希望するユーザーは事実上利用できなくなった
- ベンダーロックインのリスクが増大
- OSS時代に構築されたLangChain等との統合は今後メンテナンスされない可能性

### 4-2. 成熟度・エコシステムの限界

第三者比較記事が一貫して指摘する弱点:

- Pinecone・Milvus・Weaviateと比べてエコシステムが小さい
- 第三者ベンチマーク（ann-benchmarks.com、VectorDBBench）への参加実績が乏しい
- 本番での採用事例は増加しているが、PineconeやWeaviateに比べると少ない

### 4-3. V1（OpenSearchバックエンド時代）の既知の問題

V2への移行で解消されているが、V1での問題として公式に認められている内容:

- 複数埋め込みサポートのためにドキュメントデータを重複格納する必要があり、メモリ・ディスク使用量が非効率だった
- 大量インデックス中・後にLuceneのセグメントマージによって予測不可能なパフォーマンス劣化が発生した
- リコール改善にHNSWのefSearch値を上げる必要があり、レイテンシとのトレードオフが避けられなかった

### 4-4. 非構造化インデックスの設計上の制約

Marqo公式ドキュメントが認める設計上のトレードオフ:

- 複数テンソルフィールドを持つ場合、非構造化インデックスはすべての埋め込みを**単一のHNSWグラフに混在させる**
- この設計はリコール精度とメモリ効率の両面で不利
- 本番環境では構造化インデックスが推奨されるが、フィールド定義をインデックス作成時に確定する必要がある

### 4-5. Hacker Newsコミュニティからの批判

- 「vectorless vector search」というマーケティング用語への違和感（ベクトル検索の専門家を疎外する可能性）
- ベンチマーク主張が次元数・ハードウェア・条件を明示しないと意味がないという技術的指摘
- ベクトル類似度検索はリトリーバル改善には有効だが、ランキング自体には限界があるという指摘

### 4-6. ポジション変更による混乱

- ベクトルDBとしての汎用ツール → エコマース特化SaaSへのピボットにより、汎用ベクトルDB用途でのユーザーが置き去りになっている
- 「Marqo Cloud」は既存顧客向けに引き続き提供されるとされているが、ロードマップはエコマース専用プラットフォームに集中している
- インフラ系ベクトルDBとしての競合比較（VectorDBBench等）には参加できていない状況

---

## 5. ベンチマーク・競合比較・その他

### 5-1. 公式ベンチマーク（V2、Marqo発表）

**テスト条件**:
- データセット: DBPedia 10Mドキュメント
- 次元数: 768（hf/e5-base-v2モデル）
- インフラ: 2xmarqo.performanceシャード、1レプリカ、5xmarqo.GPUノード
- クエリセット: 1,000ランダムクエリ（512トークンフルコンテキスト推論）
- Recall基準: 正確なkNN検索結果をグランドトゥルースとして使用

**結果**（V1→V2比較）:

| 指標 | V1 | V2 | 改善率 |
|---|---|---|---|
| Recall@10 | 0.81 | 0.97 | +20% |
| QPS | 147.8 | 157.7 | +6.7% |
| P50レイテンシ | 170ms | 70ms | -59% |
| P99レイテンシ | 250ms | 140ms | -44% |

**注意**: これはMarqo社自身が発表したベンチマークであり、独立した第三者機関による検証ではない。

### 5-2. バックエンド比較（Marqo社内評価、50Mベクトル）

| DB | P50レイテンシ |
|---|---|
| Vespa（V2採用） | 16ms |
| Milvus | 140ms |
| OpenSearch（V1） | ~140ms（同等とみなせる） |

### 5-3. 埋め込みモデルベンチマーク（独自モデル評価）

| 比較対象 | MRR改善 | nDCG@10改善 |
|---|---|---|
| ViT-SO400M-14-SigLIP vs Marqo-Ecommerce-L | +17.6% | +20.5% |
| Amazon Titan Multimodal vs Marqo-Ecommerce-L | +38.9% | +45.1% |

**注意**: 4Mプロダクトデータセットでの評価。Marqo社発表のベンチマーク。

### 5-4. 主要技術仕様まとめ

| 項目 | 仕様 |
|---|---|
| インデックスタイプ | HNSW（構造化/非構造化の2モード） |
| 最大次元数 | 4096次元（ほとんどの埋め込みモデルをカバー） |
| 距離メトリクス | euclidean, angular, dotproduct, prenormalized-angular, hamming |
| HNSWパラメータ | M (デフォルト16)、efConstruction (デフォルト512)、efSearch (デフォルト2000) |
| 量子化 | bfloat16（同メモリで約2倍のドキュメント格納可能、わずかなRecall低下あり） |
| ハイブリッド検索 | TENSOR + LEXICAL の組み合わせ（言語対応あり） |
| 検索方法 | TENSOR検索、LEXICAL検索、HYBRID検索 |
| フィルタ | Marqo Filter DSL（bool, int, keyword対応） |
| スコアモディファイア | 対応（フィールド値によるスコア調整） |
| 正確なkNN | approximate=false で利用可能 |

### 5-5. 競合プロダクトとの比較メモ

| 競合 | Marqoの優位点 | Marqoの劣位点 |
|---|---|---|
| **Pinecone** | エコマース特化モデルが強力、マルチモーダルネイティブ | フルマネージドの完成度・エンタープライズ実績・サポート体制 |
| **Weaviate** | エコマースドメイン特化の深さ、レコメンドAPI | ハイブリッド検索の成熟度・GraphQLの柔軟性・汎用性 |
| **Milvus** | セットアップ簡便性、エコマース向け統合 | スケール時のパフォーマンス（V2以降は改善）、汎用ベクトルDB機能の幅 |
| **Qdrant** | エコマース特化ユースケース | リコメンドAPI・フィルタ付き検索の成熟度・汎用性 |
| **Vespa** | 専用の高レベルAPIと独自モデル | 生の設定柔軟性（MarqoはVespaをバックエンドとして使用） |

### 5-6. 価格情報

**Marqo Cloud**（従量制、既存顧客向けに継続提供）:
- CPU Small インスタンス: 最安プラン
- CPU Large インスタンス: 中間プラン
- GPU インスタンス: 最上位、本番低レイテンシ向け（例: $1.0310/時間）
- 基本ストレージシャード + CPU Large の組み合わせ例: $0.38/時間

**エンタープライズ向けエコマースプラットフォーム**: 
- 問い合わせ制（デモ予約制）
- SOC 2 Type II 認証取得済み

**AWS Marketplace**: 出品済み（別途価格体系）

### 5-7. 最新動向（2025-2026）

- **OSSの廃止**: GitHub上で公式にdeprecatedと表明（2025年時点）
- **製品ピボット完了**: ベクトルDB汎用ツール → AIネイティブエコマース検索プラットフォームへの完全移行
- **エンタープライズ機能強化**: アジェンティック検索（会話型購買体験）、Klaviyo統合、Shopify/Adobe Commerce/Salesforceの直接統合
- **最新バージョン**: v2.26.0（2026年4月7日リリース、ただしOSS版は廃止済み）
- **Series A後の成長**: Lightspeed主導の$12.5M調達後、本社をSFに移転しエンタープライズ市場へ本格参入

---

## 6. 参考URL

- [Marqo 公式サイト](https://www.marqo.ai/)
- [Marqo ドキュメント](https://docs.marqo.ai/)
- [Marqo GitHub リポジトリ（OSS廃止済み）](https://github.com/marqo-ai/marqo)
- [Marqo V2: Performance at Scale（公式ブログ）](https://www.marqo.ai/blog/marqo-v2-performance-at-scale-predictability-and-control)
- [Marqo chooses Vespa（Vespa公式ブログ）](https://blog.vespa.ai/marqo-chooses-vespa/)
- [Introducing Marqo's Ecommerce Embedding Models（公式ブログ）](https://www.marqo.ai/blog/introducing-marqos-ecommerce-embedding-models)
- [Marqo Cloud is Generally Available（公式ブログ）](https://www.marqo.ai/blog/marqo-cloud-is-generally-available)
- [Marqo Raises $12.5M Series A（GlobeNewswire）](https://www.globenewswire.com/news-release/2024/02/13/2828211/0/en/Marqo-Raises-12-5M-to-Make-AI-powered-Vector-Search-Seamless.html)
- [Meet Marqo（TechCrunch 2023）](https://techcrunch.com/2023/08/16/meet-marqo-an-open-source-vector-search-engine-for-ai-applications/)
- [Show HN: Marqo – Vectorless Vector Search（Hacker News）](https://news.ycombinator.com/item?id=37147140)
- [Marqo - Database of Databases](https://dbdb.io/db/marqo)
- [Marqo – Simplyblock Glossary](https://simplyblock.io/glossary/what-is-marqo/)
- [Best Vector Databases 2026 – Firecrawl](https://www.firecrawl.dev/blog/best-vector-databases)
- [Marqo – Crunchbase](https://www.crunchbase.com/organization/marqo)
- [Marqo AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-5hmixpdwwvgbg)

---

## まとめ表

| 項目 | 値 |
|---|---|
| 提供元 / ライセンス | Marqo（豪州発・SF本社）/ Apache-2.0（OSS廃止済み）|
| 位置付け | AIネイティブ・エコマース検索＆プロダクトディスカバリープラットフォーム（旧: 汎用ベクトル検索エンジン）|
| 対応インデックス種類 | HNSW（構造化・非構造化の2モード）|
| 最大次元数 | 4096次元（float32想定、型別の公式記載なし）|
| 量子化対応 | bfloat16（SQ相当・最大2倍のドキュメント格納）/ PQ・Binary・RaBitQの記載なし |
| シャーディング / レプリケーション | 水平シャーディング対応（インデックス作成時に指定）/ レプリカ設定対応 |
| コンピュート/ストレージ分離 | Vespaバックエンドが内部的に対応（公式の明示的な言及なし）|
| 公称最大データ規模 | 数億ドキュメント規模（公式事例として50Mベクトルを明示）|
| 公式ベンチマーク（QPS/Recall）| 10M DBPedia: QPS 157.7、Recall@10 0.97、P50 70ms（V2、Marqo社発表）|
| フィルタ付き検索 | 対応（Marqo Filter DSL、フィルタ付き検索で60-65%のレイテンシ改善）|
| ハイブリッド検索（BM25+Vector）| 対応（TENSOR + LEXICAL、言語対応あり）|
| SPLADE / 学習型スパース対応 | 記載なし（明示的なサポートの公式ドキュメント確認できず）|
| Late Interaction（ColBERT等）対応 | 記載なし（明示的な対応の公式ドキュメント確認できず）|
| Cross-Encoder リランカー対応 | 記載なし（Vespaの内部多段ランキングは利用しているが、ユーザー向けAPIでの公開は不明）|
| リコメンド API / 機能 | ネイティブ対応（similar / complementary 専用エンドポイント、最大10 docId指定）|
| 提供形態（OSS / Managed / Enterprise）| OSS廃止済み / Marqo Cloud（既存顧客向け）/ エンタープライズ向けエコマースSaaS |
| SLA / コンプライアンス | SOC 2 Type II 取得済み / 具体的SLA数値は非公開 |
| 価格モデル | 従量制（CPU Small/Large・GPU・ストレージシャード組み合わせ）/ 例: CPU Large+基本ストレージ $0.38/時間、GPU+基本ストレージ $1.0310/時間 |
| デプロイ手段 | Docker / Helm / Kubernetes / Marqo Cloud / AWS Marketplace |
| マルチテナンシー | インデックス単位での分離（詳細な記載なし）|
| 可観測性 | 記載なし（Marqo Pixel によるユーザー行動トラッキングは対応）|
| バックアップ / リストア | 記載なし |
| 特徴的な機能 | マルチモーダル埋め込みモデル内蔵（Marqo-Ecommerce-B/L、FashionCLIP/SigLIP）、エコマース特化レコメンドAPI、Vespaバックエンド（V2以降）、会話型アジェンティック検索 |
