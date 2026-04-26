# jina-embeddings-v4 モデル情報レポート

**論文**: jina-embeddings-v4: Universal Embeddings for Multimodal Multilingual Retrieval (arXiv:2506.18902, 2025年6月、v3 = 2025年7月)
**著者/所属**: Michael Günther, Saba Sturua, Mohammad Kalim Akram, Isabelle Mohr, Andrei Ungureanu, Bo Wang, Sedigheh Eslami, Scott Martens, Maximilian Werk, Nan Wang, Han Xiao (Jina AI)
**URL**: https://arxiv.org/abs/2506.18902

## モデルについて

### 使用したベースモデル
- **値**: **Qwen2.5-VL-3B-Instruct**(3.8B パラメータの視覚言語モデル)
- **モデルの特徴**: 画像をトークン列にエンコードし、テキストと同じ Transformer に流す統合型 VLM。
- **採用の背景**: CLIP 系の dual-encoder ではテキストエンコーダと画像エンコーダが分離しており「モダリティギャップ」が大きい。Qwen2.5-VL のように画像→トークン列→単一 LLM で処理する設計は、テキストと画像を同じ意味空間にマップしやすく、視覚的に情報密度の高い文書(チャート、表、ウェブスクリーンショット等)の検索に強い。実測でクロスモーダル整合スコアは 0.71(OpenAI CLIP の 0.15 を大幅に上回る)。

### モデルアーキテクチャ
- **位置埋め込み方式**: 本論文では明示なし(ベース Qwen2.5-VL は RoPE 系を採用)。
- **Transformerブロック数**: 本論文では明示なし。
- **LoRA アダプタの有無**: あり。**3 種類のタスク特化 LoRA(各 60M パラメータ)** をベース凍結のまま装着:
  - Asymmetric Query-Document Retrieval
  - Semantic Similarity / Symmetric Retrieval(Text Matching)
  - Code Retrieval
- **背景**: ベース VLM の知識を破壊せずタスク間最適化を切り分けるための設計。LoRA のオーバーヘッドはベースの約 2% 未満。
- 単一ベクトル出力に加えて、トークン列をそのまま射影して **マルチベクトル(late-interaction)出力** を同時生成できる、デュアル出力アーキテクチャを採用。

### モデルのパラメータ数
- **値**: ベース **3.8B** + LoRA **60M × 3** ≒ **約3.98B**
- **背景**: 既存 SOTA(ColPali / VDR / e5-mistral 等)に匹敵する規模を確保しつつ、LoRA で軽量に拡張する戦略。

### 最大コンテキスト長
- **値**: **テキスト 32,768 トークン**(画像入力にも対応)
- **背景**: 長文文書および複雑な visual document を 1 ショットで処理することを意図。

### 出力ベクトルの次元数
- **値**:
  - 単一ベクトル: **2,048 次元**(MRL で 128 まで切り詰め可)
  - マルチベクトル: トークンあたり **128 次元**
- **背景**: 同じモデルで dense retrieval(高速・低コスト)と late-interaction retrieval(高精度)の両方を提供する設計。

### 学習したタスク
- 非対称検索(query-document)
- 対称検索 / セマンティック類似度
- マルチモーダル検索(画像+テキスト)
- 視覚的に情報密度の高い文書検索(チャート/表/PDF/Web スクリーンショット)
- コード検索
- 多言語検索

### Instruction Tuning への対応
- 「task-specific instruction を必要としない」 と明記。LoRA の切替で済むためプロンプト設計の負担が低い。

### マトリョーシカ表現学習(MRL)の対応
- **あり**。2,048 次元から **128 次元まで** 段階的に切り詰め可能。次元順序は意味的重要度で並ぶ。

### 多言語対応かどうか
- **多言語対応**(ベース Qwen2.5-VL に依拠)。Jina-VDR ベンチマーク内で確認できる訓練/評価言語は ar, de, en, es, fr, hi, hu, ja, ko, nl, pt, ru, th, vi, zh など、最大 20 言語規模。

## モデルの訓練方法

### 損失関数
- **InfoNCE**: 単一ベクトル/マルチベクトルの双方に適用するコントラスト学習の主損失。
- **KL Divergence**: 単一ベクトルとマルチベクトルの誤差分布のずれを補正。
- **Matryoshka Loss**: 切り詰め可能性を担保。
- **CoSENT Loss**: text-matching アダプタで類似度スコアの順序学習に使用。
- **背景**: 1 つのバックボーンから dense / late-interaction の両系統を取り出すため、それぞれの出力に loss をかけつつ、両者を整合させる KL を追加するハイブリッド設計。

### 正則化
- LoRA(低ランク化) + ベース凍結 → 破滅的忘却防止
- Matryoshka loss → 次元の意味階層化
- KL → 単一/マルチの整合性

### プーリング戦略
- **単一ベクトル**: 最終層への **mean pooling**
- **マルチベクトル**: プーリングを行わず、各トークン埋め込みを射影層で 128 次元に落とす

### 訓練パイプライン
- **2 段階**:
  1. **Pair Training**: テキストペア + テキスト×画像ペアを使い、単一 LoRA を contrastive で学習。Single/Multi 双方の損失を同時適用。
  2. **Task-Specific Adaptation**: Phase 1 のアダプタを 3 つに複製し、Retrieval / Text-matching / Code それぞれをタスクに合った損失とデータで微調整。

### 訓練に適用した方式
- バックボーン重みは完全に凍結し、LoRA アダプタと射影層のみを学習。
- FlashAttention/FSDP/DeepSpeed/bf16 などの実装詳細は本文には明示されていない。

### 訓練データの構成と品質
- **300+ ソース** のテキスト/マルチモーダルペア。
- テキストは jina-embeddings-v3 と同じフィルタリング基準。
- マルチモーダル: ウェブスクリーンショット、レンダリング済み Markdown、チャート、表、その他「in the wild」資料。
- セマンティック類似度: STS12, SICK 等。
- コード: CodeSearchNet, APPS, StackExchangeQA 等。
- 詳細件数は非公開。

### ハードネガティブマイニングの手法
- 非対称検索アダプタでは「query / matching doc / 意味的に近いが正解ではない doc」のトリプレット形式で hard negatives を投入。
- マルチモーダル側では Wiki-SS、VDR multilingual 等の既存データセットから負例を取得し、追加収集データで補強。

## モデルの評価

### ベンチマークスコア
- **Jina-VDR(マルチベクトル)**: avg nDCG@5 = **81.52**(SOTA)
- **ViDoRe(マルチベクトル)**: avg nDCG@10 = **90.17**(専用モデルを上回る)
- **MTEB-en Retrieval**: nDCG@10 = **55.97**
- **MMTEB Retrieval**: nDCG@10 = **66.49**
- **CoIR (Code Retrieval)**: nDCG@10 = **71.59**(voyage-code 77.33 にはやや劣る)
- **強み**: 視覚的文書(チャート/表/Web スクショ) の検索で大幅 SOTA。マルチモーダル+多言語+長文をワンモデル化。
- **弱み**: 純粋コード検索では voyage-code 等の特化モデルに一歩譲る。

## 論文

### 今回の発表の目新しいポイント
1. **VLM(Qwen2.5-VL-3B)を埋め込みモデルのバックボーンに据えた** 真の統合型マルチモーダル埋め込み。CLIP 系 dual-encoder の「モダリティギャップ」を 0.71 vs 0.15 と劇的に縮小。
2. **単一ベクトル(dense)と マルチベクトル(late-interaction)を同一モデルから同時出力** する設計。
3. **3 つのタスク別 LoRA** で retrieval / similarity / code を切り分け、instruction-prompt 不要を実現。
4. **Jina-VDR ベンチマーク** を新規提案。30+ visually rich document タスク、複数言語・複数文書タイプ・複数クエリ形式を網羅。
5. ViDoRe ベンチマークを大幅に拡張(英仏・チャート/表中心 → 多言語かつ多文書タイプ)。

### 先行研究(Related Work)の要約
- **CLIP / jina-clip-v2 など**: dual-encoder で画像とテキストを別々のエンコーダに通すため、モダリティギャップが残り、視覚的文書検索で性能頭打ち。
- **Qwen2.5-VL / 他 VLM**: もともと汎用 VLM として優秀だが、retrieval embedding 用には微調整されていない。
- **ColBERT / ColPali**: late-interaction で精度を稼ぐが、専用モデルとして単一ベクトル検索や多タスク汎用性に欠ける。
- **法律/コード等のドメイン特化埋め込み**: 高精度だが汎用性が低く、複数ドメインを横断するアプリには不向き。
- **ViDoRe ベンチマーク**: 視覚文書評価の事実上の標準だが、英仏 QA 中心で多言語・多文書タイプには不足。
- 本論文はこれらをすべて「1 つの VLM ベースモデル + LoRA 切替 + デュアル出力」で統合し、既存ベンチマークを大幅に拡張した。

## まとめ表

| 項目 | 値 |
|--|--|
| 使用したベースモデル | Qwen2.5-VL-3B-Instruct |
| 位置埋め込み方式 | 記載なし(ベース Qwen2.5-VL に準拠) |
| Transformerブロック数 | 記載なし |
| LoRA アダプタの有無 | あり(3タスク × 各60M、ベース凍結) |
| モデルのパラメータ数 | ベース3.8B + 60M×3 LoRA ≒ 約3.98B |
| 最大コンテキスト長 | テキスト 32,768 トークン(画像入力可) |
| 出力ベクトルの次元数 | 単一2048 / マルチ128(MRL で128まで切り詰め可) |
| 学習したタスク | 検索/STS/コード検索/マルチモーダル/visually-rich文書検索 |
| Instruction Tuning 対応 | 不要(LoRA 切替で代替) |
| MRL 対応 | あり(2048→128) |
| 多言語対応 | あり(Qwen2.5-VL ベース、Jina-VDR で15+言語実証) |
| 損失関数 | InfoNCE + KL + Matryoshka + CoSENT(タスク別) |
| プーリング戦略 | 単一: mean pooling / マルチ: トークン射影(プーリングなし) |
| 訓練パイプライン | 2段(Pair Training → タスク別LoRA分岐) |
| ハードネガティブマイニング | トリプレット形式、Wiki-SS/VDR等から取得 |
| 主要ベンチマーク | Jina-VDR 81.52 / ViDoRe 90.17 / MTEB-en 55.97 / MMTEB 66.49 / CoIR 71.59 |
| 特記事項 | 単一ベクトル+マルチベクトル(late-interaction)の同時出力 |
