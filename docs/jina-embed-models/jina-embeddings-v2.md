# jina-embeddings-v2 モデル情報レポート

**論文**: Jina Embeddings 2: 8192-Token General-Purpose Text Embeddings for Long Documents (arXiv:2310.19923, 2023年10月、最終改訂 2024年2月)
**著者/所属**: Michael Günther, Jackmin Ong, Isabelle Mohr, Alaeddine Abdessalem, Tanguy Abel, Mohammad Kalim Akram, Susana Guzman, Georgios Mastrapas, Saba Sturua, Bo Wang, Maximilian Werk, Nan Wang, Han Xiao (Jina AI)
**URL**: https://arxiv.org/abs/2310.19923

## モデルについて

### 使用したベースモデル
- **値**: **改造版 BERT**(独自にゼロから事前学習)。既存の HuggingFace BERT をそのまま使うのではなく、長文に対応するために以下を改造:
  - 位置埋め込みを撤廃し、ALiBi に置き換え
  - NSP(Next Sentence Prediction)を除去
- **モデルの特徴**: 通常の双方向エンコーダ。3 サイズ(small/base/large)を独自に事前学習。
- **採用の背景**: 既存 BERT 系は 512 トークン制約があり長文ドキュメント処理に向かない、という強い問題意識。長文を「分割→チャンク埋め込み→集約」する従来手法は意味の断片化と検索遅延の原因になるため、本論文では 1 ショットで 8192 トークンを扱える独自エンコーダをゼロから設計している。

### モデルアーキテクチャ
- **位置埋め込み方式**: **ALiBi (Attention with Linear Biases)** の **双方向対称版**。本来 ALiBi は単方向(decoder-only LM)用だが、エンコーダ全トークンが相互に attend できるようバイアスを対称化した変種を導入。
- **Transformerブロック数**:
  - small: **4 層**
  - base: **12 層**
  - large: **24 層**
- **LoRA アダプタの有無**: なし(本論文では未導入。後継 v3 で導入される)。
- **背景**: ALiBi は学習時より長いシーケンスへの外挿が可能なため、512 で訓練しても 8192 まで一気に拡張できる。学習可能な位置埋め込みを廃した結果、メモリオーバーヘッドも削減。

### モデルのパラメータ数
- **値**:
  - small: **33M**
  - base: **137M**
  - large: **435M**(本文記載は約 455M に近い)
- **背景**: 一般的な「small/base/large」の BERT 系階層に揃え、用途別に選べるようにしている。

### 最大コンテキスト長
- **値**: **8,192 トークン**(従来 BERT の 16 倍)
- **背景**: ALiBi の位置非依存な設計が外挿を可能にする。事前学習は 512 トークンで行うのに、推論時は 8192 まで安定して MLM 精度を維持できることを実証している。

### 出力ベクトルの次元数
- **値**:
  - small: **512 次元**
  - base: **768 次元**
  - large: **1,024 次元**
- **背景**: 各サイズの隠れ状態次元をそのまま埋め込み次元として使用。MRL は導入していない。

### 学習したタスク
- 検索(MS-MARCO, Natural Questions など)
- 分類(MTEB Classification 群)
- セマンティック類似度・NLI(STS, MNLI/SNLI 系)
- クラスタリング・再ランキング(MTEB 一般 + 長文)

### Instruction Tuning への対応
- **なし**(プレフィックス的 instruction も使わない)。

### マトリョーシカ表現学習(MRL)の対応
- **なし**。

### 多言語対応かどうか
- **英語のみ**(monolingual)。多言語対応版は別ライン(jina-embeddings-v2-base-zh など)で派生し、本論文の対象外。

## モデルの訓練方法

### 損失関数
- **事前学習**: **MLM**(マスク 30%、whole word masking、80% [MASK] / 10% ランダム / 10% 維持)。NSP は採用せず。
- **Stage I 微調整**: 双方向 **InfoNCE**(コントラスト学習、ペアの順序を入れ替えた loss も加算)。
- **Stage II 微調整**: ハードネガティブ込みの **拡張 InfoNCE**(positive 1 + negatives 15)。
- **背景**: 長文一般用途の embedding には、まず大規模一般ペアで方向性を学ばせ、その後検索タスク特化の hard negative 学習で精度を伸ばす二段構成が効くという観察に基づく。

### 正則化
- whole word masking と 30% の高めマスク率(汎化のため)
- Activation checkpointing でメモリ削減

### プーリング戦略
- **Mean pooling**(全トークン平均、追加パラメータなし)。

### 訓練パイプライン
- **3 段階**:
  1. **事前学習**: 英語 C4(約 3.65 億文書 / 1700 億トークン)で MLM。512 トークン固定、document packing なし(文書境界は維持)。
  2. **Stage I 微調整(ペア)**: 約 40 種類の多様なソースから集めたテキストペアで双方向 InfoNCE。
  3. **Stage II 微調整(ハードネガ)**: MSMarco / NQ などの検索データに NLI を加え、各バッチに positive 1 + hard negatives 15 を投入。

### 訓練に適用した方式
- **DeepSpeed**(分散学習最適化)
- **FP16 動的混合精度**
- **Activation Checkpointing**(BERT 各層の後ろにチェックポイント挿入)
- **ALiBi 採用** によりポジショナル埋め込みのメモリを削減
- 注: FlashAttention の言及はない(ALiBi 双方向の最適化に独自実装を使用)。

### 訓練データの構成と品質
- **事前学習**: C4(英語、約 365M 文書 / 約 170B トークン)。
- **Stage I**: 約 40 種類のペアデータセット(Wikipedia, StackExchange, Reddit 等を含む多様なソース)。
- **Stage II**: MSMarco, Natural Questions、各種 NLI(SNLI, MultiNLI 等)。
- **長文評価**: PatentClustering, WikiCitiesClustering, NarrativeQA など、長文評価データセットを新規導入。

### ハードネガティブマイニングの手法
- **検索データ**: 既存検索モデルが「似ている」と判定する文書を hard negative として採掘。
- **非検索データ**: positive と hard negative の境界が引きにくいため、ランダムサンプリングで代替。
- **検証**: cross-encoder で「マイニングされた hard negative の関連スコアが正解より低い」ことを必ずチェック。
- **構成**: 1 batch あたり positive 1 + negatives 15。

## モデルの評価

### ベンチマークスコア
- **MTEB(英語、jina-base-v2)**: 平均 **60.37**
  - 比較: text-embedding-ada-002 = 60.99、e5-base-v2 = 61.50
  - **強い項目**: Classification 73.45%、Retrieval 48.45%
- **総合**: OpenAI ada-002 と同等のスコアを **オープンソースで** 達成、長文ドメインでは長文専用評価セット(NarrativeQA 等)で優位性。
- **強み**: 長文(8k)対応かつ ada-002 同等の汎用性能、しかも完全 OSS。
- **弱み**: 平均では同サイズの e5-base-v2 にわずかに劣る項目もあり、多言語対応もなし。

## 論文

### 今回の発表の目新しいポイント
1. **8,192 トークン**(従来 BERT の 16 倍)の汎用 OSS 埋め込みモデルを公開。
2. ALiBi を **双方向対称化** してエンコーダに適用するという技術的工夫(本来は decoder-only 用)。
3. **3 段階訓練レシピ**(MLM → 一般ペア InfoNCE → 検索系 hard negative InfoNCE)を確立。
4. **長文評価データセット**(PatentClustering, WikiCitiesClustering, NarrativeQA)を新規提案。
5. オープンソースで OpenAI ada-002 と同等の MTEB を達成。

### 先行研究(Related Work)の要約
- **古典的トピックモデル**(LSA, LDA): 浅い意味表現に留まり、深い semantic 検索は困難。
- **Sentence-BERT 系**: 埋め込み品質は高いが 512 トークンの制約。長文を扱うにはチャンク分割が必要で、断片化とコスト増大が問題。
- **Contrastive 系(E5, GTE, Jina v1 など)**: 大規模 contrastive で精度を上げたが、長文制約は同じ。
- **長文化アプローチ**: Longformer / BigBird 等は局所 attention で長文化したが、コストや精度のトレードオフがあり embedding には未活用。ALiBi は decoder-only LM での外挿に成功していたが、エンコーダ embedding には未適用だった。
- 本論文は ALiBi をエンコーダに移植して、従来の長文化トレードオフを回避した点が差別化要因。

## まとめ表

| 項目 | 値 |
|--|--|
| 使用したベースモデル | 改造版 BERT(自前で事前学習)|
| 位置埋め込み方式 | 双方向対称 ALiBi(位置埋め込みは廃止) |
| Transformerブロック数 | small=4 / base=12 / large=24 |
| LoRA アダプタの有無 | なし |
| モデルのパラメータ数 | small=33M / base=137M / large≒435M |
| 最大コンテキスト長 | 8,192 トークン(訓練は 512、ALiBi で外挿) |
| 出力ベクトルの次元数 | small=512 / base=768 / large=1024 |
| 学習したタスク | 検索 / 分類 / STS・NLI / クラスタリング / 長文 |
| Instruction Tuning 対応 | なし |
| MRL 対応 | なし |
| 多言語対応 | なし(英語のみ) |
| 損失関数 | MLM(事前学習) / 双方向 InfoNCE / 拡張 InfoNCE(15 hard negatives) |
| プーリング戦略 | Mean pooling |
| 訓練パイプライン | 3段(MLM → 一般ペア InfoNCE → ハードネガ InfoNCE) |
| ハードネガティブマイニング | 検索データ:既存検索モデルで採掘+cross-encoder で検証 / 非検索:ランダム |
| 主要ベンチマーク | MTEB-en base 60.37(ada-002 60.99 と同等) |
| 学習効率化 | DeepSpeed / FP16 mixed precision / Activation Checkpointing |
