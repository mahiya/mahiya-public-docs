# japanese-splade-v2 モデル情報レポート

**モデル名**: hotchpotch/japanese-splade-v2
**公開**: 2024-12 (HuggingFace Hub)
**関連技術論文**: SPLADE v2: Sparse Lexical and Expansion Model for Information Retrieval (Formal et al., arXiv:2109.10086, 2021-09)
**開発者/関連記事**: Yuichi Tateno (hotchpotch / secon)
**モデル URL**: https://huggingface.co/hotchpotch/japanese-splade-v2
**技術レポート**: https://secon.dev/entry/2024/10/23/080000-japanese-splade-tech-report/
**リリース記事**: https://secon.dev/entry/2024/12/19/100000-japanese-splade-v2-release/

> 本モデルは単独の学術論文で発表されたモデルではなく、SPLADE v2 の方法論を日本語 BERT 上に適用した派生モデルです。本レポートでは (a) SPLADE v2 の原著論文 (Formal et al., 2021) と (b) 開発者 hotchpotch 氏のテクニカルレポート・モデルカードを組み合わせて整理しています。

## モデルについて

### 開発組織
- **値**: 個人開発者 hotchpotch (Yuichi Tateno, 通称 secon)
- **背景**: 日本語のスパース検索モデル系列 (`japanese-splade-base-v1` → `japanese-splade-base-v1_5` → `japanese-splade-v2`) を継続的に公開しているほか、`japanese-reranker-tiny-v2` などのリランカーも公開している。関連記事はブログ secon.dev に集約されている。

### 公開年月
- **値**: 2024-12 (v2 のリリース記事が 2024-12-19 付け)
- **背景**: 2024-10 に japanese-splade-base-v1 とテクニカルレポートが出たあと、過剰スパースの是正や再蒸留を行い v1_5 を経て同年 12 月に v2 をリリース。わずか 2 か月のスパンで一気にアップデートしている。

### 使用したベースモデル
- **値**: `hotchpotch/japanese-splade-base-v1_5` (その更に前身は `hotchpotch/ruri-pt-base-retromae` → `cl-nagoya/ruri-pt-base` → `tohoku-nlp/bert-base-japanese-v3`)
- **モデルの特徴**: tohoku-nlp BERT base (日本語 WikiPedia + CC100 等で MLM 事前学習された 12 層 BERT) をベースに、RetroMAE による検索向け事前学習、cl-nagoya ruri の対比学習、さらに SPLADE 蒸留を重ねた多段継承モデル。
- **採用の背景**: SPLADE は MLM ヘッドを再利用して vocab 次元のロジットをスパース化するため、高品質な MLM 重みが不可欠。日本語 SPLADE の最大公約数として評価されている tohoku-nlp BERT を基盤にし、さらに RetroMAE / ruri で検索向けに表現を整えた段階的な継承チェーンを採っている。

### モデルアーキテクチャ
- **バックボーン**: BERT-base (Transformer encoder)
- **Transformer ブロック数**: 12 層 (BERT-base 標準)
- **位置埋め込み方式**: 学習済み絶対位置埋め込み (BERT 系)
- **出力ヘッド**: BERT の MLM ヘッド (vocab_size 次元のロジット) + SPLADE の max-log(1+ReLU(·)) 圧縮
- **LoRA アダプタの有無**: 無し。フルパラメータでのファインチューン。
- **背景**: SPLADE v2 (Formal et al., 2021) の最大の設計判断は「MLM ヘッドを dense エンベッディング用ではなくスパース重要度推定器として再利用する」点で、この重要な仕掛けのために dense モデルではなく encoder-only BERT が必要。

### モデルのパラメータ数
- **値**: 約 0.1B (110M 規模、BERT-base 相当)
- **背景**: パラメータ数ではなく語彙次元のスパース表現で勝負するのが SPLADE の設計思想。したがってベースモデルは敢えて軽量な BERT-base に留め、強化はデータと蒸留で行う方針。

### 最大コンテキスト長
- **値**: 512 トークン
- **背景**: tohoku-nlp BERT の学習済み位置埋め込みの上限に一致。モデルカードでも「512 トークン以下の JMTEB 検索タスクで最高スコア」と明示されており、RAG における標準的なチャンクサイズをターゲットにした設計。長文対応は別系列のモデルで扱う前提。

### 出力ベクトルの次元数
- **値**: BERT-base 日本語版の語彙サイズ (約 32,768 次元) のスパースベクトル。実際の平均的な非ゼロ要素数は:
  - クエリ: 約 29.8 トークン (v1 は 23.3)
  - ドキュメント: 約 150〜379.6 トークン (v1 は 146.2)
- **背景**: dense の 768/1024 次元とは設計思想が根本的に異なる。dense との違いは「値が非ゼロな語彙 ID = 意味的に関連する語」と解釈でき、BM25 同様に転置インデックスで高速検索できる点が強み。v1 は過剰にスパースだったため語彙被覆が不足し、v2 では非ゼロ数を意図的に増やして再現率を改善。

### 学習したタスク
- 検索 (retrieval / first-stage ranker) が主目的
- JMTEB の Retrieval タスクへの汎化を志向 (mr-tydi / jaqket 等の *訓練データ* は意図的に除外)
- サブ用途として語彙レベルの重要度可視化・リランキングも可能

### Instruction Tuning への対応
- **値**: 無し
- **背景**: SPLADE は語彙空間で重要度を推定する構造上、instruction プレフィックスによるタスク切替は不要。Query / Document は 1 つのエンコーダ (同じ重み) で処理される。

### マトリョーシカ表現学習 (MRL) の対応
- **値**: 無し (SPLADE はスパースベクトルなので MRL の概念が直接は当てはまらない)
- **背景**: MRL は dense 埋め込みの次元削減手法。SPLADE ではスパース性の強さ (L1 / FLOPS の正則化強度) が同じ役割を果たし、強度を上げれば平均非ゼロ数が減って「小さい次元」相当になる。v1 は強スパース、v2 は中庸な設定。

### 多言語対応かどうか
- **値**: 日本語特化 (英語データも訓練に混ぜているが主ターゲットは日本語)
- **背景**: 語彙ヘッドは tohoku-nlp BERT の日本語語彙 (約 32K) に固定されているため、他言語では実用的な品質は期待できない。訓練には mmarco / msmarco-ja / hard-negatives 等の日本語・英語双方のデータが使われているが、英語混入は負例の質と分布の多様化が目的。

## モデルの訓練方法

### 損失関数
- **値**: クロスエントロピー損失 (リランカー教師スコアに対する蒸留)
- **背景**: テクニカルレポートによれば、KL ダイバージェンスや MarginMSE も試したが日本語データではクロスエントロピーが最も良かったとのこと。損失の形は「教師リランカーが付与した正例/負例スコア分布を生徒 SPLADE の内積スコアで再現する」形式。

### 正則化
- **値**: スパース性制御に L1 正則化を採用 (FLOPS 正則化ではない)
- **背景**: SPLADE v2 原著は FLOPS 正則化 (λ_q, λ_d を別々に設定) が標準だが、テクニカルレポートでは「日本語では L1 の方がスパース化の効果が高かった」と明記。さらにウォームアップ期間で正則化係数を徐々に強める schedule を採用しており、学習初期に埋め込み品質を確保してから徐々に絞り込む構造。

### プーリング戦略
- **値**: SPLADE max pooling: `max_t log(1 + ReLU(w_t)) · attention_mask`
- **背景**: SPLADE v1 は sum pooling を採用していたが、v2 で max に変更され精度が改善。max は「その語彙 ID に対して最も強く反応したトークン位置の値を採る」ため文書長の影響を受けにくい。

### 訓練パイプライン
- **値**: 多段のモデル継承 + リランカー蒸留
  1. tohoku-nlp/bert-base-japanese-v3 (MLM 事前学習)
  2. cl-nagoya/ruri-pt-base (検索向け対比事前学習)
  3. hotchpotch/ruri-pt-base-retromae (RetroMAE で検索向け再構成事前学習)
  4. hotchpotch/japanese-splade-base-v1_5 (SPLADE 蒸留)
  5. **japanese-splade-v2** (ハードネガティブ強化 + スパース性リバランス)
- **背景**: 単一段の対比学習では日本語データが不足しがち。段階的に目的が異なる事前学習を積み上げることで、小さな BERT-base でも高スコアを実現している。

### 訓練に適用した方式
- **学習率**: 5.0e-2 (SPLADE は MLM ヘッド由来の大きな出力を使うため、dense モデルより一桁以上高い LR が標準)
- **スケジューラ**: コサイン + 10% ウォームアップ
- **バッチ構成**: 1 正例 + 7 負例
- **バッチサイズ**: v1 では 32、mmarco-only 派生では 128 (家庭用 GPU で回したと明言あり)
- **フレームワーク**: 自作トレーナ YAST (HuggingFace Trainer API 互換)、Transformers ベース

### 訓練データの構成と品質
- `hpprc/emb`: auto-wiki-qa, jsquad, jaquad, auto-wiki-qa-nemotron, quiz-works, quiz-no-mori, baobab-wiki-retrieval, mkqa
- `hotchpotch/japanese-splade-v1-hard-negatives`: mmarco, mqa, msmarco-ja ベースのハードネガティブ
- `hotchpotch/mmarco-hard-negatives-reranker-score`: 英語ハードネガティブ (リランカースコア付き)
- **注目点**: JMTEB 評価に用いる `mr-tydi` や `jaqket` の訓練分割は意図的に除外。ベンチマーク汚染を避け汎化性能を測れるようにしている。

### ハードネガティブマイニングの手法
- **値**: 二段階の蒸留型マイニング
  1. 既存の埋め込み / BM25 系で候補負例を抽出
  2. 高性能リランカー (BAAI/bge-reranker-v2-m3, cl-nagoya/ruri-reranker-large) で各ペアをスコアリングし、スコア分布を教師ラベルとして保存
- **背景**: SPLADE v2 原著では cross-encoder からの蒸留が高品質化の鍵とされているが、日本語特化の強力なリランカー (ruri-reranker-large) と多言語 SOTA (bge-reranker-v2-m3) の 2 つを併用することで、単一教師の偏りを平滑化している。

## モデルの評価

### ベンチマークスコア (JMTEB Retrieval)
モデルカードより抜粋:

| タスク | japanese-splade-v2 |
|--|--|
| jagovfaqs | 0.7313 |
| jaqket | 0.6986 |
| mrtydi | **0.5106** |
| nlp_journal (title_abs) | **0.9831** |
| nlp_journal (abs_intro) | 0.9067 |
| nlp_journal (title_intro) | 0.8026 |
| **Avg (≤512 tokens)** | **0.7309** |
| Avg (ALL) | 0.7722 |

- **相対的な強み**: 512 トークン以下のコーパスでは OpenAI `text-embedding-3-large` などを含む同時代モデル群の中で首位クラス (リリース時点)。
- **弱み**: 512 超の長文は扱えない。全体平均 (ALL) は上位ではあるが、長文主体のコーパスでは dense long-context モデル (bge-m3 等) に劣りうる。
- **特筆点**: mr-tydi の訓練セットを使わずに 0.5106 を出している点。汎化性能が高いことを示唆。

## 論文 / リリースの目新しいポイント

### 今回の発表の目新しいポイント
1. **日本語特化の SPLADE を公開水準で実現**: 英語以外の SPLADE は希少だったなかで、日本語 JMTEB で 0.7309 (≤512) を達成。
2. **v1 → v2 でスパース性をリバランス**: v1 は強スパース (平均 23〜146 トークン) で再現率が頭打ちだった。v2 は中庸 (29〜380 トークン) にして語彙被覆を増やし検索精度を底上げ。
3. **リランカー二種蒸留**: BAAI/bge-reranker-v2-m3 と cl-nagoya/ruri-reranker-large の二段蒸留スコアを訓練データに埋め込み。
4. **L1 正則化の採用**: SPLADE v2 原著の FLOPS ではなく L1 の方が日本語で有効という経験的知見を明文化。
5. **YAST トレーナの公開**: HuggingFace Trainer 互換の SPLADE 訓練フレームワークを OSS 化。再現性の敷居を下げている。

### 先行研究 (Related Work) の要約
- **SPLADE v1 (Formal et al., SIGIR 2021)**: BERT の MLM ヘッドで語彙重要度を出し、FLOPS 正則化でスパース化した最初期モデル。Sum pooling のため文書長に敏感だった。
- **SPLADE v2 (Formal et al., arXiv 2021-09)**: pooling を max log(1+ReLU) に変更、知識蒸留 (cross-encoder 教師) とハードネガティブを導入して BEIR 強化。本モデルが踏襲する直接の祖先。
- **tohoku-nlp BERT**: 日本語コミュニティの標準的 encoder。MLM 品質が高く SPLADE のヘッド再利用と相性が良い。
- **cl-nagoya/ruri**: 日本語汎用検索埋め込みモデル。`ruri-pt-base` を中間ステップに挟むことで対比学習済みの重みから出発できる。
- **RetroMAE (Xiao et al., 2022)**: 検索向けの非対称 auto-encoder 事前学習。本モデルでは `ruri-pt-base-retromae` として中間段に採用。
- **差別化**: dense モデルに対して (a) BM25 スタイルの転置インデックスで高速検索可能、(b) トークンレベルの解釈性があり、(c) RAG でのリランキングを部分的に代替できる。日本語でこれを OSS で提供した点が最大の貢献。

## まとめ表

| 項目 | 値 |
|--|--|
| 開発組織 | 個人開発者 hotchpotch (Yuichi Tateno / secon) |
| 公開年月 | 2024-12 (HuggingFace Hub) |
| 使用したベースモデル | hotchpotch/japanese-splade-base-v1_5 (遡ると tohoku-nlp/bert-base-japanese-v3) |
| 位置埋め込み方式 | 学習済み絶対位置埋め込み (BERT) |
| Transformer ブロック数 | 12 (BERT-base) |
| LoRA アダプタの有無 | 無し (フルファインチューン) |
| モデルのパラメータ数 | 約 0.1B (110M) |
| 最大コンテキスト長 | 512 トークン |
| 出力ベクトルの次元数 | 語彙サイズ約 32K のスパース (非ゼロ: Q ~30, D ~150-380) |
| 学習したタスク | 検索 (first-stage retrieval) |
| Instruction Tuning 対応 | 無し |
| MRL 対応 | 無し (L1 正則化強度でスパース度を制御) |
| 多言語対応 | 日本語特化 (英語データも混入) |
| 損失関数 | クロスエントロピー (リランカー蒸留) |
| 正則化 | L1 正則化 + ウォームアップ (FLOPS ではない) |
| プーリング戦略 | max log(1 + ReLU(w)) · attention_mask |
| 訓練パイプライン | BERT → ruri-pt-base → RetroMAE → splade-base-v1_5 → **v2** |
| ハイパーパラメータ | LR 5e-2, cosine + 10% warmup, 1pos+7neg, batch 32〜128 |
| ハードネガティブマイニング | BAAI/bge-reranker-v2-m3 + cl-nagoya/ruri-reranker-large の二段蒸留スコア |
| 主要ベンチマーク | JMTEB Avg (≤512): 0.7309 / Avg (ALL): 0.7722、≤512 トークンでクラス首位 |
| 訓練フレームワーク | YAST (HuggingFace Trainer 互換、著者 OSS) |
| ライセンス | MIT |

## 参考リンク

- モデルカード: https://huggingface.co/hotchpotch/japanese-splade-v2
- リリース記事 (2024-12-19): https://secon.dev/entry/2024/12/19/100000-japanese-splade-v2-release/
- テクニカルレポート (2024-10-23): https://secon.dev/entry/2024/10/23/080000-japanese-splade-tech-report/
- YAST (訓練コード): https://github.com/hotchpotch/yast
- YASEM (推論ライブラリ): https://github.com/hotchpotch/yasem
- SPLADE v2 原著論文: https://arxiv.org/abs/2109.10086
- 前身モデル v1: https://huggingface.co/hotchpotch/japanese-splade-base-v1
