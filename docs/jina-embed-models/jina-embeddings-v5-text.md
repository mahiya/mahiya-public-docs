# jina-embeddings-v5-text モデル情報レポート

**論文**: jina-embeddings-v5-text: Task-Targeted Embedding Distillation (arXiv:2602.15547, 2026年2月)
**著者/所属**: Mohammad Kalim Akram, Saba Sturua, Nastia Havriushenko, Quentin Herreros, Michael Günther, Maximilian Werk, Han Xiao (Jina AI)
**URL**: https://arxiv.org/abs/2602.15547

## モデルについて

本論文は2つのコンパクトモデルを同時に発表している。共通設計と差分は下記の通り。

### 使用したベースモデル
- **値**:
  - `jina-embeddings-v5-text-small`: **Qwen3-0.6B-Base** (約596M)
  - `jina-embeddings-v5-text-nano`: **EuroBERT-210M** (約212M)
- **モデルの特徴**: Qwen3-0.6B は Qwen3 系の最小デコーダ LM、EuroBERT は欧州言語に強いエンコーダ系 BERT。
- **採用の背景**: 「コンパクトかつ効率的な埋め込みを得たい」という主目的に対し、軽量かつ多言語性のあるバックボーンを2系統用意することで、デコーダ型(small) と エンコーダ型 (nano) で蒸留戦略の有効性を比較できる構成にしている。教師モデル Qwen3-Embedding-4B の知識を圧縮するためのターゲットとして選択。

### モデルアーキテクチャ
- **位置埋め込み方式**: RoPE (Rotary Positional Embeddings)。長文外挿に対応するため、訓練時の RoPE θ を small=1M、nano=250K と低めに設定し、推論時の長コンテキスト化に備えている。
- **Transformerブロック数**: 本文では明示なし(ベースモデルに準ずる)。
- **LoRA アダプタの有無**: あり。**4 種類のタスク特化 LoRA(rank=32, alpha=32)** を装着:
  - Asymmetric Retrieval
  - Text Matching / STS
  - Clustering
  - Classification
- **背景**: 1モデルでマルチタスク蒸留を行うとタスク間の最適化目標が衝突する問題を、ベース重みを凍結しタスクごとに小さな LoRA を切り替えることで回避している(Jasper-Token-Compression との差別化点)。

### モデルのパラメータ数
- **値**:
  - small: 596M (base) + 4 × 20.2M (LoRA) ≒ **約677M**
  - nano: 212M (base) + 4 × 6.7M (LoRA) ≒ **約239M**
- **背景**: 「教師である Qwen3-Embedding-4B を 1/6〜1/17 程度に圧縮しつつ、MTEB v2 で教師に匹敵する精度を出すこと」をターゲットにしたサイズ選定。

### 最大コンテキスト長
- **値**: **32,000 トークン**(両モデル共通)
- **背景**: Stage 1 蒸留の後半で 4,096 トークンまでの長文サンプルを使う「long-context training」フェーズ(6,500 ステップ)を実施。さらに RoPE θ を小さくして 32k まで外挿できるようにしている。

### 出力ベクトルの次元数
- **値**: small = **1,024 dim**、nano = **768 dim**
- **背景**: MRL を併用しているため 256 次元程度まで切り詰めても精度が大きく落ちない。バイナリ量子化下でもロバストとされる。

### 学習したタスク
- 非対称検索 (Asymmetric Retrieval)
- セマンティック類似度 (STS / Text Matching)
- クラスタリング
- 分類
- 長文書検索(Stage 1 後半)

### Instruction Tuning への対応
- 軽量なプレフィックス方式のみ。学生側は `Query:` / `Document:` の最小プロンプト、教師側は汎用 web 検索 instruction を付与。重い instruction-tuning は行わず、LoRA で代替している。

### マトリョーシカ表現学習(MRL)の対応
- **あり**。Kusupati ら (2022) の MRL を Stage 1 蒸留に組み込み、出力次元を 256 まで切り詰めても性能を維持できる設計。

### 多言語対応かどうか
- **多言語対応**。
  - small: ベースの Qwen3-0.6B が 119 言語をリスト。
  - nano: ベースの EuroBERT が主要 15 言語(欧州中心+グローバル)。
  - 訓練データは 30 言語以上 / 300+ データセットからサンプリング。低資源言語については機械翻訳済みデータを活用。

## モデルの訓練方法

### 損失関数
- **Stage 1 (蒸留)**: 教師埋め込みと学生埋め込みの **コサイン距離ロス**(線形射影 ψ で学生を教師空間にマップ)+ Score-based 蒸留(softmax 化した類似度行列の MSE) をablationで比較。
- **Stage 2 (LoRA タスク学習)**:
  - Retrieval: **InfoNCE**(in-batch 負例 + ハードネガティブ、温度スケール)
  - STS: **CoSENT**(リストワイズで類似度順序を保つ)
  - Classification: Relational KD レギュラライザ付き InfoNCE
- **背景**: タスクごとに最適な損失が違うので、純粋な distillation や純粋な contrastive 一辺倒では精度頭打ちになる、という問題意識。本論文の核心的貢献は「蒸留 + タスク別 contrastive のハイブリッド」設計。

### 正則化
- **GOR (Global Orthogonal Regularizer)**: 非マッチペアの類似度を抑え、埋め込み空間での均一分布を促進。
- **Matryoshka loss**: 部分次元での性能を担保。
- **Relational Knowledge Distillation**: 分類アダプタにおけるフィーチャー崩壊防止。
- **モデル平均化**: LoRA 学習の最終チェックポイントと早期チェックポイントを平均してロバスト化。

### プーリング戦略
- **Last-token pooling**(EOS トークンの埋め込みを使用)。デコーダ型 small の自然な選択であり、エンコーダ型 nano にも統一。

### 訓練パイプライン
- **2 段階**:
  1. **Stage 1 — 汎用蒸留** (50,000 ステップ)。30 言語超 / 300+ データセットの一般ペアで蒸留。後半 6,500 ステップで 4,096 トークンの長文学習。
  2. **Stage 2 — タスク別 LoRA 学習**(ベース凍結):
     - Retrieval LoRA: 8,000 ステップ
     - STS LoRA: 20,000 ステップ
     - Clustering LoRA: 20,000 ステップ
     - Classification LoRA: 30,000 ステップ

### 訓練に適用した方式
- 本文では FlashAttention/FSDP/DeepSpeed/bf16 などの実装最適化は明示されていない。
- RoPE θ の段階的調整(訓練時と推論時で異なる θ)が長コンテキスト対応の中心テクニック。

### 訓練データの構成と品質
- 30+ 言語、300+ データセットから収集した大規模ペアコーパス。
- STS12 / SICK 等の semantic similarity データ、パラレル翻訳・パラフレーズ。
- 長文用に **合成ドキュメント、書籍チャプター、LLM生成クエリ** を追加。
- 分類データは multilabel → single-label に変換して投入。
- 三つ組(query / positive / hard negative)も併用。
- 低資源言語は機械翻訳データで補完。Ablation では filtered S2ORC を使用。

### ハードネガティブマイニングの手法
- InfoNCE の負例集合に「in-batch 内の非マッチ文書」+「事前にマイニングした hard negatives(意味的に近いが正解ではない)」 を統合する標準的な方式。マイニング元モデルの明示はないが、教師である Qwen3-Embedding-4B 系統と推察される。

## モデルの評価

### ベンチマークスコア
- **Multilingual MTEB v2(Table 2 平均)**:
  - j-v5-text-small: **67.0** / j-v5-text-nano: **65.5**
  - 比較: jina-v3 = 58.4、snowflake-l-v2 = 57.0、multilingual-e5-large-instruct = 63.2
- **English MTEB v2(Table 3 平均)**:
  - j-v5-text-small: **71.7**(同サイズ帯トップ)
  - j-v5-text-nano: **71.0**
  - 比較: Qwen3-0.6B (instruction-tuned) = 70.5
- **タスク別(small/nano)**:
  - Classification 90.4 / 89.7
  - Clustering 85.0 / 84.7
  - Retrieval 82.9 / 81.9
  - STS 78.9 / 78.2
  - Reranking 42.0 / 41.3
- **検索系まとめ(Table 4)**: BEIR で small=66.84、LongEmbed で 66.39、MTEB Multilingual Retrieval で 64.88(教師 Qwen3-0.6B の 64.65 を上回る)。
- **強み**: 200M〜700M クラスで多言語+長文+量子化耐性をすべて両立。**弱み**: Reranking は依然 40 点台で、cross-encoder 型を凌駕するわけではない。

## 論文

### 今回の発表の目新しいポイント
1. **蒸留 × タスク別 contrastive のハイブリッド** という新しい訓練レシピを提案し、純 distillation/純 contrastive を上回ることを実証。
2. **タスク別 LoRA アダプタ** によりマルチタスク埋め込みの最適化衝突問題を解決。
3. **小型 (212M) と中型 (596M) の二系統** をエンコーダ系/デコーダ系の異なるバックボーンで構築、両方を公開。
4. **長文・多言語・量子化耐性・MRL** を 1 モデルで両立するレシピを示した。
5. embedding-based vs. score-based 蒸留を比較した ablation を提示。

### 先行研究(Related Work)の要約
- **E5 / BGE / GTE 系**: in-batch contrastive 主体で大規模事前学習を行うが、モデルサイズが大きくなりがちで、コンパクト化の余地が残る。
- **Jasper-Token-Compression**: 蒸留 + contrastive の 2 段階パイプラインを採るが、既存埋め込みモデルを単に微調整するだけで、タスクごとの最適化方針を分けない。本論文は LoRA を使ってこの分離を実現した点が差別化要因。
- **multilingual-e5 / jina-embeddings-v3**: マルチ言語対応はあるが long-context や量子化耐性は十分でない。
- **LongEmbed 系**: 長文特化だがマルチタスク汎用性に欠ける。
- 本論文は「コンパクトな多言語・長文・MRL 対応モデルを蒸留で実現する」というニッチを狙い、教師 Qwen3-Embedding-4B を活用してそれを達成した。

## まとめ表

| 項目 | 値 |
|--|--|
| 使用したベースモデル | small: Qwen3-0.6B-Base / nano: EuroBERT-210M |
| 位置埋め込み方式 | RoPE(訓練時 θ small=1M, nano=250K) |
| Transformerブロック数 | 記載なし(ベースに準拠) |
| LoRA アダプタの有無 | あり(4タスク × rank32/alpha32) |
| モデルのパラメータ数 | small ≒ 677M(596M base+4×20.2M LoRA) / nano ≒ 239M(212M+4×6.7M) |
| 最大コンテキスト長 | 32,000 トークン |
| 出力ベクトルの次元数 | small 1024 / nano 768(MRL で 256 まで縮約可) |
| 学習したタスク | 検索・STS・分類・クラスタリング・長文検索 |
| Instruction Tuning 対応 | 軽量プレフィックス(Query:/Document:)のみ、本格 IT は LoRA で代替 |
| MRL 対応 | あり(256 次元まで安定) |
| 多言語対応 | small=119言語(Qwen3 由来) / nano=15欧州中心+α、訓練は30言語超 |
| 損失関数 | Stage1: コサイン距離蒸留 / Stage2: InfoNCE, CoSENT, Relational KD |
| プーリング戦略 | Last-token pooling(EOS) |
| 訓練パイプライン | 2段(Stage1 汎用蒸留50k step → Stage2 タスク別LoRA) |
| ハードネガティブマイニング | in-batch + 事前マイニングした hard negatives を併用 |
| 主要ベンチマーク | MMTEB v2: small 67.0 / nano 65.5、MTEB-en: small 71.7、BEIR: 66.84、LongEmbed: 66.39 |
