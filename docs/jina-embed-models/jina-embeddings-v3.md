# jina-embeddings-v3 モデル情報レポート

**論文**: jina-embeddings-v3: Multilingual Embeddings With Task LoRA (arXiv:2409.10173, 2024年9月、v3=2024年9月)
**著者/所属**: Saba Sturua, Isabelle Mohr, Mohammad Kalim Akram, Michael Günther, Bo Wang, Markus Krimmel, Feng Wang, Georgios Mastrapas, Andreas Koukounas, Nan Wang, Han Xiao (Jina AI)
**URL**: https://arxiv.org/abs/2409.10173

## モデルについて

### 使用したベースモデル
- **値**: **XLM-RoBERTa(改造版)**
- **モデルの特徴**: 100 言語を対象とした多言語マスクド言語モデル。本論文では (1) 長文対応、(2) タスク特化の埋め込み生成、(3) 計算効率の向上を狙って改造を加えている。
- **採用の背景**: 「LLM ベースの埋め込みは精度の伸びが限定的なわりに計算コストが高く実用的でない」という判断から、軽量・多言語強い・既に成熟している XLM-R を出発点に選択している。

### モデルアーキテクチャ
- **位置埋め込み方式**: **RoPE (Rotary Position Embeddings)**。学習時の base frequency は 10,000、推論時には 20,000 に調整して長文への外挿性能を高める。
- **Transformerブロック数**: **24 層**
- **LoRA アダプタの有無**: あり。**rank=4 の LoRA を 5 アダプタ**(4 タスクタイプ用に retrieval.query / retrieval.passage を別々に学習し、ペアで使用)
- **背景**: instruction tuning(E5 系)はプロンプト設計の負担が高いという問題意識から、ベース凍結 + LoRA 切替方式を採用。LoRA はベース総パラメータの 3% 未満。

### モデルのパラメータ数
- **値**: ベース **559M** + LoRA = **約572M**(LoRA は 3% 未満)
- **背景**: OpenAI/Cohere の有償 embeddings と同等以上の精度を、500M 級で達成することを狙ったサイズ選定。

### 最大コンテキスト長
- **値**: **8,192 トークン**
- **背景**: RoPE + 段階的な訓練(まず 100,000 ステップを 512 トークンで、続いて 60,000 ステップを 8,192 トークンに伸ばしてバッチサイズ縮小)で長文化を実現。さらに推論時に RoPE base frequency を 20,000 に上げて外挿。

### 出力ベクトルの次元数
- **値**: 既定 **1,024 次元**(MRL により **32 次元まで** 切り詰め可能)
- **背景**: ストレージ・検索コストの最適化のため、低次元での性能保持を loss レベルで担保。

### 学習したタスク
- 非対称検索(retrieval.query / retrieval.passage)
- セマンティック類似度・対称検索(text-matching)
- 分類(classification)
- クラスタリング/再ランキング(separation)

### Instruction Tuning への対応
- **不採用**(E5 系の instruction-prefix 方式の代替として LoRA を採用)。ユーザーは利用時にアダプタ名を指定するだけ。

### マトリョーシカ表現学習(MRL)の対応
- **あり**。**32〜1024 次元** の任意次元に切り詰め可能。学習時の損失関数を MRL 対応に修正して実現。

### 多言語対応かどうか
- **89 言語**(CulturaX コーパスに基づく)。事前学習データの英語比率は約 20%。明示的な評価対象には中国語、ドイツ語、スペイン語、フランス語、ポーランド語、ロシア語などが含まれる。

## モデルの訓練方法

### 損失関数
- **InfoNCE(双方向)**: ペア微調整の主損失。`L_pairs(B) = L_NCE(B) + L_NCE(B†)`(B† はペアの順序を入れ替えたもの)で双方向に学習。
- **CoSent loss**: text-matching と separation アダプタで、類似度のランク順序を強制(`ζ(q1,p1) > ζ(q2,p2)`)。
- **Extended InfoNCE(triplet)**: classification アダプタで複数負例 `(q, p, n1...n7)` を扱うために拡張。
- **背景**: 単一の InfoNCE では分類・クラスタリング系で不十分なため、タスクの特性に合った損失をアダプタごとに使い分ける設計。

### 正則化
- MRL 対応の損失修正(部分次元での性能を担保)
- LoRA でベース凍結 → ベース知識の破壊を防止
- 合成データで「失敗モード」を補完(後述)

### プーリング戦略
- **Mean pooling**(Sentence-BERT 流)。全出力トークンの平均。

### 訓練パイプライン
- **3 段階**:
  1. **事前学習**: CulturaX(89 言語)に対して MLM。512 トークンで 100K ステップ → 8192 トークンで 60K ステップに延長。
  2. **ペア微調整**: 10 億超のテキストペア(300+ サブデータセット)で双方向 InfoNCE。mean pooling 層を学習。
  3. **タスク別 LoRA**: 5 つの LoRA(rank=4)をそれぞれ独立に学習(retrieval.query と retrieval.passage はペアで学習)。

### 訓練に適用した方式
- **FlashAttention 2** を統合
- **Activation Checkpointing** でメモリ削減
- **DeepSpeed** で分散学習
- RoPE base frequency の段階調整(訓練 10k → 推論 20k)

### 訓練データの構成と品質
- **事前学習**: CulturaX、英語約 20%。
- **ペア微調整**: 1B+ ペア、300+ サブデータセット。構文的重複除去フィルタリング。
- **分類**: 感情分析、意図分類、記事カテゴリ等のラベル付きデータ。
- **Text matching**: STS12, SICK + WMT19 / MADLAD-3B での機械翻訳版。
- **検索**: MS-MARCO, Natural Questions(BGE-large と BM25 でハードネガティブを採掘)。
- **Separation**: 少量のクラスタリング付きデータ + ペア学習データで補完。
- **失敗モード補完**: 4 種の検索失敗モード(誤った構文類似度、固有表現の誤読、極性疑問、低品質文書)に対して合成データを生成。

### ハードネガティブマイニングの手法
- 検索系では **BGE-large** と **BM25** を用いて hard negatives をマイニング。アノテーションがないデータセットへの後付けマイニングに重点。

## モデルの評価

### ベンチマークスコア
- **MTEB(英語、jina-embeddings-v3)**:
  - Classification: **82.58%**
  - STS: **85.80%**
  - Retrieval (nDCG@10): **53.87%**
  - Overall: **65.52**(text-embedding-3-large の 64.60 を上回る)
- **Multilingual MTEB**: **64.44**(multilingual-e5-large の 59.58 を上回る)
- **LongEmbed MTEB(長文)**: 平均 nDCG@10 = **70.39%**(比較対象中トップ)
- **強み**: 500M 級で OpenAI text-embedding-3-large(プロプライエタリ)を上回る、長文・多言語両立。
- **弱み**: 純粋な検索 nDCG では大型 LLM ベース(7B)系には及ばない部分もある。

## 論文

### 今回の発表の目新しいポイント
1. **タスク別 LoRA を埋め込みモデルに本格適用** した最初の代表事例(instruction-based 手法の代替)。アダプタはベースの 3% 未満。
2. 検索の **失敗モードを 4 つに分類** し、それぞれに合成データを当てて補完する分析的アプローチ。
3. **MRL + 長文(8192) + 多言語(89言語) + LoRA** を 1 モデルに統合。
4. XLM-RoBERTa を改造して RoPE 化することで、エンコーダ系でも 8k 長文を扱える設計を実証。
5. 500M 級で OpenAI text-embedding-3-large を上回るコスパを示した。

### 先行研究(Related Work)の要約
- **汎用テキスト埋め込み**: Sentence-BERT, SimCSE, GTR 系など。マルチタスク contrastive で精度向上を狙うが、多言語・長文の両立は弱い。
- **多言語埋め込み**: multilingual-E5, mE5, LaBSE 等。XLM-R 系を拡張するが、シーケンス長が 512 に縛られる例が多い。
- **タスク特化の手法**: E5 / BGE 系の **instruction-based** モデル、または軽量アダプタを使う手法。Instruction-based 手法はプロンプト設計の負担が大きい。
- 本論文はこれらを統合し、**ベース凍結 + LoRA**(プロンプトいらずでタスク切替) という選択肢を示した。

## まとめ表

| 項目 | 値 |
|--|--|
| 使用したベースモデル | XLM-RoBERTa(RoPE 等の改造あり) |
| 位置埋め込み方式 | RoPE(訓練 base=10k / 推論 base=20k) |
| Transformerブロック数 | 24 |
| LoRA アダプタの有無 | あり(rank=4、5アダプタ/4タスクタイプ) |
| モデルのパラメータ数 | 559M base + LoRA ≒ 572M(LoRA は <3%) |
| 最大コンテキスト長 | 8,192 トークン |
| 出力ベクトルの次元数 | 1,024(MRL で 32 まで) |
| 学習したタスク | 検索(query/passage)、STS、分類、クラスタリング/再ランキング |
| Instruction Tuning 対応 | 不採用(LoRA で代替) |
| MRL 対応 | あり(32〜1024) |
| 多言語対応 | 89言語(CulturaX)、英語比率約20% |
| 損失関数 | 双方向 InfoNCE / CoSent / 拡張 InfoNCE(タスク別) |
| プーリング戦略 | Mean pooling |
| 訓練パイプライン | 3段(MLM 事前学習 → ペア微調整 → タスク別 LoRA) |
| ハードネガティブマイニング | BGE-large + BM25 でマイニング |
| 主要ベンチマーク | MTEB-en 65.52 / MMTEB 64.44 / LongEmbed 70.39 |
| 学習効率化 | FlashAttention 2 / Activation Checkpointing / DeepSpeed |
