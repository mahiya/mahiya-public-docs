# jina-embeddings-v1 モデル情報レポート

**論文**: Jina Embeddings: A Novel Set of High-Performance Sentence Embedding Models (arXiv:2307.11224, 2023年7月、最終改訂 2023年10月)
**著者/所属**: Michael Günther, Louis Milliken, Jonathan Geuter, Georgios Mastrapas, Bo Wang, Han Xiao (Jina AI)
**URL**: https://arxiv.org/abs/2307.11224

## モデルについて

### 使用したベースモデル
- **値**: **T5(エンコーダ部分のみ)**。具体的には zero-shot T5 系の 3 サイズ(small / base / large)。Encoder-Decoder 全体ではなく、**T5 エンコーダだけを抜き出して** 使用。
- **モデルの特徴**: T5 はもともと「すべてを text-to-text に統一する」というマルチタスク事前学習を施しており、BERT より幅広い下流タスク経験を持つ。
- **採用の背景**: 著者は「T5 の事前学習が混合された下流タスク群で行われているため、訓練戦略の有効性を正確に評価できる」と説明している。BERT より T5 のほうが、本論文が提案するペア/トリプレット学習レシピの検証に向いている、という判断。

### モデルアーキテクチャ
- **位置埋め込み方式**: 本文では明示なし(ベース T5 は **相対位置バイアス** を採用)。
- **Transformerブロック数**: 本文では明示なし(ベース T5 のサイズに準ずる)。
- **LoRA アダプタの有無**: なし。
- **背景**: 「ベースモデルを丸ごと微調整しつつ、ペア → トリプレットの 2 段階で学習する」というシンプルな設計。タスク別アダプタや prompt 切替は v3 以降で導入される。

### モデルのパラメータ数
- **値**:
  - jina-small-v1: **35M**
  - jina-base-v1: **110M**
  - jina-large-v1: **330M**
  - (本文では追加 2 サイズが計画段階として言及されているが、本論文時点では未公開)
- **背景**: 同サイズ帯の Sentence-BERT/Sentence-T5 と直接比較できるよう、典型的な small/base/large の階層を踏襲。

### 最大コンテキスト長
- **値**: **512 トークン**(ハイパーパラメータ表に明記)
- **背景**: 旧来 BERT/T5 系の標準長。長文化は v2 以降の課題として残されている。

### 出力ベクトルの次元数
- **値**:
  - small: **512 次元**
  - base: **768 次元**
  - large: **1,024 次元**(Table 1 による)
- **背景**: ベースモデルの隠れ状態次元をそのまま使用。MRL は未対応。

### 学習したタスク
- セマンティック類似度 (STS)
- 検索(Retrieval)
- ペアワイズマッチング(QA, 重複検出)
- (副次目的)否定文の理解

### Instruction Tuning への対応
- **なし**。

### マトリョーシカ表現学習(MRL)の対応
- **なし**。

### 多言語対応かどうか
- **英語のみ**。fastText で言語識別し、非英語データを除外している。

## モデルの訓練方法

### 損失関数
- **Stage 1(ペア学習)**: **双方向 InfoNCE**(温度 τ = 0.05)。
- **Stage 2(トリプレット学習)**: 3 種を組み合わせた複合損失:
  - 拡張 InfoNCE(追加負例つき)
  - 逆方向 InfoNCE
  - **Triplet margin loss**(マージン ε = 0.05)
- **背景**: 純粋な InfoNCE のみではハードネガとの距離関係が安定しないため、triplet margin を加えて anchor / positive / negative の幾何的関係を直接強制する設計。

### 正則化
- 重複除去・言語識別・整合性フィルタによる前処理(高品質ペアだけを残す)
- cross-encoder によるトリプレット validation(後述)

### プーリング戦略
- **Mean pooling**(token embeddings の平均で固定長表現を生成)。

### 訓練パイプライン
- **2 段階**:
  1. **Pairwise stage**: フィルタリング後の **3.85 億ペア**(初期 16 億から削減)を双方向 InfoNCE で学習。
  2. **Triplet stage**: フィルタリング後の **約 92.7 万トリプレット**(初期 1.13M から削減)で複合損失。最終アダプタはここで形成。

### 訓練に適用した方式
- **DeepSpeed Stage 2**(分散学習)
- **A100 GPU × 8** を使用
- **32-bit 精度**(混合精度 mixed-precision は本論文では使っていない、と明記)
- FlashAttention の言及はなし

### 訓練データの構成と品質
- **32 個のデータセット** を統合。E コマース・QA・Web 検索・重複検出の 4 ドメイン。
- **フィルタリング工程**(本論文の核心の一つ):
  - 重複除去 (de-dup)
  - 言語識別 (fastText で英語のみ)
  - **all-MiniLM-L6-v2** による整合性フィルタ(意味的に乖離するペアを除外)
- 結果として 1.6B → 385M ペア / 1.13M → 927k トリプレットに精選。
- **新規 negation データセット**: SNLI の正例ペアに対し、**GPT-3.5 で生成した negation 文** を負例として追加した triplet データセット。anchor / entailment / negative の 3 つ組で、negative は entailment を文法的に否定したものとなる。

### ハードネガティブマイニングの手法
- **cross-encoder(ms-marco-MiniLM-L-6-v2)** を使ったスコア検証。
- 条件: `r(q, p) − r(q, n) > κ`(κ = 0.2)を満たすトリプレットだけを残す。
- これにより「曖昧な negative」を除外し、本当に難しい hard negatives だけで学習できる。

## モデルの評価

### ベンチマークスコア
- **MTEB**(全タスク):
  - jina-base-v1 の **STS 平均**: **79.93**
  - jina-large-v1 は retrieval (nDCG@10) で 1.2B パラメータ級モデルと同等。
  - 同サイズの sentence-T5/sentence-BERT 系を上回る。
- **Negation データセット**(本論文の独自評価):
  - jina-large-v1: **EasyNegation 98.2% / HardNegation 65.4%**(triplet 学習の効果が顕著)。
- **強み**: 同サイズ帯の Sentence-BERT/Sentence-T5 を一貫して上回る。トリプレット学習で否定文の理解が大幅改善。
- **弱み**: 著者自身が認めている通り、**MTEB の Classification と Clustering タスクは弱い**。サンプリング比率もヒューリスティックに依存。

## 論文

### 今回の発表の目新しいポイント
1. **データクレンジング重視**: 16 億ペア → 3.85 億 / 1.13M トリプレット → 92.7 万、と大幅に削った高品質データで学習。「データ量より品質」を主張。
2. **2 段階学習レシピ**(ペア InfoNCE → トリプレット 複合損失)を確立。
3. **Negation データセット** を新規公開。SNLI と GPT-3.5 を組み合わせ、否定文の理解を測定する EasyNegation / HardNegation 2 指標を提案。
4. **T5 エンコーダのみを使う** 設計を採用し、Sentence-T5 / GTR との直接比較で優位を示した。
5. cross-encoder を使った triplet validation という品質ゲートを提示。

### 先行研究(Related Work)の要約
- **Sentence-BERT (SBERT)**: BERT を NLI で微調整して文埋め込みを獲得。汎用性は高いが、否定文の扱いは弱い。
- **Sentence-T5 / GTR**: T5 ベースの埋め込み。大規模 contrastive 事前学習 + 検索系微調整で SOTA を更新するが、訓練データに対する考察は浅い。
- **共通の枠組み**: Contrastive 事前学習 + ハードネガティブで微調整、というレシピが標準化されつつあった。
- **限界**: (a) どんなデータ前処理が有効か、(b) どの損失関数が最適か、(c) スケーリングの効果、についての系統的検証が不十分。
- 本論文はこれらの問いに答えるべく、データ品質・損失関数選択・モデルサイズの効果を体系的に検証し、特に「より少ないデータでも高品質に整えれば SOTA に届く」ことを示した。

## まとめ表

| 項目 | 値 |
|--|--|
| 使用したベースモデル | T5 のエンコーダ部分のみ(small / base / large) |
| 位置埋め込み方式 | 記載なし(ベース T5 は相対位置バイアス) |
| Transformerブロック数 | 記載なし(ベース T5 に準拠) |
| LoRA アダプタの有無 | なし |
| モデルのパラメータ数 | small=35M / base=110M / large=330M |
| 最大コンテキスト長 | 512 トークン |
| 出力ベクトルの次元数 | small=512 / base=768 / large=1024 |
| 学習したタスク | STS / 検索 / 重複検出・QA / 否定文理解 |
| Instruction Tuning 対応 | なし |
| MRL 対応 | なし |
| 多言語対応 | なし(英語のみ、fastText で言語フィルタ) |
| 損失関数 | Stage1: 双方向 InfoNCE(τ=0.05) / Stage2: 拡張 InfoNCE + 逆方向 InfoNCE + Triplet margin(ε=0.05) |
| プーリング戦略 | Mean pooling |
| 訓練パイプライン | 2段(ペア InfoNCE → トリプレット 複合損失) |
| ハードネガティブマイニング | cross-encoder (ms-marco-MiniLM-L-6-v2) 検証、`r(q,p)-r(q,n)>0.2` |
| 主要ベンチマーク | MTEB-en STS(base)79.93、Negation: large EasyNeg 98.2 / HardNeg 65.4 |
| 学習効率化 | DeepSpeed Stage 2 / A100×8 / 32-bit精度(mixed precisionなし) |
| 特記事項 | データクレンジング重視(16億ペア→3.85億)、negation triplets を新規公開 |
