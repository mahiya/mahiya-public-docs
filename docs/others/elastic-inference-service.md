# Elastic Inference Service

## 概要

- Elastic Inference Service (EIS) は、Elastic Cloud上で提供される**マネージドGPU推論サービス**であり、Elasticsearchクラスタとネイティブ統合された埋め込み生成・リランキング・LLM推論を提供する
- ユーザーは機械学習ノードを自前で立ち上げ・スケールさせる必要がなく、`semantic_text` フィールドや `_inference` API を介してそのまま利用できる「Inference as a Service」モデルである
- 提供モデルは ELSER (`.elser-2-elastic`)、Jina AIの `jina-embeddings-v3`・`jina-reranker-v2-base-multilingual`・`jina-reranker-v3` に加え、Anthropic / OpenAI / Google などのLLMを含むマルチモデルカタログである
- AWS `us-east-1`、GCP `asia-southeast1` / `europe-west1` / `us-east4` の複数リージョンで利用可能で、マルチクラウド・マルチリージョン・マルチモーダルを設計目標としている
- 2025年10月にGPU推論基盤として登場後、Elastic 9.3 (2026年2月) で Jina モデル群がGAとなり、**Cloud Connect** 経由で自己管理 (ECK / ECE / オンプレ) クラスタからも利用可能になった

---

## 技術者向けポイント

### 1. アーキテクチャ：MLノードからGPUフリートへの分離

- 従来の Elasticsearch 推論は各クラスタの ML ノード（CPU中心）でモデルをホストしていたが、EIS はこれを Elastic 側の常駐 **GPU フリート**にオフロードする
- バックエンドは Ray ベースのモデルサービング基盤上に構築されており、ELSER などのスパース埋め込みモデルをGPUで実行することで、MLノード比でingestスループットの大幅向上を実現している
- クラスタ側は `inference_id` (`.elser-2-elastic` など) を指す軽量なエンドポイント参照のみを保持し、データプレーンを跨いだ呼び出しは Elastic 内部ネットワーク上のマネージドサービスとして処理される
- search latency は MLノードと同等を維持する設計で、検索クエリ時のレイテンシ悪化なくingest側のGPU恩恵を享受できる

### 2. Inference Endpoint と semantic_text による統合

- EIS はデフォルトで preconfigured な inference endpoint (`.elser-2-elastic`、`.rerank-v1-elastic` 等) を提供し、`semantic_text` フィールド定義時の `inference_id` にそのまま指定可能
- ML ノード版のデフォルト (`.elser-2-elasticsearch`、`.multilingual-e5-small-elasticsearch` 等) と並列に存在し、運用者はデプロイメントごとに使い分けできる
- 既存の Inference API (`PUT _inference/{task_type}/{inference_id}`) を通じて、特定モデルバージョンや独自設定を持つカスタム EIS endpoint も作成可能
- ELSER / E5 のような自前モデルは adaptive allocations による動的スケーリングが可能で、EIS endpoint と Eland 経由のサードパーティモデルを統一的なAPIで扱える

### 3. Cloud Connect によるハイブリッドトポロジ

- Cloud Connect は **自己管理 Elasticsearch (ECK / ECE / standalone)** を Elastic Cloud のマネージドサービスへ接続するブリッジ機構で、EIS via Cloud Connect は Elastic 9.3 で GA となった
- データノード・マスタノード・インデックスストレージはすべてオンプレ／プライベートクラウドに残し、**ベクトル化対象のテキストフィールドのみ**を Elastic Cloud に送信して GPU 推論を受ける構成
- 接続フローは「Elastic Cloud 上で Cloud Connect API キーを発行 → 自己管理クラスタの Cloud Connect ページに貼り付け → EIS を Connect」の3ステップで、Kibana AI Connector も自動生成される
- Anthropic Claude などの LLM コネクタも含めて自動構成されるため、Agent Builder や AI Assistant、Attack Discovery などが追加設定なしに動作する

### 4. モデルカタログとマルチモーダル展開

- 埋め込み: ELSER v2 (sparse)、`jina-embeddings-v3` (multilingual dense)、E5 系
- リランカー: `jina-reranker-v2-base-multilingual`、`jina-reranker-v3` (テキスト→テキスト、データ保持0日、リージョン US/SG/EU、Stack 9.3 以降GA)
- LLM: Agent Builder / AI Assistant のバックエンドとして Anthropic / OpenAI 等のモデルがマネージド提供され、エージェントの「retrieve → reason → act」を一貫したAPIで構築可能
- 今後の Jina AI 製モデル（買収済み）は新規リリース時点から EIS 経由提供がデフォルトとなり、マルチモーダル（テキスト・画像・コード・長文多言語）への拡張が予定されている

---

## ビジネス側向けポイント

### 1. 運用負荷とTCOの削減

- GPU 調達・容量計画・モデルのデプロイ／更新・スケール調整といった MLOps 業務が不要になり、エンジニアリングリソースをアプリケーション側に集中投下できる
- ML ノード追加によるクラスタ拡張・ライセンス費用の増大を回避し、推論コストは EIS のトークンベース消費型課金へ移行する
- 検索インフラの「常時GPU待機コスト」を Elastic 側のフリート共有でならせるため、トラフィック変動の大きいワークロードでとくにコスト効率が高い
- バージョンアップやモデル差し替えがマネージド側で吸収され、ベンダーロックインリスクの低い形でモデルライフサイクル管理を委譲できる

### 2. 規制・セキュリティ要件への適合（Cloud Connect）

- データ本体（テラバイト級の業務データ・インデックス）はオンプレ／プライベートクラウドに留まり、推論対象のテキストフィールドのみが暗号化通信で Elastic Cloud に送られるハイブリッド構成
- リフト&シフトを伴う完全クラウド移行が困難な金融・医療・公共セクターでも、セマンティック検索・RAG・エージェントワークフローを段階的に導入可能
- Jina リランカーは「データ保持0日 / モデル学習に利用しない」と明示されており、企業データの第三者学習混入リスクを回避できる
- リージョン選択 (US / SG / EU) によりデータ越境要件への対応が可能で、GDPR等の規制下でも採用しやすい

### 3. 検索品質と新しいユーザー体験の早期実装

- ELSER on EIS により「キーワード一致を超えた意味検索」を、追加のデータサイエンスチームなしで本番投入可能
- Jina の多言語埋め込み＋多言語リランカーで、グローバル多言語コンテンツに対する高精度検索 (RAG) を即座に導入できる
- Elastic Agent Builder と組み合わせることで、社内ドキュメントに対する自然言語チャット (例: 休暇ポリシー問い合わせ) や AI Assistant 連携をマネージドモデルで構築可能
- AI Assistants・Attack Discovery・Agent Builder などの Elastic 標準機能が EIS 接続で即時利用可能になり、PoC からプロダクション化までのリードタイムを大幅に短縮できる

### 4. 戦略的ポジショニングと今後の拡張性

- Elastic は Jina AI を買収しており、今後の最先端 Jina モデルはリリース時から EIS で提供される計画 — 検索基盤に最新の埋め込み／リランカーを継続的に取り込める
- マルチクラウド (AWS / GCP) / マルチリージョン / マルチモーダルを設計目標としており、長期的な AI 検索基盤として将来要件への耐性が高い
- Elastic Cloud Trial・Serverless・Hosted の全プランで EIS が標準利用可能となっており、PoC 障壁が低くスタートアップから大企業まで採用しやすい
- ベクトルDB単独製品やGPU推論サービス単独製品を組み合わせる「点ソリューション」アプローチに対し、EIS は検索＋推論を1ベンダーで完結させる統合価値を提供する

---

## 出典

収集した一次情報は `urls.md` および `collected/` 配下の各記事 (Markdown + 画像) を参照。主要画像は `images/` に集約。
