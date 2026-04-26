# ZeroEntropy Zerank 市場調査レポート

> 調査日: 2026年4月25日

---

## 基本情報

| 項目 | 内容 |
|------|------|
| プロダクト名 | Zerank（zerank-1 / zerank-1-small / zerank-2） |
| 開発元 | ZeroEntropy |
| 公式URL | https://zeroentropy.dev/ |
| ドキュメント | https://docs.zeroentropy.dev/models |
| 最新モデル | zerank-2（フラッグシップ） |
| 価格 | $0.025 / 1Mトークン（全モデル共通） |
| ライセンス | zerank-1-small: Apache 2.0、zerank-1 / zerank-2: 非商用ライセンス（商用利用は別途契約） |
| デプロイ方式 | API / AWS Marketplace / Azure Marketplace / セルフホスト |
| コンプライアンス | SOC2 Type II、HIPAA、GDPR、CCPA |
| 論文 | [zELO: ELO-inspired Training Method for Rerankers and Embedding Models (arXiv:2509.12541)](https://arxiv.org/abs/2509.12541) |

### モデルファミリー

| モデル | 特徴 | ライセンス |
|--------|------|-----------|
| zerank-2 | 最新フラッグシップ。多言語・命令追従・スコアキャリブレーション対応 | 非商用（商用は要契約） |
| zerank-1 | 初代SOTA。金融・法律・STEM等のドメイン特化 | 非商用 |
| zerank-1-small | 軽量版。完全オープンソース | Apache 2.0 |

---

## 市場ポジション

- **Agentset ELOリーダーボード1位**（2025年時点）: ELO 1638でzerank-2がトップ
- 次点のCohere Rerank 4 Pro（ELO 1629）に9ポイント差をつけて首位
- リランカー専業ベンダーとして「精度・レイテンシ・コスト」の三拍子揃いを主軸に訴求
- AWS Marketplace・Azure Marketplaceに出品済みで、エンタープライズ販路を確保
- 主要採用顧客: Assembled、Mem0、Vera Health、Profound、Sendbird

---

## 開発元のアピールポイント

### 1. 精度の優位性
- zerank-1はCohere rerank-3.5・Salesforce LlamaRankをNDCG@10で最大18%上回ると主張
- 金融・法律・医療・STEM・コード等の専門ドメインで一貫してSOTA性能
- ゼロショットでドメイン外・プライベートデータセットでも高い汎化性能

### 2. レイテンシの優位性
- 97.3%のリクエストが500ms以内に完了（zerank-2実測値）
- Jina rerankerより最大14倍高速と主張（zerank-1時代の比較）
- Cohereより約12%高速（zerank-1 vs Cohere rerank-3.5）
- 500ms超過率: zerank-2 2.7% vs Cohere 14.3% vs Jina 70.8% vs Voyage 10.9%

### 3. コスト優位性
- $0.025/1Mトークンで競合の半額（CohereとVoyage AIはともに$0.050/1Mトークン）
- GPT-4o統合時のトータルコストを最大72%削減した事例あり（$162,000/日→$44,010/日）

### 4. zerank-2の差別化機能
- **ネイティブ命令追従（Instruction Following）**: ビジネスコンテキスト・用語集・ドメイン固有の略語を指示として与え、リランキングを制御可能
- **真の多言語対応**: 100言語以上で近英語同等性能を維持。アラビア語・中国語・複合言語（Spanglish、Hinglishなど）にも対応
- **キャリブレーション済みスコア**: スコア0.8 ≈ 実際の関連性80%という信頼度のある確率的スコアを提供
- **SQL・集計クエリ対応**: 「上位N件を抽出」「〇〇順にソート」などの構造化指示を理解

### 5. zELO訓練手法（独自技術）
- ランキングタスクをThurstoneモデルと統計的に等価と捉えたELOインスパイアの訓練法
- 112,000クエリ × 100ドキュメントのデータで、10,000 H100時間未満で訓練
- ポイントワイズの人手アノテーションを排し、ペアワイズ比較に基づくスコアリング
- 非教師データから高品質なリランカーを学習できることを実証

### 6. インフラとしての統合製品
- zerank単体だけでなく、zembed-1（埋め込みモデル）とzsearch（E2E検索API）を合わせた「検索インフラ」として訴求

---

## 第三者評価：強み

### Agentset リーダーボード（2025）
- zerank-2がELO 1638で全リランカー中トップ
- 「本番利用における最良のリランカー（best overall reranker for production use）」と評価
- nDCG@5/10、Recall@5/10をFiQA（金融）・SciFact（科学）・PG（長文）で測定

### コミュニティ・技術ブログの評価
- zerank-1は「商用クローズドソースの2倍サイズのモデルを一貫して上回る」とされる
- コスト・性能のバランスで第三者が「最良の選択肢」として推薦するケースが増加
- AWS Marketplaceでの提供により導入摩擦が低く、エンタープライズ採用が進む

---

## 第三者評価：弱点・批判点

### 1. zerank-2のウェイト非公開問題（Hugging Face コミュニティ）
- HuggingFace上のzerank-2リポジトリで「スコアヘッド（score.weight）がチェックポイントに含まれておらず、毎回のロード時にランダム初期化される」という致命的バグが複数ユーザーから報告（2026年2月）
- 標準的な `CrossEncoder` 経由では正しく動作しない
- 回避策として独自の `modeling_zeranker.py` を直接ロードする方法が提供されているが、HuggingFace Transformers / Sentence Transformers との統合が非標準

参考: [zerank-2 Discussions: "where is weights"](https://huggingface.co/zeroentropy/zerank-2/discussions/6)

### 2. 商用ライセンスの制限
- zerank-2・zerank-1 は非商用ライセンスであり、商用利用には ZeroEntropy との別途契約が必要
- API依存・ベンダーロックインのリスクがある
- 完全オープンなのはzerank-1-small（Apache 2.0）のみ

### 3. ベンチマーク自己申告への懸念
- 多くのベンチマーク数値はZeroEntropy自身のブログで掲載されており、独立した第三者による再現性検証が限られている
- Agentset leaderboardが最も信頼性の高い独立評価だが、評価データセット数はまだ少ない（FiQA・SciFact・PG の3データセット）

### 4. エコシステム成熟度
- 新興ベンダーであり、CohereやVoyage AIと比較してSDKサポート・ドキュメントの深さ・コミュニティ規模で劣る
- Sentence Transformers / vLLM との統合に問題があるとの報告（[vLLM Forums](https://discuss.vllm.ai/t/zerank-deploying-using-vllm/1793)）

### 5. Agentset leaderboard上のnDCG@10数値
- Cohere Rerank 4 Pro（0.095）やVoyage AI Rerank 2.5（0.110）と比較して zerank-2 は 0.079 と低い値を示しており、「精度でも首位」という主張と乖離がある点は注意が必要
- ELO（相対的な頭合わせ評価）では首位だが、NDCG@10（絶対的精度指標）では差がある

---

## ベンチマーク結果

### Agentset ELOリーダーボード（2025）

| モデル | ELO | nDCG@10 | 平均レイテンシ | 価格/1Mトークン |
|--------|-----|---------|--------------|----------------|
| **zerank-2** | **1638** | 0.079 | 265ms | $0.025 |
| Cohere Rerank 4 Pro | 1629 | 0.095 | 614ms | $0.050 |
| zerank-1 | 1573 | - | - | $0.025 |
| Voyage AI Rerank 2.5 | 1544 | 0.110 | 613ms | $0.050 |
| zerank-1-small | 1539 | - | - | $0.025 |
| Qwen3 Reranker 8B | 1473 | 0.106 | 4687ms | $0.050 |

*評価方法: GPT-5による頭合わせ比較からELOを算出。FAISSで取得した上位50件をリランキング。*

### レイテンシベンチマーク（zerank-2 vs 競合、500ms超過率）

| モデル | >150ms | >500ms | >1s | 失敗率 |
|--------|--------|--------|-----|--------|
| **zerank-2** | 50.5% | **2.7%** | 0.9% | **0.0%** |
| Cohere rerank-3.5 | - | 14.3% | 11.6% | 0.0% |
| Jina reranker m0 | - | 70.8% | 57.4% | 55.7% |
| Voyage rerank-2.5 | - | 10.9% | 9.7% | 9.2% |

*出典: ZeroEntropy公式レイテンシアセスメント（自社測定）*

### ドメイン別NDCG@10（zerank-1, ZeroEntropy社内測定）

- 金融文書検索: Cohere rerank-3比で +18% NDCG@10
- 医療サービス: NDCG@10 0.89（競合は0.75〜0.80）
- 対象ドメイン: 金融・法律・コード・STEM・医療・会話データ

### zELO論文ベンチマーク（arXiv:2509.12541）

- 金融・法律・コード・STEMのNDCG@10およびRecallで、クローズドソース競合を上回ると報告
- ドメイン外・プライベートデータセットでも強いゼロショット性能

---

## 競合比較

| 比較軸 | zerank-2 | Cohere Rerank 4 Pro | Voyage AI Rerank 2.5 | Jina Reranker v2 |
|--------|----------|---------------------|----------------------|------------------|
| ELO（Agentset） | **1638 (1位)** | 1629 (2位) | 1544 (4位) | - |
| nDCG@10（Agentset） | 0.079 | 0.095 | **0.110** | - |
| 平均レイテンシ | **265ms** | 614ms | 613ms | 高レイテンシ |
| 価格/1Mトークン | **$0.025** | $0.050 | $0.050 | - |
| 多言語対応 | 100言語以上 | 高水準 | 高水準 | - |
| 命令追従 | ネイティブ対応 | - | チューニング済み | - |
| スコアキャリブレーション | 対応 | - | - | - |
| オープンウェイト | 非商用のみ | クローズド | クローズド | オープン |
| 商用ライセンス | 要別途契約 | API提供 | API提供 | Apache 2.0 |

### まとめ

- **精度（ELO）vs コスト**: zerank-2がELOトップかつ最安値という稀有なポジション
- **精度（nDCG@10絶対値）**: Voyage AI Rerank 2.5が最高スコアを示す局面もある
- **レイテンシ**: zerank-2が競合より2〜23倍高速（特にJina比）
- **オープン性**: zerank-1-smallのみApache 2.0、zerank-2は実質クローズド商用モデル
- **エコシステム成熟度**: Cohere/Voyage AIに対してまだ発展途上

---

## 参考リンク

- [ZeroEntropy 公式サイト](https://zeroentropy.dev/)
- [ZeroEntropy ドキュメント（モデル一覧）](https://docs.zeroentropy.dev/models)
- [zerank-2 紹介ブログ](https://zeroentropy.dev/articles/zerank-2-advanced-instruction-following-multilingual-reranker/)
- [zerank-1 リリースブログ](https://zeroentropy.dev/articles/announcing-zeroentropy-s-first-rerankers-zerank-1-and-zerank-1-small/)
- [zELO論文 (arXiv:2509.12541)](https://arxiv.org/abs/2509.12541)
- [zELO論文 TLDR（ZeroEntropyブログ）](https://zeroentropy.dev/articles/paper-tldr-how-we-trained-zerank-1-with-the-zelo-method/)
- [レイテンシベンチマーク: Cohere vs zerank-1](https://zeroentropy.dev/articles/lightning-fast-reranking-with-zerank-1/)
- [zerank-2 レイテンシアセスメント](https://www.zeroentropy.dev/articles/latency-performance-assessment-of-zerank-2)
- [リランキングモデル選択ガイド 2026 (ZeroEntropy)](https://zeroentropy.dev/articles/ultimate-guide-to-choosing-the-best-reranking-model-in-2025/)
- [Agentset リランカーリーダーボード](https://agentset.ai/rerankers)
- [Agentset: Best Reranker for RAG](https://agentset.ai/blog/best-reranker)
- [zerank-1 Hugging Face](https://huggingface.co/zeroentropy/zerank-1)
- [zerank-2 Hugging Face](https://huggingface.co/zeroentropy/zerank-2)
- [zerank-2 ウェイト問題 Hugging Face Discussion](https://huggingface.co/zeroentropy/zerank-2/discussions/6)
- [zerank-2 AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-o7avk66msiukc)
- [Communeify: zerank-2 レビュー](https://www.communeify.com/en/blog/zeroentropy-zerank-2-precise-cheap-search-reranking-multilingual/)
- [zerank訓練事例 (TensorPool)](https://tensorpool.dev/blog/zeroentropy-zerank-training)
