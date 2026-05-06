# CSPLADE: Learned Sparse Retrieval with Causal Language Models

Zhichao Xu, Aosong Feng, Yijun Tian, Haibo Ding, Lin Lee Cheong
Amazon Web Services
xzhichao@amazon.com

## 概要

- 近年、情報検索 (IR) 研究では dense retrieval が主流となっている。
- dense retrieval は有効である一方で、解釈不可能な dense ベクトルを生成し、インデックスサイズが大きいという欠点を抱えている。
- learned sparse retrieval (LSR) は有望な代替手法として登場しており、競争力のある検索性能を達成しつつ、効率的な検索のために古典的な転置インデックスのデータ構造を活用できる。
- しかしながら、LSR を BERT 規模を超えてスケールさせる研究は限定的である。
- 本研究では、large language models (LLM) を LSR 用に学習する際の 2 つの課題を特定する。
- (1) contrastive training の初期段階における学習の不安定性、(2) 事前学習済み LLM の単方向アテンションに起因する性能の最適化不足、である。
- これらの課題に対処するため、対応する 2 つの技術を提案する。
- (1) 学習の不安定性を解消するための軽量な適応学習フェーズ、(2) 双方向情報を可能にする 2 つのモデルバリアント、である。
- これらの技術により、8B 規模の LLM を用いた LSR モデルを学習することが可能となり、削減されたインデックスサイズで競争力のある検索性能を達成する。
- さらに、本研究はモデル量子化の観点から LLM ベース LSR モデルの性能と効率のトレードオフを分析した最初の研究の 1 つである。
- 本研究の知見は、効率的な検索モデリングのために LLM を適応させる方法に関する示唆を提供する。

## 1 はじめに

- 近年、情報検索 (IR) における主な研究の焦点は、dense retrieval とその関連技術にある (Karpukhin et al., 2020; Lin et al., 2022; Zhu et al., 2023a; Xu et al., 2025b, inter alia)。
- dense retrieval はクエリと文書を高次元のスパースベクトルにエンコードする。
- 効果的ではあるものの、これらの dense ベクトルは意味的内容を人間が解釈することが難しい。
- さらに、文書集合全体について dense ベクトルをエンコードして保存するには、多くのリソースを必要とする。
- 例えば、Llama-2-7b の dense retriever でエンコードした MS MARCO passage コーパス (Bajaj et al., 2016) のフラットインデックスは 135G のディスク容量を占めるのに対し (Ma et al., 2024)、Lucene の BM25 実装による Lucene インデックスは 2.6G に過ぎず、その差は 50 倍以上にもなる。

- dense retrieval のこれらの欠点を緩和するため、別の研究の流れとして learned sparse retrieval (LSR) が研究されている。
- 従来の sparse retrieval モデル (Sparck Jones, 1972; Robertson et al., 1995) に着想を得た LSR は、バックボーン言語モデルと言語モデルヘッドを用いてクエリと文書を語彙サイズのベクトルにエンコードする。
- ベクトルの各次元は、対応するトークンの「impact」を表す (Formal et al., 2021b,a; Mallia et al., 2021)。
- LSR の代表的な例が SPLADE である (Formal et al., 2021b,a)。
- SPLADE は BERT (Devlin et al., 2019) でテキストをエンコードし、続いて pooling と log-saturation (Fang et al., 2004) を適用することで、結果として得られる語彙サイズのベクトルが各次元で非負値を持つようにし、inverted index での利用に適した形にする。
- dense retrieval で確立されている学習手法、すなわち contrastive learning (Oord et al., 2018)、hard negatives mining (Karpukhin et al., 2020; Xiong et al., 2021)、knowledge distillation (Hofstätter et al., 2020) と組み合わせることで、LSR は BERT スタイルの encoder-only マスク言語モデルと競合する性能を示している (Kong et al., 2023; Lassance et al., 2024)。

- スケーリングは自然言語処理 (NLP) と IR において勝利の方程式となってきた (Kaplan et al., 2020; Hoffmann et al., 2022; Fang et al., 2024)。
- 最近の研究 (Ma et al., 2024; Lee et al., 2024; Wang et al., 2024a; Xu et al., 2025a; Zhang et al., 2025, inter alia) では、Llama (Touvron et al., 2023) や Mistral (Jiang et al., 2023) のような事前学習済み decoder-only large language model (LLM) を用いて dense retrieval や reranking をスケーリングする試みが行われており、BERT 系モデルと比較して優れた性能を示している。
- しかし、BERT 規模 (110M および 330M) を超えた LSR モデルの学習に関しては、これまで取り組みが限られてきた。
- 我々の予備実験では、decoder-only LLM を用いて LSR を学習する際の 2 つの主要な課題を特定した。
- (1) SPLADE の log-saturation で用いられる $\mathrm{ReLU}$ 活性化関数が、contrastive 学習の初期段階において学習の不安定性問題を引き起こす。
- これは一般に dying ReLU 問題 (Lu et al., 2019) として知られている。
- (2) decoder-only LLM の単方向 attention は、検索性能を準最適にする (Lee et al., 2024; BehnamGhader et al., 2024)。
- これら 2 つの課題に対処するため、本論文では 2 つの手法を提案する。

- 我々は軽量な adaptation phase 学習を提案する。
- これは、causal language modeling 損失と log-saturation 損失の組み合わせを用いて、ラベルなしテキスト上で事前学習済み言語モデルを適応させるものである。
- 実験の結果、わずか 10k の adaptation ステップで、その後の contrastive 学習における学習不安定性問題を解消できることが示された。

- 単方向 LM が双方向情報を捉えられるようにするため、2 つのバリアントを検討した。
- (1) echo embedding のアイデア (Springer et al., 2024) を適用し、入力系列を繰り返し、テキスト系列の 2 回目の出現からのみ表現を集約する手法。
- (2) causal language modeling (CLM) マスクを直接無効化し、Lee et al. (2024) と同様に contrastive 学習段階で言語モデルが双方向情報に適応するようにする手法。
- 実験により、これら 2 つのバリアントはいずれも単方向情報のみを使用する causal 言語モデルに対して大幅に性能を改善することを示した。

- 我々はこの手法を Causal SPLADE (CSPLADE) と呼ぶ。
- 提案手法を用いることで、最大 8B 規模の事前学習済み LM (Llama-3.1-8B) を用いて LSR モデルを学習することが可能となり、MS MARCO passage retrieval の学習セットのみを使用しても競合する性能 (MS MARCO passage retrieval で MRR 41.3、BEIR で NDCG@10 が 55.3) を達成し、インデックスサイズも削減できる (135G の dense フラットインデックスに対して、MS MARCO passage コーパスの Lucene インデックスは 8G 未満)。

- LLM を retrieval に採用する上での重要な課題は、スケーラビリティと推論レイテンシにある。
- 我々は LLM.int8 (Dettmers et al., 2022)、torchao (torchao team, 2024) などのいくつかの一般的な量子化手法を検討し、CSPLADE に適用した際の性能と効率のトレードオフを報告する。
- calibration-free な量子化手法は GPU メモリ使用量を削減するものの、小さなバッチサイズでは必ずしも推論の高速化につながらないことを発見した。
- 本研究の知見は、neural retrieval モデルに特化して設計・最適化された量子化手法を詳細に研究することの重要性を強調するものである。

## 2 背景と表記

- 本節では、本論文で用いるタスク定義と表記を導入し、さらに learned sparse retrieval の背景について、特に SPLADE (Formal et al., 2021b,a) に焦点を当てて説明する。

### 2.1 タスク定義と表記

- クエリ $Q$ が与えられたとき、タスクは $Q$ に対して高い関連性を示す $k$ 個の文書のランク付きリスト $\{D_1, D_2, \ldots, D_k\}$ を見つけることである。
- 検索は、 $|C| > k$ であるような文書コレクション $C$ から top-k の文書を見つけることによって行われる。
- $\theta$ でパラメータ化された検索モデルを $f_\theta(\cdot)$ と表記する。
- 効率的な検索を可能にするため、文書コレクションは典型的にはオフラインで検索モデルによって事前にエンコードされ、いわゆる文書インデックスが構築される。
- 検索時には、入力されたクエリがまず検索モデルによってエンコードされ、その後、事前構築された文書インデックスに対して類似度検索が実行される。

### 2.2 スパース検索

- 文書を密ベクトルで表現する一般的な dense retrieval 手法 (Karpukhin et al., 2020; Xiong et al., 2021, inter alia) と異なり、sparse retrieval 手法では文書を vocabulary サイズのベクトルで表現し、その要素のほとんどはゼロである。
- これが「sparse(疎)」と呼ばれる所以である。
- この sparse なベクトル表現はその後、効率的な検索のために inverted index で利用できる。
- sparse retrieval の例としては、boolean model (Salton, 1984) のような古典的手法や、BM25 (Robertson et al., 1995) のような確率的検索モデルが挙げられる。

- 伝統的な sparse retrieval 手法は語彙的マッチング信号の捕捉に焦点を当てており、これが意味的に関連する文書を見つける際の性能を妨げている (Yates et al., 2024)。
- Learned sparse retrieval は、事前学習済み言語モデルを活用することでこの弱点を緩和する手法として登場した。
- より高いレベルでは、LSR はデータからトークン重要度、すなわち「impact」スコアを学習する手法と見なすことができる (Dai and Callan, 2019; Bai et al., 2020; Mallia et al., 2021)。

### 2.3 SPLADE

- 提案手法 (第 3 節) の基礎となる SPLADE (Formal et al., 2021b,a) の定式化を詳述する。
- vocabulary を $V$ 、文書を $D$ 、トークンを $\{t_1, t_2, \ldots, t_{|D|}\}$ ( $t_i$ は $i$ 番目のトークン)、その対応する文脈化表現(例: 事前学習済み BERT からのもの)を $\{h_1, h_2, \ldots, h_{|D|}\}$ と表記する。
- 各 $h_i$ について、language modeling head(例: BERT の masked language modeling head)を用いて、隠れ表現を vocabulary サイズのベクトル $H_i \in \mathbb{R}^{|V|}$ に射影する。
- $H_i$ の $j$ 番目の次元は、入力系列における $i$ 番目のトークンに対する vocabulary $V$ 中のトークン $j$ の重要度を表しており、実際には LM head 出力からの logit である。
- テンソル形状 $(|V|, |D|)$ の $H_D = \{H_1, H_2, \ldots, H_{|D|}\}$ が与えられると、SPLADE は系列長次元(つまり全トークンにわたって)max-pooling を適用し、続いて ReLU 活性化と log re-scaling を適用して、入力文書 $d$ に対する vocabulary サイズの表現を得る:

$$
D = \log(1 + \mathrm{ReLU}(\mathrm{MaxPooling}(H_D))) \in \mathbb{R}^{|V|} \tag{1}
$$

- 同様の操作はクエリ $Q$ にも適用でき、クエリ表現 $Q \in \mathbb{R}^{|V|}$ を得る。
- 類似度関数を $s(\cdot)$ (例: 内積)と表記すると、対比学習のための標準的な InfoNCE 損失 (Oord et al., 2018) で SPLADE を最適化できる。
- 学習ペア $(Q, D^+)$ ( $D^+$ はクエリ $Q$ に関連する文書)、および $Q$ に関連しない文書のリスト $\{D_N\}$ を表記すると、ランキング損失は以下のように表される:

$$
\mathcal{L}_{\text{rank}}(Q, D^+, \{D_N\}) = -\log p(D = D^+ \mid Q) = -\log \frac{e^{s(Q, D^+)}}{e^{s(Q, D^+)} + \sum_{D_i \in \{D_N\}} e^{s(Q, D_i)}}
$$

- 実際には、 $\{D_N\}$ は hard negatives と in-batch negatives を含むことが多い (Qu et al., 2021; Ma et al., 2024)。
- 式 (1) は非負性を保証することで既にある程度のスパース性を達成していることに注意されたい。
- さらに SPLADE は、効率的な sparse 表現を学習するためにスパース性をさらに強化すべく、FLOPs regularization (Paria et al., 2020) も採用している。
- $Q$ と $D$ に対する FLOPs regularization 損失をそれぞれ $\mathcal{L}_{\text{reg}}^Q$ と $\mathcal{L}_{\text{reg}}^D$ 、対応する係数を $\lambda_Q$ 、 $\lambda_D$ と表記すると、SPLADE は最終的な損失を以下のように最適化する:

$$
\mathcal{L} = \mathcal{L}_{\text{rank}}(Q, D^+, \{D_N\}) + \lambda_Q \mathcal{L}_{\text{reg}}^Q + \lambda_D \mathcal{L}_{\text{reg}}^D
$$

- 実際には、 $\lambda_Q$ と $\lambda_D$ は性能と効率のバランスを取るためにハイパーパラメータとして調整される。

## 3 課題と提案手法

- SPLADE の BERT 規模における有効性は、これまでに数多くの先行研究によって示されてきた (Formal et al., 2021a, 2022; Kong et al., 2023; Li et al., 2023, inter alia)。
- しかしながら、SPLADE を BERT 規模を超えて学習する試み、すなわち Llama (Touvron et al., 2023) や Mistral (Jiang et al., 2023) のような事前学習済み causal large language model に拡張し、より強力なバックボーン LM と大規模事前学習によって性能をさらに向上させる試みについては、限定的な研究しか行われていない。
- 本研究の予備実験では、オリジナルの SPLADE 実装における BERT (Devlin et al., 2019) を OPT-1.3B (Zhang et al., 2022) や Llama-3.2-1B (Grattafiori et al., 2024) のような causal LLM に置き換えたところ、いくつかの重要な課題を特定した (Section 3.1)。
- 次に、これらの課題に対応するため、causal language model を用いた SPLADE の学習を可能にする戦略を提案する (Section 3.2)。
- 我々はこの手法を Causal SPLADE (CSPLADE) と名付ける。

### 3.1 課題

- 第一に、contrastive learning の初期段階における学習の不安定性の問題が観察された。
- 式 (1) に示されるように、語彙サイズの表現 $Q$ および $D$ の非負性を保証するために ReLU 活性化関数が用いられている。
- 学習が始まると、ReLU ニューロンは急速に不活性化し、任意の入力に対して 0 のみを出力するようになる。
- これは文献において dying ReLU 問題として知られており (Lu et al., 2019)、最適化対象パラメータ、本研究の場合はバックボーン言語モデルの初期化に起因する。
- この仮説を検証するため、MosaicBERT (Portes et al., 2023) や ModernBERT (Warner et al., 2024) を含む他の encoder-only モデルでの学習も試みた。
- しかし、learning rate の warmup 戦略やその他のハイパーパラメータを広範に調整したにもかかわらず、同じ理由で学習は一貫して失敗した。

- 第二に、オリジナルの SPLADE 実装では、モデルがまず各 token の文脈化された表現を語彙空間に射影して $|D|$ 個のベクトルを取得し、その後、系列長次元に対して MaxPooling を適用して単一のベクトル表現を得ていることが観察される。
- 明らかに、この系列レベルの MaxPooling 操作は、unidirectional attention を持つ causal LLM にとっては最適ではない。
- なぜなら、入力系列内の早い token は後の token に attend できず、最終的なベクトル表現において情報の損失が生じるためである。
- 要約すると、これら 2 つの課題が、SPLADE を大規模事前学習済み causal LLM に拡張する試みを阻害していると我々は考える。

1 後続研究 (Formal et al., 2021a; Kong et al., 2023) では、distillation (Hofstätter et al., 2020) のような他の学習戦略も検討されている。本研究では、より複雑な学習戦略は本論文の焦点とは直交するため、シンプルな contrastive learning を採用した。

### 3.2 提案手法

- Section 3.1 において、(1) 学習の不安定性の問題、および (2) unidirectional な情報の問題、という 2 つの課題を特定した。
- これらの課題に対処するため、最終的な検索モデルを得るための 2 段階の学習パイプラインを導入する: (1) 学習の安定性を改善するための adaptation phase 学習、および (2) より豊かな文脈を捉えるための contrastive learning における bidirectional な情報の活用、である。

- **Adaptation Phase Training.**
- Lu et al. (2019) が指摘しているように、dying ReLU の原因は不適切に初期化されたモデルパラメータにある。
- したがって、後続の contrastive learning フェーズで使用するための初期化を改善するため、事前学習済み causal language model を adaptation することで学習の不安定性の問題に取り組む。
- 具体的には、入力系列 $D$ に対して、出力 logits $H_D \in \mathbb{R}^{|V| \times |D|}$ を計算できる。
- 次に、式 (1) と類似した変換を適用するが、MaxPooling 操作は除去する:

$$
\bar{H}_D = \log(1 + \mathrm{ReLU}(H_D)) \tag{2}
$$

- ここで $\bar{H}_D$ テンソルは $H_D$ と同じ形状を持つが、すべての要素は非負である。
- この非負テンソルを用いて、目標系列 (本研究の場合は同じ入力系列) の確率を最大化するための causal language model loss を計算する。
- ReLU adaptation を意図したこの causal language modeling loss を $\mathcal{L}_{\mathrm{ReLU}}$ 、通常の causal language model loss を $\mathcal{L}_{\mathrm{CLM}}$ と表記し、最終的な loss を最適化する:

$$
\mathcal{L}_{\mathrm{Adapt}} = \mathcal{L}_{\mathrm{CLM}} + \lambda_{\mathrm{ReLU}} \cdot \mathcal{L}_{\mathrm{ReLU}} \tag{3}
$$

- ここで $\lambda_{\mathrm{ReLU}}$ は 2 つの loss 項のバランスを取るトレードオフ重みであり、実際には 1 に設定される。
- ここで、通常の causal language modeling loss は $H_D$ と目標系列との間で直接計算されることに注意する。
- したがって、2 つの loss 項を 1 回の forward pass で計算できる。
- この loss の形式により、後続の contrastive learning で使用される ReLU 活性化に対して事前学習済み causal LLM を adaptation することが可能となる。
- 理解の容易さのため、擬似コード (PyTorch スタイル) を Section A に示す。

- この adaptation 学習戦略には 2 つの強みがある: (1) 任意のラベルなしテキストに対して実行可能であること、(2) ドメイン適応学習 (Gururangan et al., 2020) と効率的に組み合わせることで、対象ドメインにおける下流タスクの性能をさらに改善できることである。
- 経験的に、わずか 10k ステップの adaptation で学習の不安定性の問題が解消されることを確認しており、その有効性が示唆される。

- **Enabling Bidirectional Information.**
- 学習の不安定性の問題に対処したので、次に表現学習の改善に進む。
- 前述したように (Section 3.1)、事前学習済み causal language model の unidirectional な性質は、系列表現を効果的に学習する能力を阻害する。
- dense retrieval においてこの問題に取り組む様々な研究が存在する (Springer et al., 2024; Lee et al., 2024; BehnamGhader et al., 2024, inter alia)。
- これらの先行研究に動機づけられ、事前学習済み causal LLM に対して bidirectional な情報を活用する 2 つの variant を検討する: (1) echo embedding (Springer et al., 2024)、および (2) bidirectional attention の直接的な活用 (Lee et al., 2024) である。

- Echo embedding は事前学習済み LLM のモデルアーキテクチャを変更せず、代わりに入力を変更する。
- 入力系列を 2 回繰り返し、入力系列の 2 回目の出現に対してのみ pooling を実行する。
- これにより、2 回目の出現における入力系列の早い token は、1 回目の系列における後の token に依然として attend することができ、bidirectional な情報を活用できる。
- 一方で、これは本質的に入力長を倍増させ、学習における計算コストの増加と推論におけるレイテンシの増加を引き起こす。

- また、Lee et al. (2024) のアイデアも実験する。
- これは、causal mask を除去することで事前学習済み causal LLM の bidirectional attention を直接有効化し、その後 contrastive learning でモデルを使用するというものである。
- この手法は、bidirectional な情報のための adaptation フェーズを contrastive learning フェーズに統合し、echo embedding variant と比較して追加の計算オーバーヘッドを発生させない。
- 実験結果は、両方の variant が causal LLM ベースラインを大幅に上回り、bidirectional attention を用いた variant がわずかに優れた性能をもたらすことを示している。

- 我々は Llama-3 (Grattafiori et al., 2024) をバックボーンの causal language model として、SPLADE モデルの 3 つの variant を学習する。
- ただし、議論される技術は他の事前学習済み causal LLM にも適用可能である。
- unidirectional な情報を持つ SPLADE を CSPLADE (adaptation 学習のみを用いるもの) と呼び、2 つの bidirectional な variant をそれぞれ CSPLADE-Echo および CSPLADE-Bi と呼ぶ。

## 4 実験設定

- 本節では、データセット、ベースライン、実装、その他の実験詳細について説明する。

### 4.1 データセット

- 我々はパッセージ検索のタスクに焦点を当てる。
- 検索モデルは、約500kの訓練クエリからなる MS MARCO passage retrieval データセット (Bajaj et al., 2016) の訓練分割で学習する。
- 公開されている2 BM25 (Robertson et al., 1995) と CoCondenser (Gao and Callan, 2022) のハードネガティブをブレンドして使用する。

- 評価については、6,980クエリからなる公式の MS MARCO passage retrieval DEV セットでドメイン内の検索性能を評価する。
- さらに、それぞれ43および54クエリで構成され詳細にアノテートされた TREC DL19 および DL20 でも評価する。
- 公式評価指標として、DEV では MRR@10 および Recall@1000、DL19 および DL20 では NDCG@10 を採用する。
- また、ドメイン外評価として BEIR データセット (Thakur et al., 2021) も含める。
- BEIR コレクション内の13個の公開テストセットに対して、公式評価指標である NDCG@10 で評価する。
- データセットの詳細については Section B に譲る。

### 4.2 比較手法

- dense retrieval と sparse retrieval の両方のベースライン手法を含める。
- dense retrieval については、CoCondenser (Gao and Callan, 2022)、bi-SimLM (Wang et al., 2023)、SGPT (Muennighoff, 2022)、および RepLlama (Ma et al., 2024) を含める。
- RepLlama は、同じ対比学習目的関数と訓練セットを使用しているため、我々の手法に最も近い dense retrieval ベースラインである。
- 元の論文の Llama-2-7b (Touvron et al., 2023) の結果に加え、Zhuang et al. (2024)3 による Llama-3.1-8b (Grattafiori et al., 2024) の結果も含める。

- sparse retrieval については、古典的な BM25 手法 (Robertson et al., 1995) を含める。
- また、Formal et al. (2021a); Lassance et al. (2024) で報告されている、複雑なハードネガティブマイニングと自己蒸留訓練戦略を用いた SPLADE++ SelfDistil および最新の SPLADE-v3 バリアントも含める。
- 最後に、もう一つの競争力のある SPLADE バリアントとして SparseEmbed (Kong et al., 2023) を含める。
- すべてのベースラインについて、対応する論文で報告されている結果を使用する。

### 4.3 実装とハイパーパラメータ

- Section 3.2 で述べたように、提案手法の有効性を、事前学習された Llama-3 ファミリーモデルを retriever のバックボーンとして用いて検証する。
- モデルサイズは1Bと8Bの2種類、すなわち Llama-3.2-1B および Llama-3.1-8B4 を使用する。

- 我々の実装は、PyTorch、Huggingface (Wolf et al., 2019)、Tevatron (Gao et al., 2022)、および Pyserini (Lin et al., 2021) の Lucene 統合に基づいている。
- モデルが訓練された後、Lucene を使用して転置インデックスを構築し、後続の検索を行う。
- 適応訓練については、事前学習済み CLM を MS MARCO passage コーパスに対して、シーケンス長2,048、グローバルバッチサイズ32で10Kステップ適応させる。
- 学習率スケジューリングには、1kステップのウォームアップを伴うコサインスケジューリングを採用する。
- 計算効率のため、sequence packing (Raffel et al., 2020) 技術を使用する。
- 対比学習については、ドメイン内とドメイン外の性能のバランスを取るため (Biderman et al., 2024)、LoRA fine-tuning (Hu et al., 2021) を使用する。
- RepLlama と類似した訓練設定、すなわち1つの正例の query-passage ペアあたり15個のハードネガティブを in-batch ネガティブと組み合わせて使用する。
- 1Bモデルと8Bモデルの両方で511個の in-batch ネガティブを使用し、グローバルバッチサイズは32となる。
- スケーラブルな訓練のため、Flash Attention 2 (Dao, 2023)、gradient checkpointing、gradient accumulation、および PyTorch FSDP (Zhao et al., 2023) などの技術を使用する。
- コサイン学習率スケジューリングを用いて、1Bモデルは3エポック、8Bモデルは1エポック訓練する。
- 主に4つのハイパーパラメータ、すなわち学習率、FLOPs正則化係数 $\lambda_Q$ および $\lambda_D$ 、LoRA ランク $R$ をチューニングする。
- さらなるハイパーパラメータの詳細とハードウェア情報は Section C に譲る。
- 推論時には、LoRA アダプタをバックボーンモデルにマージし、推論には bfloat 16 精度を使用する。

## 5 結果と分析

- ドメイン内評価結果(セクション5.1)とドメイン外評価結果(セクション5.2)について議論する。
- 量子化評価のセットアップと結果(セクション5.3)を詳細に述べ、最後に成功しなかった試み(セクション5.4)について議論する。

2https://huggingface.co/datasets/Tevatron/
msmarco-passage-aug

3RepLlama-3-8B の BEIR における結果は Zhuang et al. (2024) によって報告されていないため、ここではスキップしている。

<table>
<caption>表1: MS MARCO ドメイン内評価における性能とインデックスサイズ。インデックスサイズの列を除き、各セクション内で最高性能をハイライトしている。</caption>
<tr>
<th>Model</th>
<th>Size</th>
<th>Dev MRR@10</th>
<th>Recall@1k</th>
<th>DL19 NDCG@10</th>
<th>DL20 NDCG@10</th>
<th>Index Size GB (1)</th>
</tr>
<tr>
<td>Dense Retrieval</td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>CoCondenser (Gao and Callan, 2022)</td>
<td>110M</td>
<td>38.2</td>
<td>98.4</td>
<td>71.7</td>
<td>68.4</td>
<td>25</td>
</tr>
<tr>
<td>bi-SimLM (Wang et al., 2023)</td>
<td>110M</td>
<td>39.1</td>
<td>98.6</td>
<td>69.8</td>
<td>69.2</td>
<td>25</td>
</tr>
<tr>
<td>GTR-XXL (Ni et al., 2022)</td>
<td>4.8B</td>
<td>38.8</td>
<td>99.0</td>
<td>-</td>
<td>-</td>
<td>25</td>
</tr>
<tr>
<td>RepLlama-2-7B (Ma et al., 2024)</td>
<td>7B</td>
<td>41.2</td>
<td>99.4</td>
<td>74.3</td>
<td>72.1</td>
<td>135</td>
</tr>
<tr>
<td>RepLlama-3-8B (Zhuang et al., 2024)</td>
<td>8B</td>
<td>42.8</td>
<td>-</td>
<td>74.5</td>
<td>73.9</td>
<td>135</td>
</tr>
<tr>
<td>Sparse Retrieval</td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>BM25 (k1= 0.9,b = 0.4)</td>
<td>-</td>
<td>18.4</td>
<td>85.4</td>
<td>50.6</td>
<td>48.0</td>
<td>2.6</td>
</tr>
<tr>
<td>SPLADE++ (Formal et al., 2021a)</td>
<td>110M</td>
<td>37.8</td>
<td>98.5</td>
<td>73.6</td>
<td>72.8</td>
<td>2.6</td>
</tr>
<tr>
<td>SparseEmbed (Kong et al., 2023)</td>
<td>110M</td>
<td>39.2</td>
<td>98.1</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>SPLADE-v3 (Lassance et al., 2024)</td>
<td>110M</td>
<td>40.2</td>
<td>-</td>
<td>72.3</td>
<td>75.4</td>
<td>3.1</td>
</tr>
<tr>
<td>Proposed Method</td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>CSPLADE-1B</td>
<td>1.3B</td>
<td>38.2</td>
<td>98.5</td>
<td>73.2</td>
<td>68.9</td>
<td>2.6</td>
</tr>
<tr>
<td>CSPLADE-Echo-1B</td>
<td>1.3B</td>
<td>38.8</td>
<td>98.9</td>
<td>72.9</td>
<td>69.5</td>
<td>4.6</td>
</tr>
<tr>
<td>CSPLADE-Bi-1B</td>
<td>1.3B</td>
<td>40.4</td>
<td>99.0</td>
<td>73.8</td>
<td>69.8</td>
<td>5.6</td>
</tr>
<tr>
<td>CSPLADE-8B</td>
<td>8B</td>
<td>39.5</td>
<td>99.0</td>
<td>73.0</td>
<td>68.0</td>
<td>7.5</td>
</tr>
<tr>
<td>CSPLADE-Echo-8B</td>
<td>8B</td>
<td>40.8</td>
<td>98.9</td>
<td>73.5</td>
<td>70.7</td>
<td>4.5</td>
</tr>
<tr>
<td>CSPLADE-Bi-8B</td>
<td>8B</td>
<td>41.3</td>
<td>99.1</td>
<td>74.1</td>
<td>72.8</td>
<td>6.7</td>
</tr>
</table>

### 5.1 ドメイン内検索

- ドメイン内の結果を表1に示す。
- dense retrieval ベースラインについては、RepLlama-3-8B が RepLlama-2-7B を上回る性能を示しており、バックボーン言語モデルの容量が検索性能にとって重要であることを示唆している。
- sparse retrieval ベースラインに関しては、SPLADE-v3 が最高性能を達成しており、DL20 ベンチマークでは RepLlama-3-8B を上回っている。
- この観察結果は、強力な cross-encoder 教師モデルからの知識蒸留が BERT サイズのモデルの性能向上に有効であることを示唆している。

- 提案手法については、CSPLADE-Echo および CSPLADE-Bi が CSPLADE バリアントを大幅に上回ることを確認した。
- 例えば、CSPLADE-Bi-1B は DEV において 40.4 MRR@10 を達成しており、CSPLADE-1b と比較して優れている。
- これは双方向情報を有効化することの重要性を示唆している。
- さらに、8B モデルは 1B モデルを上回ることが観察され、バックボーンモデルの容量の重要性が改めて確認された。
- CSPLADE-Echo と CSPLADE-Bi の比較では、CSPLADE-Bi がわずかに優れた性能を示している。
- ただし、強力な性能を達成するためにはより慎重なハイパーパラメータ調整が必要であることに留意する。
- 最後に、最高性能の CSPLADE-Bi-8B でも、対応する dense retrieval モデルには依然として及ばないことを指摘する。
- 我々は、この性能差は RepLlama-3-8B が単一の 4,096 次元の dense ベクトルを使用していることに起因すると仮定しており、これは CSPLADE の sparse 表現と比較してより大きな表現容量を提供する。
- 我々は効率的な検索のために転置インデックスのサイズを制御することを意図している。
- 検索の有効性とインデックスサイズの間のトレードオフについてのより包括的な調査は将来の課題とする。

### 5.2 ゼロショット検索

- ゼロショット検索の性能を表2に示す。
- スペースの制約により、代表的なベースラインとして SPLADE-v3 と RepLlama-2 のみの結果を報告し、ベースライン比較の全体については Section D を参照されたい。

- RepLlama-2-7b は他の dense retrieval ベースラインと比較してより良いドメイン外性能 (平均 55.1 NDCG@10) を達成しており、最も競争力のある sparse retrieval 手法である SPLADE-v3 と比較しても優れている。
- 一方、CSPLADE-Echo-1B と CSPLADE-Bi-1B はそれぞれ平均 NDCG@10 スコアで 49.5 と 49.4 を達成しており、SPLADE-v3 を下回っている。
- これは、特にバックボーン LM の容量が限られている場合に、蒸留訓練の有効性を改めて示唆するものである。
- しかしながら、バックボーン言語モデルの容量を増加させると、性能は大幅に改善される。
- 例えば、CSPLADE-Echo-8B と CSplade-bi-8b は SPLADE-v3 を大きく上回り、RepLlama-2-7b と同等の性能を達成することができる。
- この観察は、提案手法の有効性がドメイン外のゼロショット検索にも一般化可能であることを示唆している。

4https://huggingface.co/meta-llama

<table>
<caption>表2: ゼロショットパッセージ検索評価の結果。各セクション内の最高性能を強調表示している。</caption>
<tr>
<th>Dataset</th>
<th>SPLADE-v3 110M</th>
<th>RepLlama-2 7B</th>
<th>CSPLADE-Echo-1B 1.3B</th>
<th>CSPLADE-Bi-1B 1.3B</th>
<th>CSPLADE-Echo-8B 8B</th>
<th>CSPLADE-Bi-8b 8B</th>
</tr>
<tr>
<td>Arguana</td>
<td>50.9</td>
<td>48.6</td>
<td>46.7</td>
<td>45.0</td>
<td>48.1</td>
<td>48.9</td>
</tr>
<tr>
<td>Climate-FEVER</td>
<td>23.3</td>
<td>31.0</td>
<td>23.8</td>
<td>21.8</td>
<td>29.5</td>
<td>29.4</td>
</tr>
<tr>
<td>DBPedia</td>
<td>45.0</td>
<td>43.7</td>
<td>39.5</td>
<td>39.0</td>
<td>45.2</td>
<td>44.5</td>
</tr>
<tr>
<td>FEVER</td>
<td>79.6</td>
<td>83.4</td>
<td>71.3</td>
<td>74.8</td>
<td>85.2</td>
<td>86.5</td>
</tr>
<tr>
<td>FİQA</td>
<td>37.4</td>
<td>45.8</td>
<td>35.0</td>
<td>36.3</td>
<td>39.9</td>
<td>40.5</td>
</tr>
<tr>
<td>HotpotQA</td>
<td>69.2</td>
<td>68.5</td>
<td>61.0</td>
<td>62.4</td>
<td>69.4</td>
<td>69.8</td>
</tr>
<tr>
<td>NFCorpus</td>
<td>35.7</td>
<td>37.8</td>
<td>33.2</td>
<td>32.4</td>
<td>37.7</td>
<td>37.2</td>
</tr>
<tr>
<td>NQ</td>
<td>58.6</td>
<td>62.4</td>
<td>54.5</td>
<td>55.4</td>
<td>59.8</td>
<td>60.9</td>
</tr>
<tr>
<td>Quora</td>
<td>81.4</td>
<td>86.8</td>
<td>81.5</td>
<td>79.6</td>
<td>86.9</td>
<td>87.1</td>
</tr>
<tr>
<td>SCIDOCS</td>
<td>15.8</td>
<td>18.1</td>
<td>16.0</td>
<td>15.1</td>
<td>17.4</td>
<td>17.6</td>
</tr>
<tr>
<td>SciFact</td>
<td>71.0</td>
<td>75.6</td>
<td>71.1</td>
<td>71.1</td>
<td>73.2</td>
<td>73.9</td>
</tr>
<tr>
<td>TREC-COVID</td>
<td>74.8</td>
<td>84.7</td>
<td>77.7</td>
<td>71.6</td>
<td>84.0</td>
<td>83.2</td>
</tr>
<tr>
<td>Touche-2020</td>
<td>29.3</td>
<td>30.5</td>
<td>32.1</td>
<td>37.7</td>
<td>38.5</td>
<td>38.9</td>
</tr>
<tr>
<td>Average</td>
<td>51.7</td>
<td>55.1</td>
<td>49.5</td>
<td>49.4</td>
<td>55.0</td>
<td>55.3</td>
</tr>
</table>

### 5.3 モデル量子化と推論レイテンシ

- LLMを実世界の検索アプリケーションに適用する上での大きな障害の一つはレイテンシである。
- そこで本研究では、learned sparse retrievalにおいて、広く用いられている推論最適化手法である量子化の有効性を検証する。
- 我々は、キャリブレーション不要の量子化手法として、LLM.int8 (Dettmers et al., 2022) と、PyTorchネイティブの量子化実装である torchao (torchao team, 2024) の2つを採用する。
- LLM.int8 については、BitsAndBytes5 における INT4 および INT8 の重みのみの量子化 (weight-only quantization) を使用する。
- torchao については、INT4 および INT8 の重みのみの量子化と、INT8 の重み・活性化量子化 (weight-and-activation quantization) の実装6を使用する。
- これらの量子化手法の詳細については Section E を参照されたい。

- 量子化手法および bfloat16 ベースラインについて、量子化されたモデルでより大きなバッチサイズを用いて転置インデックスを構築する。
- その後、バッチサイズを1に設定してモデルがクエリをエンコードする速度を計測することにより、レイテンシをベンチマークする。
- 検索性能としては MS MARCO DEV セットでの MRR@10 を報告し、レイテンシ指標として queries/second を用いる7。

- 量子化評価の結果を図1に示す。
- まず、低ビット量子化はモデルの性能を損なうことが分かる。
- 例えば、4-bit 量子化モデルでは性能の大幅な低下が見られる一方、8-bit 量子化モデルでは性能低下はそれほど深刻ではない。
- この観察は、既存の量子化評価に関する研究 (Dettmers and Zettlemoyer, 2023; Xu et al., 2024a; Hong et al., 2024, inter alia) と一致する。
- 推論速度の観点では、1B スケールにおいて、専用の GPU カーネルサポートがない場合、量子化されたモデルは GPU メモリ使用量こそ少なくて済むものの、Flash Attention 2 と torch.compile によって十分に最適化された bfloat16 ベースラインと比較すると、実際には推論速度が遅くなることが分かった。
- 我々はまた、キャリブレーションを必要とする量子化手法、すなわち GPTQ (Frantar et al., 2023) と AWQ (Lin et al., 2024) でも実験を行ったが、これらは深刻な性能低下 (MRR@10 が 10 未満) を引き起こすことが判明した。
- その理由は、キャリブレーションで用いられる causal language modeling 目的関数と、検索モデルのファインチューニングに用いられるランキング目的関数との間の不整合にある。
- 要約すると、我々の発見は、量子化手法に関するより慎重で的を絞った調査の必要性、ならびに検索モデルに特化した効率的な量子化モデル推論カーネルの開発の必要性を浮き彫りにしている。

### 5.4 失敗した試み

- 事前学習済み causal language model を learned sparse retrieval に適応させる実験全般を通じて、失敗に終わった2つの試みについて議論する。

- dying ReLU 問題を緩和するために、Gumbel-softmax トリック (Jang et al., 2016) に着想を得た biased reparameterization トリック (Wang et al., 2024b) を試した。
- このトリックを PyTorch スタイルで示すと以下のようになる。

z = F.relu(z).detach() + F.gelu(z)
\- F.gelu(z).detach()

- ここで z.detach() は z の勾配を消去する。

5https://github.com/bitsandbytes-foundation/
bitsandbytes

"https://github.com/pytorch/ao

7Lucene インデックスからの検索時間は含めず、バックボーン言語モデルからのエンコーディング速度のみに焦点を当てることとした。これは、Lucene の検索速度がすべての量子化手法で同じであり、主にインデックスサイズと CPU ハードウェア能力に依存するためである。

- このトリックを使うと、forward の出力は依然として F.relu(z) と等しくなるが、勾配は負の入力に対して勾配を持つ F.gelu(z) (Hendrycks and Gimpel, 2016) に関して計算される。
- GeLU の勾配は ReLU のそれとは異なるため、この再パラメータ化はバイアスを持ち、性能の低下を招く可能性がある。
- しかしながら、このトリックでは訓練の不安定性を完全には緩和できず、ハイパーパラメータの特定の組み合わせでは依然として訓練が失敗することが分かった。

- contrastive training フェーズにおいて、Llama-3 に対して LoRA ファインチューニングではなくフル・パラメータ・ファインチューニングを用いる実験も行った。
- その結果、BEIR データセットでの結果が劣化することが観察された一方で、BERT スケールのモデルでは同様の問題は顕著ではなかった。
- 我々は、Llama のような最新の causal LLM は広範な事前学習を経ているため過学習しやすいことが原因ではないかと推測している。
- この過学習問題については、今後の調査課題として残しておく。

## 6 関連研究

- 本節では、既存の learned sparse retrieval 手法について議論し、dense retrieval 手法に関しては既存のサーベイ論文 (Lin et al., 2022; Zhu et al., 2023b; Xu et al., 2025b) を参照されたい。
- Zamani et al. (2018) は、文書とクエリをスパースな高次元の潜在空間に埋め込み、l1 正則化によりスパース性を強制する SNRM を提案した。
- DeepCT (Dai and Callan, 2019) は、文脈化された表現を学習することで term の重み付けを再学習するが、この手法ではクエリと文書の拡張を採用していないため、語彙ミスマッチ問題を緩和することはできない。
- その後の研究では、SparTerm (Bai et al., 2020)、SPARTA (Zhao et al., 2020)、EPIC (MacAvaney et al., 2020) に代表されるように、拡張技術と対応する集約メカニズムにより検索性能をさらに改善している。

- SPLADE (Formal et al., 2021b) では、事前学習済み masked language model のマスク付き言語モデリングヘッドが、文脈化された表現を語彙空間へ射影するのに特に適していることを指摘している。
- さらに log(tf) (Fang et al., 2004) からインスピレーションを得て、性能向上のために FLOPs (Paria et al., 2020) 正則化を採用している。
- SPLADE のその後のバージョン (Formal et al., 2021a, 2022; Lassance et al., 2024) では、MaxPooling 集約メカニズムへの切り替えと、ハードネガティブのマイニングや cross-encoder 教師モデルからの蒸留などの洗練された訓練戦略を用いることで、さらなる改善を実現している。
- 後続の研究では、SparseEmbed (Kong et al., 2023)、SLIM (Li et al., 2023)、SPLATE (Formal et al., 2024) に代表されるように、関連性をよりよく捉えるためにクエリ-文書 term 間の細粒度な相互作用を可能にすることが提案されている。
- しかし、これらの研究はいずれも事前学習済みの masked language model、特に BERT (Devlin et al., 2019) ファミリーモデルに限定されている。
- 一部の同時並行的な研究では、encoder バックボーンを超えた SPLADE スタイルのモデル訓練が試みられている。
- Qiao et al. (2025) は、Flan-T5 (Chung et al., 2024) のような encoder-decoder モデルと、decoder-only の OPT (Zhang et al., 2022) を比較している。
- しかし、彼らの実験は 3B 規模のモデルに限定されており、より強力な事前学習済み LLM は含まれていない。
- Mistral-SPLADE (Doshi et al., 2024) は、Mistral-7B (Jiang et al., 2023) を echo embeddings (Springer et al., 2024) を用いて訓練している。
- 本研究では、事前学習済み LLM をバックボーンとした learned sparse retrieval モデルの訓練における課題を正式に検証し、対応する緩和戦略を提案する。

## 7 結論と今後の課題

- 本論文では、learned sparse retrieval、特にSPLADEを事前学習済みのcausal language modelへ拡張することに焦点を当てた。
- 我々は、訓練の不安定性問題と一方向情報の問題という2つの課題を特定した。
- これらの問題を解決するために、訓練の不安定性を解消する軽量なadaptation training phaseを提案するとともに、双方向情報を実現する2つのモデルバリアントを設計した。
- これらの手法により、index sizeを最小化したまま、8B規模の事前学習済みcausal language modelでSPLADEを訓練し、競争力のある性能を達成した。
- さらに、model quantizationがlearned sparse retrievalに与える影響を分析し、今後の改善に向けた示唆について議論した。

- 我々は今後の研究の方向性として2つを展望している。
- 訓練の観点からは、教師なしのadaptation phase trainingおよびその後の教師ありfine-tuningの双方において、データセット規模拡大の効果を慎重に検討すべきである (Hoffmann et al., 2022)。
- さらに、knowledge distillation (Hinton et al., 2015) やMatryoshka Representation Learning (Kusupati et al., 2022) のような異なる訓練戦略についても、引き続き探求の余地が残されている。
- 推論の観点からは、retrieverのバックボーンとしてのcausal LLMの推論レイテンシは依然として実用上の制約となっており、inference-free learned sparse retrieval (Formal et al., 2021b,a; Geng et al., 2025) は有望な今後の方向性である。
- さらに、learned sparse retrievalに特化したretrieval indexをいかに最適化するかも、もう一つの重要な課題である (Bruch et al., 2024)。

## 限界

- 本研究では、causal language modelをlearned sparse retrievalへ適用することに焦点を当てており、特にその高い性能からSPLADEを対象とした。
- 我々はLlama-3ファミリのモデルでベンチマークを行った。
- 提案手法が他のバックボーン言語モデルやlearned sparse retrieval手法に適用可能かどうかは、さらなる調査とベンチマークが必要である。
- 長文書に対するlearned sparse retrievalの有効性についても慎重に検証されるべきである。
- 紙面の制約から、model quantizationのさらなる調査は今後の課題として残す。

## 倫理的考察

- 本論文はモデリングの改善に焦点を当てており、実験は公開ベンチマーク上で実施されている。
- 我々の知る限り、本論文は潜在的な倫理的懸念やリスクを生じさせるものではない。

## 参考文献

Yang Bai, Xiaoguang Li, Gang Wang, Chaoliang Zhang,
Lifeng Shang, Jun Xu, Zhaowei Wang, Fangshan
Wang, and Qun Liu. 2020. Sparterm: Learning
term-based sparse representation for fast text retrieval.
arXiv preprint arXiv:2010.00768.

Payal Bajaj, Daniel Campos, Nick Craswell, Li Deng,
Jianfeng Gao, Xiaodong Liu, Rangan Majumder,
Andrew McNamara, Bhaskar Mitra, Tri Nguyen,
et al. 2016. Ms marco: A human generated ma-
chine reading comprehension dataset. arXiv preprint
arXiv: 1611.09268.

Parishad BehnamGhader, Vaibhav Adlakha, Marius
Mosbach, Dzmitry Bahdanau, Nicolas Chapados, and
Siva Reddy. 2024. Llm2vec: Large language models
are secretly powerful text encoders. arXiv preprint
arXiv:2404.05961.

Dan Biderman, Jacob Portes, Jose Javier Gonzalez Ortiz,
Mansheej Paul, Philip Greengard, Connor Jennings,
Daniel King, Sam Havens, Vitaliy Chiley, Jonathan
Frankle, et al. 2024. Lora learns less and forgets less.
Transactions on Machine Learning Research.

Alexander Bondarenko, Maik Fröbe, Meriem Be-
loucif, Lukas Gienapp, Yamen Ajjour, Alexander
Panchenko, Chris Biemann, Benno Stein, Henning
Wachsmuth, Martin Potthast, et al. 2020. Overview
of touché 2020: argument retrieval. In Experimental
IR Meets Multilinguality, Multimodality, and Interac-
tion: 11th International Conference of the CLEF As-
sociation, CLEF 2020, Thessaloniki, Greece, Septem-
ber 22-25, 2020, Proceedings 11, pages 384-395.
Springer.

Vera Boteva, Demian Gholipour, Artem Sokolov, and
Stefan Riezler. 2016. A full-text learning to rank
dataset for medical information retrieval. In Ad-
vances in Information Retrieval: 38th European Con-
ference on IR Research, ECIR 2016, Padua, Italy,
March 20-23, 2016. Proceedings 38, pages 716-722.
Springer.

Sebastian Bruch, Franco Maria Nardini, Cosimo Rulli,
and Rossano Venturini. 2024. Efficient inverted in-
dexes for approximate retrieval over learned sparse
representations. In Proceedings of the 47th Inter-
national ACM SIGIR Conference on Research and
Development in Information Retrieval, pages 152-
162.

Hyung Won Chung, Le Hou, Shayne Longpre, Barret
Zoph, Yi Tay, William Fedus, Yunxuan Li, Xuezhi
Wang, Mostafa Dehghani, Siddhartha Brahma, et al.
2024. Scaling instruction-finetuned language models.
Journal of Machine Learning Research, 25(70):1-53.

Arman Cohan, Sergey Feldman, Iz Beltagy, Doug
Downey, and Daniel S Weld. 2020. Specter:
Document-level representation learning using
citation-informed transformers. arXiv preprint
arXiv:2004.07180.

Zhuyun Dai and Jamie Callan. 2019. Deeper text un-
derstanding for ir with contextual neural language
modeling. In Proceedings of the 42nd international
ACM SIGIR conference on research and development
in information retrieval, pages 985-988.

Tri Dao. 2023. Flashattention-2: Faster attention with
better parallelism and work partitioning. arXiv
preprint arXiv:2307.08691.

Tim Dettmers, Mike Lewis, Younes Belkada, and Luke
Zettlemoyer. 2022. Gpt3. int8 (): 8-bit matrix mul-
tiplication for transformers at scale. Advances in
neural information processing systems, 35:30318-
30332.

Tim Dettmers and Luke Zettlemoyer. 2023. The case for
4-bit precision: k-bit inference scaling laws. In In-
ternational Conference on Machine Learning, pages
7750-7774. PMLR.

Jacob Devlin, Ming-Wei Chang, Kenton Lee, and
Kristina Toutanova. 2019. BERT: Pre-training of
deep bidirectional transformers for language under-
standing. In Proceedings of the 2019 Conference of
the North American Chapter of the Association for
Computational Linguistics: Human Language Tech-
nologies, Volume 1 (Long and Short Papers), pages
4171-4186, Minneapolis, Minnesota. Association for
Computational Linguistics.

Thomas Diggelmann, Jordan Boyd-Graber, Jannis Bu-
lian, Massimiliano Ciaramita, and Markus Leip-
pold. 2020. Climate-fever: A dataset for verifica-
tion of real-world climate claims. arXiv preprint
arXiv:2012.00614.

Meet Doshi, Vishwajeet Kumar, Rudra Murthy, Vignesh
P, and Jaydeep Sen. 2024. Mistral-splade: Llms for
better learned sparse retrieval.

Hui Fang, Tao Tao, and ChengXiang Zhai. 2004. A
formal study of information retrieval heuristics. In
Proceedings of the 27th annual international ACM
SIGIR conference on Research and development in
information retrieval, pages 49-56.

Yan Fang, Jingtao Zhan, Qingyao Ai, Jiaxin Mao, Wei-
hang Su, Jia Chen, and Yiqun Liu. 2024. Scaling
laws for dense retrieval. In Proceedings of the 47th
International ACM SIGIR Conference on Research
and Development in Information Retrieval, SIGIR
'24, page 1339-1349, New York, NY, USA. Associa-
tion for Computing Machinery.

Thibault Formal, Stéphane Clinchant, Hervé Déjean,
and Carlos Lassance. 2024. Splate: Sparse late in-
teraction retrieval. In Proceedings of the 47th Inter-
national ACM SIGIR Conference on Research and
Development in Information Retrieval, pages 2635-
2640.

Thibault Formal, Carlos Lassance, Benjamin Pi-
wowarski, and Stéphane Clinchant. 2022. From dis-
tillation to hard negative sampling: Making sparse
neural ir models more effective. In Proceedings of

the 45th International ACM SIGIR Conference on
Research and Development in Information Retrieval,
SIGIR '22, page 2353-2359, New York, NY, USA.
Association for Computing Machinery.

Thibault Formal, Carlos Lassance, Benjamin Pi-
wowarski, and Stéphane Clinchant. 2021a. Splade
v2: Sparse lexical and expansion model for informa-
tion retrieval.

Thibault Formal, Benjamin Piwowarski, and Stéphane
Clinchant. 2021b. SPLADE: Sparse Lexical and
Expansion Model for First Stage Ranking, page
2288-2292. Association for Computing Machinery,
New York, NY, USA.

Elias Frantar, Saleh Ashkboos, Torsten Hoefler, and Dan
Alistarh. 2023. OPTQ: Accurate quantization for
generative pre-trained transformers. In The Eleventh
International Conference on Learning Representa-
tions.

Luyu Gao and Jamie Callan. 2022. Unsupervised cor-
pus aware language model pre-training for dense pas-
sage retrieval. In Proceedings of the 60th Annual
Meeting of the Association for Computational Lin-
guistics (Volume 1: Long Papers), pages 2843-2853,
Dublin, Ireland. Association for Computational Lin-
guistics.

Luyu Gao, Xueguang Ma, Jimmy Lin, and Jamie Callan.
2022. Tevatron: An efficient and flexible toolkit for
dense retrieval. arXiv preprint arXiv:2203.05765.

Zhichao Geng, Yiwen Wang, Dongyu Ru, and Yang
Yang. 2025. Towards competitive search relevance
for inference-free learned sparse retrievers.

Aaron Grattafiori, Abhimanyu Dubey, Abhinav Jauhri,
Abhinav Pandey, Abhishek Kadian, Ahmad Al-
Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten,
Alex Vaughan, et al. 2024. The llama 3 herd of mod-
els. arXiv preprint arXiv:2407.21783.

Suchin Gururangan, Ana Marasović, Swabha
Swayamdipta, Kyle Lo, Iz Beltagy, Doug Downey,
and Noah A. Smith. 2020. Don't stop pretraining:
Adapt language models to domains and tasks. In
Proceedings of the 58th Annual Meeting of the
Association for Computational Linguistics, pages
8342-8360, Online. Association for Computational
Linguistics.

Faegheh Hasibi, Fedor Nikolaev, Chenyan Xiong, Krisz-
tian Balog, Svein Erik Bratsberg, Alexander Kotov,
and Jamie Callan. 2017. Dbpedia-entity v2: a test
collection for entity search. In Proceedings of the
40th International ACM SIGIR Conference on Re-
search and Development in Information Retrieval,
pages 1265-1268.

Dan Hendrycks and Kevin Gimpel. 2016. Gaus-
sian error linear units (gelus). arXiv preprint
arXiv: 1606.08415.

Geoffrey Hinton, Oriol Vinyals, and Jeff Dean. 2015.
Distilling the knowledge in a neural network.

Jordan Hoffmann, Sebastian Borgeaud, Arthur Men-
sch, Elena Buchatskaya, Trevor Cai, Eliza Ruther-
ford, Diego de Las Casas, Lisa Anne Hendricks,
Johannes Welbl, Aidan Clark, et al. 2022. Train-
ing compute-optimal large language models. arXiv
preprint arXiv:2203.15556.

Sebastian Hofstätter, Sophia Althammer, Michael
Schröder, Mete Sertkan, and Allan Hanbury. 2020.
Improving efficient neural ranking models with cross-
architecture knowledge distillation. arXiv preprint
arXiv:2010.02666.

Junyuan Hong, Jinhao Duan, Chenhui Zhang,
Zhangheng Li, Chulin Xie, Kelsey Lieberman, James
Diffenderfer, Brian R Bartoldson, Ajay Kumar
Jaiswal, Kaidi Xu, et al. 2024. Decoding compressed
trust: Scrutinizing the trustworthiness of efficient
llms under compression. In International Conference
on Machine Learning, pages 18611-18633. PMLR.

Edward J Hu, Yelong Shen, Phillip Wallis, Zeyuan
Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, and
Weizhu Chen. 2021. Lora: Low-rank adaptation of
large language models. arxiv 2021. arXiv preprint
arXiv:2106.09685.

Eric Jang, Shixiang Gu, and Ben Poole. 2016. Categori-
cal reparameterization with gumbel-softmax. arXiv
preprint arXiv: 1611.01144.

Albert Qiaochu Jiang, Alexandre Sablayrolles, Arthur
Mensch, Chris Bamford, Devendra Singh Chap-
lot, Diego de Las Casas, Florian Bressand, Gi-
anna Lengyel, Guillaume Lample, Lucile Saulnier,
L'elio Renard Lavaud, Marie-Anne Lachaux, Pierre
Stock, Teven Le Scao, Thibaut Lavril, Thomas Wang,
Timothée Lacroix, and William El Sayed. 2023. Mis-
tral 7b. ArXiv, abs/2310.06825.

Jared Kaplan, Sam McCandlish, Tom Henighan, Tom B
Brown, Benjamin Chess, Rewon Child, Scott Gray,
Alec Radford, Jeffrey Wu, and Dario Amodei. 2020.
Scaling laws for neural language models. arXiv
preprint arXiv:2001.08361.

Vladimir Karpukhin, Barlas Oguz, Sewon Min, Patrick
Lewis, Ledell Wu, Sergey Edunov, Danqi Chen, and
Wen-tau Yih. 2020. Dense passage retrieval for open-
domain question answering. In Proceedings of the
2020 Conference on Empirical Methods in Natural
Language Processing (EMNLP), pages 6769-6781,
Online. Association for Computational Linguistics.

Weize Kong, Jeffrey M. Dudek, Cheng Li, Mingyang
Zhang, and Michael Bendersky. 2023. Sparseembed:
Learning sparse lexical representations with contex-
tual embeddings for retrieval. In Proceedings of the
46th International ACM SIGIR Conference on Re-
search and Development in Information Retrieval,
SIGIR '23, page 2399-2403, New York, NY, USA.
Association for Computing Machinery.

Aditya Kusupati, Gantavya Bhatt, Aniket Rege,
Matthew Wallingford, Aditya Sinha, Vivek Ramanu-
jan, William Howard-Snyder, Kaifeng Chen, Sham
Kakade, Prateek Jain, et al. 2022. Matryoshka repre-
sentation learning. Advances in Neural Information
Processing Systems, 35:30233-30249.

Tom Kwiatkowski, Jennimaria Palomaki, Olivia Red-
field, Michael Collins, Ankur Parikh, Chris Alberti,
Danielle Epstein, Illia Polosukhin, Jacob Devlin, Ken-
ton Lee, Kristina Toutanova, Llion Jones, Matthew
Kelcey, Ming-Wei Chang, Andrew M. Dai, Jakob
Uszkoreit, Quoc Le, and Slav Petrov. 2019. Natu-
ral questions: A benchmark for question answering
research. Transactions of the Association for Compu-
tational Linguistics, 7:452-466.

Carlos Lassance, Hervé Déjean, Thibault Formal, and
Stéphane Clinchant. 2024. Splade-v3: New baselines
for splade. arXiv preprint arXiv:2403.06789.

Chankyu Lee, Rajarshi Roy, Mengyao Xu, Jonathan
Raiman, Mohammad Shoeybi, Bryan Catanzaro, and
Wei Ping. 2024. Nv-embed: Improved techniques for
training llms as generalist embedding models. arXiv
preprint arXiv:2405.17428.

Minghan Li, Sheng-Chieh Lin, Xueguang Ma, and
Jimmy Lin. 2023. Slim: Sparsified late interaction
for multi-vector retrieval with inverted indexes. In
Proceedings of the 46th International ACM SIGIR
Conference on Research and Development in Infor-
mation Retrieval, pages 1954-1959.

Ji Lin, Jiaming Tang, Haotian Tang, Shang Yang, Wei-
Ming Chen, Wei-Chen Wang, Guangxuan Xiao,
Xingyu Dang, Chuang Gan, and Song Han. 2024.
Awq: Activation-aware weight quantization for on-
device llm compression and acceleration. In Proceed-
ings of Machine Learning and Systems, volume 6,
pages 87-100.

Jimmy Lin, Xueguang Ma, Sheng-Chieh Lin, Jheng-
Hong Yang, Ronak Pradeep, and Rodrigo Nogueira.
2021. Pyserini: An easy-to-use python toolkit to
support replicable ir research with sparse and dense
representations. arXiv preprint arXiv:2102.10073.

Jimmy Lin, Rodrigo Nogueira, and Andrew Yates. 2022.
Pretrained transformers for text ranking: Bert and
beyond. Springer Nature.

Lu Lu, Yeonjong Shin, Yanhui Su, and George Em
Karniadakis. 2019. Dying relu and initialization:
Theory and numerical examples. arXiv preprint
arXiv:1903.06733.

Xueguang Ma, Liang Wang, Nan Yang, Furu Wei, and
Jimmy Lin. 2024. Fine-tuning llama for multi-stage
text retrieval. In Proceedings of the 47th Inter-
national ACM SIGIR Conference on Research and
Development in Information Retrieval, pages 2421-
2425.

Sean MacAvaney, Franco Maria Nardini, Raffaele
Perego, Nicola Tonellotto, Nazli Goharian, and Ophir
Frieder. 2020. Expansion via prediction of impor-
tance with contextualization. In Proceedings of the
43rd International ACM SIGIR conference on re-
search and development in Information Retrieval,
pages 1573-1576.

Macedo Maia, Siegfried Handschuh, André Freitas,
Brian Davis, Ross McDermott, Manel Zarrouk, and
Alexandra Balahur. 2018. Www'18 open challenge:
financial opinion mining and question answering. In
Companion proceedings of the the web conference
2018, pages 1941-1942.

Antonio Mallia, Omar Khattab, Torsten Suel, and Nicola
Tonellotto. 2021. Learning passage impacts for in-
verted indexes. In Proceedings of the 44th Inter-
national ACM SIGIR Conference on Research and
Development in Information Retrieval, pages 1723-
1727.

Niklas Muennighoff. 2022. Sgpt: Gpt sentence
embeddings for semantic search. arXiv preprint
arXiv:2202.08904.

Jianmo Ni, Chen Qu, Jing Lu, Zhuyun Dai, Gustavo
Hernandez Abrego, Ji Ma, Vincent Zhao, Yi Luan,
Keith Hall, Ming-Wei Chang, and Yinfei Yang. 2022.
Large dual encoders are generalizable retrievers. In
Proceedings of the 2022 Conference on Empirical
Methods in Natural Language Processing, pages
9844-9855, Abu Dhabi, United Arab Emirates. As-
sociation for Computational Linguistics.

Aaron van den Oord, Yazhe Li, and Oriol Vinyals. 2018.
Representation learning with contrastive predictive
coding. arXiv preprint arXiv: 1807.03748.

Biswajit Paria, Chih-Kuan Yeh, Ian EH Yen, Ning Xu,
Pradeep Ravikumar, and Barnabás Póczos. 2020.
Minimizing flops to learn efficient sparse represen-
tations. In International Conference on Learning
Representations.

Jacob Portes, Alexander Trott, Sam Havens, Daniel
King, Abhinav Venigalla, Moin Nadeem, Nikhil Sar-
dana, Daya Khudia, and Jonathan Frankle. 2023. Mo-
saicbert: A bidirectional encoder optimized for fast
pretraining. Advances in Neural Information Pro-
cessing Systems, 36:3106-3130.

Jingfen Qiao, Thong Nguyen, Evangelos Kanoulas, and
Andrew Yates. 2025. Leveraging decoder architec-
tures for learned sparse retrieval. arXiv preprint
arXiv:2504.18151.

Yingqi Qu, Yuchen Ding, Jing Liu, Kai Liu, Ruiyang
Ren, Wayne Xin Zhao, Daxiang Dong, Hua Wu, and
Haifeng Wang. 2021. RocketQA: An optimized train-
ing approach to dense passage retrieval for open-
domain question answering. In Proceedings of the
2021 Conference of the North American Chapter of
the Association for Computational Linguistics: Hu-
man Language Technologies, pages 5835-5847, On-
line. Association for Computational Linguistics.

Colin Raffel, Noam Shazeer, Adam Roberts, Katherine
Lee, Sharan Narang, Michael Matena, Yanqi Zhou,
Wei Li, and Peter J Liu. 2020. Exploring the lim-
its of transfer learning with a unified text-to-text
transformer. Journal of machine learning research,
21(140):1-67.

Stephen E Robertson, Steve Walker, Susan Jones,
Micheline M Hancock-Beaulieu, Mike Gatford, et al.
1995. Okapi at trec-3. Nist Special Publication Sp,
109:109.

Gerard Salton. 1984. The use of extended boolean
logic in information retrieval. In Proceedings of the
1984 ACM SIGMOD International Conference on
Management of Data, SIGMOD '84, page 277-285,
New York, NY, USA. Association for Computing
Machinery.

Karen Sparck Jones. 1972. A statistical interpretation
of term specificity and its application in retrieval.
Journal of documentation, 28(1):11-21.

Jacob Mitchell Springer, Suhas Kotha, Daniel Fried,
Graham Neubig, and Aditi Raghunathan. 2024. Rep-
etition improves language model embeddings. arXiv
preprint arXiv:2402.15449.

Nandan Thakur, Nils Reimers, Andreas Rücklé, Ab-
hishek Srivastava, and Iryna Gurevych. 2021. BEIR:
A heterogeneous benchmark for zero-shot evaluation
of information retrieval models. In Thirty-fifth Con-
ference on Neural Information Processing Systems
Datasets and Benchmarks Track (Round 2).

James Thorne, Andreas Vlachos, Christos
Christodoulopoulos, and Arpit Mittal. 2018.
Fever: a large-scale dataset for fact extraction and
verification. arXiv preprint arXiv: 1803.05355.

torchao team. 2024. torchao: Pytorch native quantiza-
tion and sparsity for training and inference.

Hugo Touvron, Louis Martin, Kevin Stone, Peter Al-
bert, Amjad Almahairi, Yasmine Babaei, Nikolay
Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti
Bhosale, et al. 2023. Llama 2: Open founda-
tion and fine-tuned chat models. arXiv preprint
arXiv:2307.09288.

Ellen Voorhees, Tasmeer Alam, Steven Bedrick, Dina
Demner-Fushman, William R Hersh, Kyle Lo, Kirk
Roberts, Ian Soboroff, and Lucy Lu Wang. 2021.
Trec-covid: constructing a pandemic information re-
trieval test collection. In ACM SIGIR Forum, vol-
ume 54, pages 1-12. ACM New York, NY, USA.

Henning Wachsmuth, Shahbaz Syed, and Benno Stein.
2018. Retrieval of the best counterargument without
prior topic knowledge. In Proceedings of the 56th
Annual Meeting of the Association for Computational
Linguistics (Volume 1: Long Papers), pages 241-251.

David Wadden, Shanchuan Lin, Kyle Lo, Lucy Lu
Wang, Madeleine van Zuylen, Arman Cohan, and
Hannaneh Hajishirzi. 2020. Fact or fiction: Verifying
scientific claims. arXiv preprint arXiv:2004.14974.

Liang Wang, Nan Yang, Xiaolong Huang, Binxing Jiao,
Linjun Yang, Daxin Jiang, Rangan Majumder, and
Furu Wei. 2023. SimLM: Pre-training with repre-
sentation bottleneck for dense passage retrieval. In
Proceedings of the 61st Annual Meeting of the As-
sociation for Computational Linguistics (Volume 1:
Long Papers), pages 2244-2258, Toronto, Canada.
Association for Computational Linguistics.

Liang Wang, Nan Yang, Xiaolong Huang, Linjun Yang,
Rangan Majumder, and Furu Wei. 2024a. Improv-
ing text embeddings with large language models. In
Proceedings of the 62nd Annual Meeting of the As-
sociation for Computational Linguistics (Volume 1:
Long Papers), pages 11897-11916, Bangkok, Thai-
land. Association for Computational Linguistics.

Yifei Wang, Qi Zhang, Yaoyu Guo, and Yisen Wang.
2024b. Non-negative contrastive learning. In The
Twelfth International Conference on Learning Repre-
sentations.

Benjamin Warner, Antoine Chaffin, Benjamin Clavié,
Orion Weller, Oskar Hallström, Said Taghadouini,
Alexis Gallagher, Raja Biswas, Faisal Ladhak, Tom
Aarsen, et al. 2024. Smarter, better, faster, longer:
A modern bidirectional encoder for fast, memory
efficient, and long context finetuning and inference.
arXiv preprint arXiv:2412.13663.

Thomas Wolf, Lysandre Debut, Victor Sanh, Julien
Chaumond, Clement Delangue, Anthony Moi, Pier-
ric Cistac, Tim Rault, Rémi Louf, Morgan Funtowicz,
et al. 2019. Huggingface's transformers: State-of-
the-art natural language processing. arXiv preprint
arXiv: 1910.03771.

Lee Xiong, Chenyan Xiong, Ye Li, Kwok-Fung Tang,
Jialin Liu, Paul N. Bennett, Junaid Ahmed, and
Arnold Overwijk. 2021. Approximate nearest neigh-
bor negative contrastive learning for dense text re-
trieval. In International Conference on Learning
Representations.

Zhichao Xu. 2023. Context-aware decoding reduces
hallucination in query-focused summarization.

Zhichao Xu. 2024. Rankmamba: Benchmarking
mamba's document ranking performance in the era
of transformers.

Zhichao Xu and Daniel Cohen. 2023. A lightweight
constrained generation alternative for query-focused
summarization. In Proceedings of the 46th Inter-
national ACM SIGIR Conference on Research and
Development in Information Retrieval, pages 1745-
1749.

Zhichao Xu, Ashim Gupta, Tao Li, Oliver Bentham, and
Vivek Srikumar. 2024a. Beyond perplexity: Multi-
dimensional safety evaluation of LLM compression.
In Findings of the Association for Computational
Linguistics: EMNLP 2024, pages 15359-15396, Mi-
ami, Florida, USA. Association for Computational
Linguistics.

Zhichao Xu, Zhiqi Huang, Shengyao Zhuang, and Vivek
Srikumar. 2025a. Distillation versus contrastive
learning: How to train your rerankers.

Zhichao Xu, Hemank Lamba, Qingyao Ai, Joel
Tetreault, and Alex Jaimes. 2024b. Cfe2: Counter-
factual editing for search result explanation. In Pro-
ceedings of the 2024 ACM SIGIR International Con-
ference on Theory of Information Retrieval, pages
145-155.

Zhichao Xu, Fengran Mo, Zhiqi Huang, Crystina Zhang,
Puxuan Yu, Bei Wang, Jimmy Lin, and Vivek Sriku-
mar. 2025b. A survey of model architectures in infor-
mation retrieval.

Zhilin Yang, Peng Qi, Saizheng Zhang, Yoshua Ben-
gio, William W Cohen, Ruslan Salakhutdinov, and
Christopher D Manning. 2018. Hotpotqa: A dataset
for diverse, explainable multi-hop question answer-
ing. arXiv preprint arXiv: 1809.09600.

Andrew Yates, Carlos Lassance, Sean MacAvaney,
Thong Nguyen, and Yibin Lei. 2024. Neural lexical
search with learned sparse retrieval. In Proceedings
of the 2024 Annual International ACM SIGIR Con-
ference on Research and Development in Information
Retrieval in the Asia Pacific Region, pages 303-306.

Hamed Zamani, Mostafa Dehghani, W Bruce Croft,
Erik Learned-Miller, and Jaap Kamps. 2018. From
neural re-ranking to neural ranking: Learning a
sparse representation for inverted indexing. In Pro-
ceedings of the 27th ACM international conference
on information and knowledge management, pages
497-506.

Susan Zhang, Stephen Roller, Naman Goyal, Mikel
Artetxe, Moya Chen, Shuohui Chen, Christopher De-
wan, Mona Diab, Xian Li, Xi Victoria Lin, et al. 2022.
Opt: Open pre-trained transformer language models.
arXiv preprint arXiv:2205.01068.

Yanzhao Zhang, Mingxin Li, Dingkun Long, Xin Zhang,
Huan Lin, Baosong Yang, Pengjun Xie, An Yang,
Dayiheng Liu, Junyang Lin, et al. 2025. Qwen3
embedding: Advancing text embedding and rerank-
ing through foundation models. arXiv preprint
arXiv:2506.05176.

Tiancheng Zhao, Xiaopeng Lu, and Kyusong Lee. 2020.
Sparta: Efficient open-domain question answering
via sparse transformer matching retrieval. arXiv
preprint arXiv:2009.13013.

Yanli Zhao, Andrew Gu, Rohan Varma, Liang Luo,
Chien-Chin Huang, Min Xu, Less Wright, Hamid
Shojanazeri, Myle Ott, Sam Shleifer, et al. 2023. Py-
torch fsdp: experiences on scaling fully sharded data
parallel. arXiv preprint arXiv: 2304.11277.

Yutao Zhu, Huaying Yuan, Shuting Wang, Jiongnan Liu,
Wenhan Liu, Chenlong Deng, Haonan Chen, Zheng
Liu, Zhicheng Dou, and Ji-Rong Wen. 2023a. Large
language models for information retrieval: A survey.
arXiv preprint arXiv:2308.07107.

Yutao Zhu, Huaying Yuan, Shuting Wang, Jiongnan Liu,
Wenhan Liu, Chenlong Deng, Haonan Chen, Zheng
Liu, Zhicheng Dou, and Ji-Rong Wen. 2023b. Large
language models for information retrieval: A survey.
arXiv preprint arXiv:2308.07107.

Shengyao Zhuang, Xueguang Ma, Bevan Koopman,
Jimmy Lin, and Guido Zuccon. 2024. PromptReps:
Prompting large language models to generate dense
and sparse representations for zero-shot document
retrieval. In Proceedings of the 2024 Conference on
Empirical Methods in Natural Language Processing,
pages 4375-4391, Miami, Florida, USA. Association
for Computational Linguistics.

## A 適応学習における損失関数のコード

- 擬似コードを Figure 2 に示す。

## B データセットの詳細

- 実験に使用したデータセットのうち4つ (NF-Corpus (Boteva et al., 2016)、FiQA-2018 (Maia et al., 2018)、Quora8、Climate-Fever (Diggelmann et al., 2020)) は、論文やリポジトリにデータセットライセンスを記載していない。
- 残りのデータセットについては、以下にライセンスを示す。

- · MS MARCO (Bajaj et al., 2016): MIT License (非商用研究目的)。

- · ArguAna (Wachsmuth et al., 2018): CC BY 4.0。

- · DBPedia (Hasibi et al., 2017): CC BY-SA 3.0。

- · FEVER (Thorne et al., 2018): CC BY-SA 3.0。

- · HotpotQA (Yang et al., 2018): CC BY-SA 4.0。

- · NQ (Kwiatkowski et al., 2019): CC BY-SA 3.0。

- . SCIDOCS (Cohan et al., 2020): GNU General Public License v3.0。

- . SciFact (Wadden et al., 2020): CC BY-NC 2.0。

- · TREC-COVID (Voorhees et al., 2021): "Dataset License Agreement"。

- · Touche-2020 (Bondarenko et al., 2020): CC BY 4.0。

## C ハイパーパラメータの詳細

- ハイパーパラメータの詳細を表3に示す。
- 我々は主に4つのハイパーパラメータをチューニングした：learning rate、LoRA Rank、FLOPs正則化係数 $\lambda_Q$ 、および $\lambda_D$ である。
- LoRA Rank を増やしても検索性能の向上は見られず、むしろ BEIR データセットでの性能低下を引き起こすことが分かったため、8B モデルでは rank=16 を使用している。
- 1B モデルは 8x A100 40GB GPU を搭載した単一の EC2 p4d.24xlarge インスタンスで学習し、8B モデルは 2 台の p4d.24xlarge インスタンスで学習している。

## D 追加実験結果

- 追加の BEIR の結果を表4に示す。

## E 量子化評価の詳細

### E.1 量子化手法

- 我々は、AWQ (Lin et al., 2024) や GPTQ (Frantar et al., 2023) を含む、キャリブレーションを必要とする量子化手法を試したが、モデルのファインチューニングとキャリブレーションの目的関数が整合していないことに起因する性能の大幅な低下が見られた。
- そのため、キャリブレーション不要の量子化手法に焦点を絞ることにした。

### E.2 ハードウェア

- 推論速度は、40GBメモリを搭載した単一の A100 GPU 上で測定した。
- bfloat16 ベースラインには torch.compile および Flash Attention 2 を使用している。

### E.3 8Bモデルの結果

- 8Bモデルの量子化結果を図3に示す。
- 8Bスケールでは、1Bモデルと比較して性能低下がそれほど深刻ではなく、torchao W8A16 量子化は bfloat16 ベースラインと比較して推論速度を改善することが分かった。

8https://www.kaggle.com/c/
quora-question-pairs

\# Input:

\# x: input sequence of tokens, shape (batch_size, sequence_length)

\# model: causal language model

\# targets: target sequence, which is the same as input, shifted by 1
\# loss_fn: cross-entropy loss function

\# adapt_loss_factor: hyperparameter to control the balance between two terms

import torch

\# Model predicts logits for each token in the sequence
logits = model(x) # (batch_size, sequence_length, vocabulary)
shift_logits = logits[:, :- 1, :] # Shift the logits by 1
shift_targets = x[:, 1:] # Shift the input sequence to get the target sequence

\# Compute the causal language modeling loss
\# Note that the tensors need to be flattened to be used in torch CrossEntropyLoss
clm_loss = loss_fn(shift_logits.view(-1, vocab_size), shift_targets.view(-1))

adapt_logits = torch. log(1 + torch.relu(shift_logits))
adapt_loss = loss_fn(adapt_logits.view(-1, vocab_size), shift_targets.view(-1))

loss = clm_loss + adapt_loss_factor * adapt_loss

\# Return the computed loss

return loss

<table>
<caption>図2: 適応フェーズの学習損失計算のための疑似コード。表3: CSPLADE の学習に使用したハイパーパラメータ。学習率のウォームアップには総学習ステップ数の 5% を使用する。Global BZ はグローバルバッチサイズを表す。</caption>
<tr>
<th>Model</th>
<th>LR</th>
<th>LR Scheduler</th>
<th>#Epochs</th>
<th>Global BZ</th>
<th>LoRA Rank</th>
<th>10</th>
<th>XD</th>
</tr>
<tr>
<td>CSPLADE-1B</td>
<td>5e-5</td>
<td>Cosine</td>
<td>3</td>
<td>32</td>
<td>64</td>
<td>0.003</td>
<td>0.003</td>
</tr>
<tr>
<td>CSPLADE-Echo-1B</td>
<td>5e-5</td>
<td>Cosine</td>
<td>3</td>
<td>32</td>
<td>64</td>
<td>0.003</td>
<td>0.003</td>
</tr>
<tr>
<td>CSPLADE-Bi-1B</td>
<td>5e-5</td>
<td>Cosine</td>
<td>3</td>
<td>32</td>
<td>64</td>
<td>0.003</td>
<td>0.003</td>
</tr>
<tr>
<td>CSPLADE-8B</td>
<td>1e-4</td>
<td>Cosine</td>
<td>1</td>
<td>32</td>
<td>16</td>
<td>0.03</td>
<td>0.03</td>
</tr>
<tr>
<td>CSPLADE-Echo-8B</td>
<td>1e-4</td>
<td>Cosine</td>
<td>1</td>
<td>32</td>
<td>16</td>
<td>0.03</td>
<td>0.03</td>
</tr>
<tr>
<td>CSPLADE-Bi-8B</td>
<td>1e-4</td>
<td>Cosine</td>
<td>1</td>
<td>32</td>
<td>16</td>
<td>0.03</td>
<td>0.03</td>
</tr>
</table>

<table>
<caption>表4: ゼロショットパッセージ検索評価の追加結果。各セクション内で最良の性能を強調表示している。</caption>
<tr>
<th rowspan="2">Dataset</th>
<th rowspan="2">BM25 -</th>
<th rowspan="2">SPLADE++ 110M</th>
<th>SparseEmbed</th>
<th>SGPT</th>
<th rowspan="2">CSPLADE-1B 1.3B</th>
<th rowspan="2">CSPLADE-8B 8B</th>
</tr>
<tr>
<th>110M</th>
<th>5.8B</th>
</tr>
<tr>
<td>Arguana</td>
<td>39.7</td>
<td>52.5</td>
<td>51.2</td>
<td>51.4</td>
<td>44.7</td>
<td>45.2</td>
</tr>
<tr>
<td>Climate-FEVER</td>
<td>16.5</td>
<td>23.0</td>
<td>21.8</td>
<td>30.5</td>
<td>19.5</td>
<td>27.2</td>
</tr>
<tr>
<td>DBPedia</td>
<td>31.8</td>
<td>43.6</td>
<td>45.7</td>
<td>39.9</td>
<td>39.2</td>
<td>41.8</td>
</tr>
<tr>
<td>FEVER</td>
<td>65.1</td>
<td>79.3</td>
<td>79.6</td>
<td>78.3</td>
<td>73.3</td>
<td>82.3</td>
</tr>
<tr>
<td>FiQA</td>
<td>23.6</td>
<td>34.8</td>
<td>33.5</td>
<td>37.2</td>
<td>33.2</td>
<td>39.5</td>
</tr>
<tr>
<td>HotpotQA</td>
<td>63.3</td>
<td>68.7</td>
<td>69.7</td>
<td>59.3</td>
<td>63.6</td>
<td>66.3</td>
</tr>
<tr>
<td>NFCorpus</td>
<td>32.2</td>
<td>34.8</td>
<td>34.1</td>
<td>36.2</td>
<td>36.5</td>
<td>35.7</td>
</tr>
<tr>
<td>NQ</td>
<td>30.6</td>
<td>53.7</td>
<td>54.4</td>
<td>52.4</td>
<td>52.9</td>
<td>58.8</td>
</tr>
<tr>
<td>Quora</td>
<td>78.9</td>
<td>83.4</td>
<td>84.9</td>
<td>84.6</td>
<td>81.0</td>
<td>87.7</td>
</tr>
<tr>
<td>SCIDOCS</td>
<td>14.9</td>
<td>15.9</td>
<td>16.0</td>
<td>19.7</td>
<td>15.8</td>
<td>17.0</td>
</tr>
<tr>
<td>SciFact</td>
<td>67.9</td>
<td>70.2</td>
<td>70.6</td>
<td>74.7</td>
<td>71.2</td>
<td>72.2</td>
</tr>
<tr>
<td>TREC-COVID</td>
<td>59.5</td>
<td>72.7</td>
<td>72.4</td>
<td>87.3</td>
<td>68.4</td>
<td>79.2</td>
</tr>
<tr>
<td>Touche-2020</td>
<td>44.2</td>
<td>24.5</td>
<td>27.3</td>
<td>25.4</td>
<td>34.8</td>
<td>38.0</td>
</tr>
<tr>
<td>Average</td>
<td>43.7</td>
<td>50.5</td>
<td>50.9</td>
<td>52.1</td>
<td>48.8</td>
<td>53.1</td>
</tr>
