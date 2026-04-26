# リランキングモデル（Cross-Encoder）市場比較レポート

> 調査日: 2026年4月25日
> 対象カテゴリ: リランキングモデル（Cross-Encoder）
> 比較対象: トップ5プロダクト

---

## エグゼクティブサマリー

リランキングモデル市場は2025〜2026年にかけて急速に成熟し、商用APIとOSSの両軸で高品質なプロダクトが揃ってきた。最大の変化は、**精度・速度・コストの三者均衡が崩れ、三軸すべてで差別化を狙う新興プレイヤーが台頭**していること。従来の市場標準だった Cohere の地位を、ELO首位の ZeroEntropy Zerank と最安値が Voyage AI が侵食しつつある。一方、OSSの BAAI BGE Reranker は月間800万DLというデファクト地位を保持しつつも、精度・速度面で後発の Jina AI Reranker や Qwen3-Reranker に追い抜かれ始めている。

### 結論（3行）
- **精度・信頼性・エコシステム重視**のエンタープライズには → **Cohere Rerank**
- **コスト・速度・精度のバランス**を最優先するプロダクション RAG には → **ZeroEntropy Zerank**
- **コストゼロ・完全制御・カスタマイズ**が必要な組織には → **BAAI BGE Reranker**

---

## 比較対象プロダクト概要

| プロダクト | 提供元 | 最新モデル | 形態 | 選定根拠 |
|------------|--------|-----------|------|---------|
| **Cohere Rerank** | Cohere | rerank-v4-pro | 商用API + エンタープライズオンプレ | 最古参商用API、全主要フレームワーク標準統合 |
| **BAAI BGE Reranker** | BAAI（北京人工知能研究院） | bge-reranker-v2-m3 | OSS（Apache 2.0） | 月間810万DL、OSSリランカーのデファクトスタンダード |
| **Voyage AI Rerank** | Voyage AI（MongoDB傘下） | voyage-rerank-2.5 | 商用APIのみ | NDCG@10業界最高水準、MongoDB買収で展開加速 |
| **Jina AI Reranker** | Jina AI（Elastic傘下） | jina-reranker-v3 | 商用API + OSS（CC-BY-NC） | Elastic買収で大規模ディストリビューション、唯一sub-200ms商用クラス |
| **ZeroEntropy Zerank** | ZeroEntropy | zerank-2 | 商用API + OSS（CC-BY-NC） | ELOリーダーボード1位、Cohere/Voyageの半額 |

---

## 総合比較表

| 比較項目 | Cohere Rerank | BAAI BGE Reranker | Voyage AI Rerank | Jina AI Reranker | ZeroEntropy Zerank |
|---------|:---:|:---:|:---:|:---:|:---:|
| **PERF-01** BEIR NDCG@10 | 非公開 | **0.5651** | 非公開 | **0.6194** | 非公開 |
| **PERF-02** ELO スコア | 1629（2位） | 1327（11位） | 1544（4位） | 未掲載 | **1638（1位）** |
| **PERF-03** 多言語精度（MIRACL） | 非公開 | **69.32** | 非公開 | 66.83 | 非公開 |
| **LATENCY-01** 平均レイテンシ | 614ms | 2383ms（API経由） | 613ms | 100〜7000ms | **265ms** |
| **LATENCY-02** P99安定性 | 普通 | 非公開 | 普通 | 不安定 | **安定** |
| **COST-01** 料金体系 | クエリ従量課金 | 無料（OSS） | トークン従量課金 | トークン従量課金 | ハイブリッド |
| **COST-02** 1M トークン価格 | $2.50 | 無料 | $0.05 | $0.05 | **$0.025** |
| **COST-03** 無料利用枠 | あり（無料ティア） | **完全無料** | あり（200M token） | あり（10M token） | あり（無料ティア） |
| **DEPLOY-01** 提供形態 | 両方対応 | OSS自己ホスト | マネージドAPIのみ | 両方対応 | 両方対応 |
| **DEPLOY-02** ライセンス | 要別途契約 | **Apache 2.0** | 独自プロプライエタリ | CC-BY-NC | CC-BY-NC |
| **LANG-01** サポート言語数 | 100以上 | 100以上 | 31 | 100以上 | 100以上 |
| **LANG-02** 日本語対応品質 | 中 | **高** | **高** | **高** | 中 |
| **INTEG-01** LangChain/LlamaIndex | **両方対応** | **両方対応** | **両方対応** | **両方対応** | なし |
| **INTEG-02** ベクトルDB統合 | **広範（3+）** | **広範（3+）** | **広範（3+）** | **広範（3+）** | 中程度 |
| **INTEG-03** クラウドMP | **複数クラウド** | 単一クラウド | **複数クラウド** | **複数クラウド** | **複数クラウド** |
| **FEAT-01** コンテキスト長 | 32,768 tok | 8,192 tok | 32,000 tok | **131,072 tok** | 32,768 tok |
| **FEAT-02** 命令追従 | **対応** | 非対応 | **対応** | 限定的対応 | **対応** |
| **FEAT-03** マルチモーダル | 非対応 | 非対応 | 非対応 | 限定的対応 | 非対応 |
| **ENTER-01** SLA | あり（非公開） | 該当なし | あり（非公開） | あり（非公開） | **あり（99.99%）** |
| **ENTER-02** セキュリティ認証 | **複数認証** | 自社管理 | **複数認証** | **複数認証** | **複数認証** |
| **ENTER-03** エンタープライズサポート | **あり** | なし | **あり** | **あり** | **あり** |

> ★ 太字は各項目で最も優れた値、または同率最上位の値

---

## カテゴリ別詳細分析

### PERF（精度・品質）

**重要な前提：ベンチマーク透明性の格差**

精度比較を行う上で最初に指摘すべきは、**主要商用プロダクトの多くが BEIR NDCG@10 の絶対値を非公開にしている**という点だ。Cohere・Voyage AI・ZeroEntropy はいずれも「競合比 XX% 向上」という相対値のみを開示するポリシーを取っており、独立したクロス比較が困難な状況にある。

```
BEIR NDCG@10（公開値）
Jina v3:  0.6194  ████████████████████████████████
BGE v2-m3: 0.5651  ██████████████████████████████
Cohere:   非公開   ████████████████████████████?
Voyage:   非公開   ████████████████████████████?
Zerank:   非公開   ████████████████████████████?
```

**ELO リーダーボード（agentset.ai、独立評価）**

ELO スコアは agentset.ai が複数モデル間のペアワイズ比較を独立して計測した指標であり、現時点で最も信頼性の高い相対評価といえる。

```
ELO スコア（agentset.ai）
Zerank 2:    1638  ██████████████████████████████████████
Cohere v4-P: 1629  ████████████████████████████████████
Voyage 2.5:  1544  ██████████████████████████████████
BGE v2-m3:   1327  ████████████████████████████
Jina v3:   未掲載  （2025年9月リリース後未収録）
```

**分析ポイント**
- Zerank 2 の ELO 首位（1638）は注目に値するが、Zerank の独自評価（7ドメイン平均 NDCG@10 0.6714）と ELO の整合性についてはコミュニティで議論が継続中
- Jina v3 の BEIR 0.6194 は公開値の中で最高だが、ELO には未収録のため他社比較が限定的
- BGE v2-m3 は MIRACL 多言語スコア（69.32）で最高値を記録し、多言語精度では商用 API を含む中でトップ

---

### LATENCY（レイテンシ・速度）

```
平均レイテンシ（ms）※第三者計測値、agentset.ai
Zerank 2:  265ms  ███
Jina v3:   *未計測（v2 ベースで188ms）
Cohere:    614ms  ██████
Voyage:    613ms  ██████
BGE:      2383ms  ████████████████████████（API経由）
```

**ZeroEntropy Zerank の優位性**

agentset.ai の第三者計測において zerank-2 は **265ms** と全商用モデル中で圧倒的に最速。P99 安定性も ZeroEntropy 自社計測値によれば 500ms 超過率 2.7%（Cohere: 14.3%、Voyage: 10.9%）と良好。ただしこの P99 データは ZeroEntropy 自身が公開したものであり、独立した検証ではない点に留意が必要。

**BGE の特殊性**

BGE v2-m3 の 2383ms はサードパーティ API 経由の計測値であり、自社 GPU 環境に直接デプロイした場合は大幅に高速化できる（一般的に 100〜400ms 程度）。自己ホストの場合はハードウェアスペックに大きく依存する。

**Jina AI の位置付け**

最新の jina-reranker-v3 は agentset.ai 未収録だが、前世代（jina-reranker-v2）で 188ms という最速値を持ち、v3 でもこの水準の維持が期待される。一方、ドキュメント長によっては 7000ms まで伸長するという特性があり、長文書 RAG では注意が必要。

---

### COST（コスト）

**価格帯の大きな格差**

```
API 利用コスト比較（1M トークン、USD）
BGE:      $0.00   ████（OSS自己ホスト）
Zerank:   $0.025  ███
Voyage:   $0.050  ██████
Jina:     $0.050  ██████
Cohere:   $2.50   ████████████████████████████████████████████████████████
```

**Cohere の料金体系の注意点**

Cohere はトークン数ではなく「クエリ数（最大100ドキュメント）」単位で課金するため、上記の $2.50/1M トークン換算は比較ツール（CloudPrice 等）による推定値である。実際には 1 クエリあたりのコストは文書数・トークン数によって異なる。一方、この体系はトークン節約の余地が少なく、Voyage AI の 200M トークン無料枠（最大の無料枠）と比較して初期費用が高い。

**ZeroEntropy の価格革命**

zerank-2 の $0.025/1M トークンは Voyage AI・Jina の 1/2、Cohere との比較では 1/100 に相当する。ZeroEntropy は「Cohere の半額で同等以上の精度」を全面に打ち出しており、コスパ追求ユーザーへの訴求力は高い。ただし zerank-2 モデル自体の商用利用には CC-BY-NC ライセンスの制約があり、API 利用（有償）が商用利用のメインパスとなる。

---

### DEPLOY（デプロイ・提供形態）

**提供形態の多様性**

| 形態 | プロダクト | 注記 |
|------|----------|------|
| マネージドAPIのみ | Voyage AI | セルフホスト不可。クラウド依存が強い |
| OSS自己ホストのみ | BAAI BGE | GPU/CPU問わず自社インフラで動作 |
| API + OSS両対応 | Jina, Zerank | CC-BY-NC のため商用OSS利用には制限 |
| API + エンタープライズオンプレ | Cohere | 自己ホストはエンタープライズ契約が必要 |

**ライセンスは選定の重要障壁**

- **Apache 2.0（BGE のみ）**: 商用利用・改変・再配布すべて自由。唯一の「本当の意味でのOSS」
- **CC-BY-NC（Jina / Zerank）**: 非商用利用のみ自由。商用用途は API 経由（有償）が必要
- **プロプライエタリ（Cohere / Voyage）**: モデルの自己ホストは原則不可。データを外部に送る必要あり

---

### LANG（多言語・言語対応）

**100言語サポートの実態差**

4プロダクトが「100言語以上」をサポートすると主張するが、その品質には差がある：

| プロダクト | 言語数 | 日本語品質 | ベンチマーク証拠 |
|-----------|-------|-----------|---------------|
| Cohere | 100以上 | 中 | 具体的数値なし |
| BGE v2-m3 | 100以上 | **高** | MIRACL 18言語 nDCG@10 **69.32（最高）** |
| Voyage 2.5 | 31 | **高** | 日本語明示、商用 API で最少言語数 |
| Jina v3 | 100以上 | **高** | MIRACL 66.83、MKQA で検証済み |
| Zerank 2 | 100以上（ブログ記載） | 中 | 個別言語ベンチマークなし |

**Voyage AI の言語数制限**

Voyage AI の 31 言語はサポート言語数で最も少ない。日本語は含まれているが、グローバル展開が必要な場合は制約となりうる。

---

### INTEG（エコシステム統合）

**ZeroEntropy の孤立**

INTEG 分野で最も目立つのは **ZeroEntropy Zerank が LangChain / LlamaIndex の公式統合を持たない**点だ。ELO 1位・最安値でありながら、最も普及したフレームワークに標準組み込みされていないことが採用障壁になっている。

```
LangChain / LlamaIndex 統合
Cohere:  ✅ 両方（公式コンポーネント）
BGE:     ✅ 両方（HuggingFaceCrossEncoder経由）
Voyage:  ✅ 両方（公式パッケージ）
Jina:    ✅ 両方（公式ドキュメント）
Zerank:  ❌ なし（API 経由でカスタム実装が必要）
```

**企業買収による統合の加速**

- **Jina AI → Elastic（2025年10月完了）**: Elasticsearch のネイティブリランカーとして統合。Elastic Inference Service でのマネージド提供も開始。
- **Voyage AI → MongoDB（2025年2月完了）**: MongoDB Atlas Vector Search との緊密なネイティブ統合。Atlas ユーザーは追加設定不要で利用可能。

---

### FEAT（機能・特徴）

**コンテキスト長の差異**

```
最大コンテキスト長（トークン）
Jina v3:  131,072  ████████████████████████████████████████████████████████████████
Cohere:    32,768  ████████████████
Zerank:    32,768  ████████████████
Voyage:    32,000  ███████████████
BGE:        8,192  ████
```

Jina v3 のコンテキスト長（131K トークン）は他を大きく引き離す。法律・医療・金融など長大な文書をリランキングする用途では唯一の現実的な選択肢。

**命令追従（Instruction Following）機能の普及**

2025年以降、命令追従は差別化機能から「基本機能」へと移行しつつある。

| 対応状況 | プロダクト | 実装の詳細 |
|---------|----------|---------|
| **対応** | Cohere | v4 で "self-learning" として搭載 |
| **対応** | Voyage AI | MAIR ベンチマークで Cohere v3.5 比 +12.70% |
| **対応** | ZeroEntropy | zerank-2 で命令追従をネイティブサポート |
| 限定的 | Jina | 構造化プロンプトのみ、公式機能としては未公開 |
| **非対応** | BGE | 命令追従機能なし |

**マルチモーダル**

テキスト以外のモダリティ対応は、現時点では Jina AI のみが限定的にサポート（jina-reranker-m0 による画像・PDF 対応）。ただし jina-reranker-v3 自体はテキスト専用であり、マルチモーダルを求める場合は別モデルとなる。

---

### ENTER（エンタープライズ対応）

**SLA 明示はZeroEntropy のみ**

エンタープライズ利用において SLA（稼働率保証）は重要だが、具体的な数値（99.9% 等）を公式に明示しているのは ZeroEntropy のみ（99.99% をエンタープライズプランで保証）。Cohere・Voyage・Jina は「あり」とは謳うが水準を非公開にしている。

**セキュリティ認証の整備状況**

商用 API プロバイダー4社（Cohere・Voyage・Jina・ZeroEntropy）はすべて SOC2 Type II 等の主要認証を取得済み。

| 認証 | Cohere | Voyage | Jina | ZeroEntropy | BGE |
|-----|--------|--------|------|------------|-----|
| SOC2 Type II | ✅ | ✅ | ✅ | ✅ | N/A |
| HIPAA | ✅ | ✅ | — | ✅ | N/A |
| GDPR | ✅ | — | ✅ | ✅ | 自社管理 |

**Cohere の特殊性：規制産業向けに実績あり**

Cohere は金融・ヘルスケア・政府向けに特化したセールスチームと事例を持つ。AWS Bedrock / Azure AI Foundry / OCI / SAP との公式統合がありアジア太平洋地域でも積極展開中（評価額 $70 億、IPO 準備中）。

---

## ユースケース別推薦

### 推薦マトリクス

| ユースケース | 推薦プロダクト | 理由 |
|-------------|--------------|------|
| **生産性・精度最優先のエンタープライズ RAG** | Cohere Rerank | ELO 2位、最も成熟したエコシステム、規制産業対応、全フレームワーク統合 |
| **コスパ最重視のプロダクション RAG** | ZeroEntropy Zerank | ELO 1位、最速（265ms）、最安値（$0.025）、命令追従対応 |
| **セルフホスト必須 / コストゼロ** | BAAI BGE Reranker | Apache 2.0 完全無料、最も広い採用実績、多言語精度 MIRACL 最高 |
| **長文書 RAG（法律・医療・金融）** | Jina AI Reranker | 131K トークンコンテキスト（他の4倍以上）、Elastic 統合 |
| **Elasticsearch / Elastic Stack 統合** | Jina AI Reranker | Elastic 買収により Elastic Inference Service で深い統合 |
| **MongoDB Atlas ユーザー** | Voyage AI Rerank | MongoDB 買収によりネイティブ統合、Atlas から seamless に利用可能 |
| **多言語 / 日本語 RAG** | BAAI BGE Reranker または Jina AI | MIRACL スコアで BGE が最高（69.32）、Jina も日本語検証済み |
| **GCP / Google エコシステム** | Voyage AI Rerank または Cohere | Google Vertex AI との統合事例あり（特に Voyage）|
| **スタートアップ / PoC 段階** | ZeroEntropy Zerank | 最安値・最速・無料ティアあり、zerank-1-small は Apache 2.0 で無料 |

---

## 総評・結論

### 市場の構造変化

リランキングモデル市場は2025〜2026年にかけて大きな転換点を迎えた。最も象徴的なのは：

1. **精度と価格のデカップリング**: ELO 1位の ZeroEntropy Zerank が Cohere の 1/100 の価格を実現。「高精度 = 高コスト」という前提が崩れた。

2. **企業買収による統合加速**: Jina AI（Elastic）・Voyage AI（MongoDB）の買収により、リランキング機能がインフラレイヤーに組み込まれ始めた。これは「専用サービスを選ぶ」ではなく「スタックについてくる」という選定パターンを生む。

3. **命令追従の標準化**: 2025年に Contextual AI が先鞭をつけた命令追従機能は、2026年時点で Cohere・Voyage・ZeroEntropy が対応。OSS ではまだ普及途上だが、差別化から必須機能へ移行中。

### 各プロダクトの最終評価

**Cohere Rerank** — *エンタープライズ標準*
最大の強みは成熟したエコシステムと信頼性。ELO では Zerank にわずかに及ばないが、LangChain/LlamaIndex/AWS/Azure への深い統合と規制産業向け実績は唯一無二。コストは最も高く、新興競合との差別化に課題。

**BAAI BGE Reranker** — *OSS のデファクト*
Apache 2.0 のみが唯一の「完全無料商用利用可能」なリランカー。精度は商用 API に劣るが、月間 810 万 DL の普及実績と多言語ベンチマーク最高値（MIRACL 69.32）は健在。エンタープライズサポート・SLA がないためミッションクリティカルな用途には非推奨。

**Voyage AI Rerank** — *精度・安定性の優等生*
NDCG@10 の絶対値（0.110）は公開値の中で最高。命令追従対応、200M トークン無料枠、MongoDB Atlas 統合が強み。言語数が 31 と限定的で自己ホスト不可という制限があり、全世界展開や厳しいデータガバナンス要件には対応困難。

**Jina AI Reranker** — *長文書と低レイテンシの専門家*
131K トークンコンテキストと 188ms 前後のレイテンシは他に代えがたい強み。Elastic への統合が進む中で Elasticsearch ユーザーへの展開が加速。CC-BY-NC ライセンスが商用 OSS 利用の障壁。ELO 未掲載で精度の客観的比較ができないことも課題。

**ZeroEntropy Zerank** — *コスパ最高の新星*
ELO 首位（1638）・最速（265ms）・最安値（$0.025/M）という三冠を引っさげて登場した最注目プロダクト。唯一の弱点は LangChain/LlamaIndex の公式統合不在と、zerank-2 に関するコミュニティからのバグ報告（score.weight の初期化問題）。2026 年中にエコシステム整備が進めば、最有力の市場標準候補。

---

## 参考資料

- [agentset.ai Rerankers Leaderboard](https://agentset.ai/rerankers)
- [ZeroEntropy Ultimate Guide to Reranking Models 2026](https://zeroentropy.dev/articles/ultimate-guide-to-choosing-the-best-reranking-model-in-2025/)
- [Jina Reranker v3 Paper (arXiv:2509.25085)](https://arxiv.org/abs/2509.25085)
- [Cohere Rerank API Documentation](https://docs.cohere.com/docs/rerank-overview)
- [Voyage AI Rerank 2.5 Release Blog](https://blog.voyageai.com/2025/08/11/rerank-2-5/)
- [ZeroEntropy zerank-2 Announcement](https://zeroentropy.dev/articles/zerank-2-advanced-instruction-following-multilingual-reranker/)
- [BAAI/bge-reranker-v2-m3 on HuggingFace](https://huggingface.co/BAAI/bge-reranker-v2-m3)
- [Contextual AI Reranker v2 Blog](https://contextual.ai/blog/rerank-v2)
- [Elastic Completes Acquisition of Jina AI](https://ir.elastic.co/news/news-details/2025/Elastic-Completes-Acquisition-of-Jina-AI)
- [BEIR Benchmark 2025/2026 Leaderboard](https://app.ailog.fr/en/blog/news/beir-benchmark-update)
