# SPLADE v2: Sparse Lexical and Expansion Model for Information Retrieval

Thibault Formal
Naver Labs Europe
Meylan, France
Sorbonne Université, LIP6
Paris, France
thibault.formal@naverlabs.com

Carlos Lassance
Naver Labs Europe
Meylan, France
carlos.lassance@naverlabs.com

## 概要

- ニューラル情報検索 (IR) の分野では、ランキングパイプラインにおける first retriever (一次検索器) の改善に向けた研究が継続的に進められている。
- 効率的な近似最近傍探索手法を用いて検索を行うために密 (dense) な埋め込みを学習するアプローチは、有効に機能することが示されている。
- 一方で、文書とクエリに対する疎 (sparse) 表現の学習にも関心が高まっている。
- これは、bag-of-words モデルが持つ望ましい特性、すなわち単語の厳密一致 (exact matching) や転置インデックス (inverted index) の効率性を継承できるためである。
- 最近提案された SPLADE モデルは、非常に疎な表現を提供しつつ、最先端の密・疎手法と比較して競争力のある結果を達成している。
- 本論文では、SPLADE をベースに、有効性および/または効率性の面でいくつかの重要な改善を提案する。
- 具体的には、プーリング機構を変更し、文書拡張のみに基づくモデルをベンチマークし、蒸留 (distillation) によって学習されたモデルを導入する。
- また、BEIR ベンチマークでの結果も報告する。
- 全体として、SPLADE は大幅に改善され、TREC DL 2019 において NDCG@10 で 9% 以上の向上を達成し、BEIR ベンチマークにおいて最先端の結果をもたらす。

## キーワード

ニューラルネットワーク、インデキシング、疎表現、正則化

## 1 はじめに

- BERT [7] のような大規模事前学習済み言語モデルの登場は、自然言語処理および情報検索の分野に大きな変革をもたらした。
- これらのモデルは、シンプルなファインチューニングによって様々なタスクに適応する高い能力を示してきた。
- 2019年初頭、Nogueira と Cho [19] は MS MARCO passage re-ranking タスクにおいて、大幅な差をつけて当時の最先端の結果を達成し、

Benjamin Piwowarski
Sorbonne Université, CNRS, LIP6
Paris, France
benjamin.piwowarski@lip6.fr

Stéphane Clinchant
Naver Labs Europe
Meylan, France
stephane.clinchant@naverlabs.com

- LM ベースのニューラルランキングモデルへの道を切り開いた。
- 厳しい効率性の要件のため、これらのモデルは当初、二段階ランキングパイプラインにおける re-ranker として用いられてきた。
- このパイプラインでは、第一段階の検索 (候補生成) は、転置インデックスに依存する bag-of-words モデル (例えば BM25) によって行われる。
- BOW モデルは依然として強力なベースラインであり続けているが [31]、長年にわたって課題とされてきた語彙ミスマッチ問題に悩まされており、関連する文書がクエリに出現する語を含まない場合がある。
- そのため、標準的な BOW アプローチを学習済み (ニューラル) なランカーで置き換える試みが行われてきた。
- このようなモデルの設計には、効率性とスケーラビリティに関するいくつかの課題があり、そのため、大部分の計算をオフラインで行え、オンライン推論が高速であるような手法が求められている。
- 近似最近傍探索を用いた密ベクトル検索は印象的な結果を示しているが [11, 16, 24, 30]、明示的な単語マッチングが存在しないため、依然として BOW モデルの恩恵を受けることができる (例えば両方のシグナルを組み合わせるなど)。
- したがって、最近ではクエリと文書のスパース表現を学習することへの関心が高まっている [1, 4, 8, 9, 18, 21, 32, 33]。
- これにより、モデルは BOW モデルの望ましい特性、すなわち (潜在的に) 単語の厳密なマッチング、転置インデックスの効率性、解釈可能性を継承することができる。
- さらに、IR における標準的な拡張モデルと同様に、暗黙的または明示的 (潜在的、文脈依存的) な拡張機構をモデル化することによって、これらのモデルは語彙ミスマッチを軽減することができる。

- 本論文では、SPLADE モデル [8] を基盤として、有効性または効率性の面で改善をもたらすいくつかの改良/修正を提案する。
- (1) SPLADE のプーリング機構を単純に修正することで、有効性を大幅に向上させることができる。
- (2) 同時に、クエリ拡張を行わないモデルの拡張版を提案する。
- このようなモデルは本質的により効率的である。
- なぜなら、すべてをオフラインで事前計算してインデックス化することができ、それでいて競争力のある結果を提供できるからである。
- (3) 最後に、蒸留技術 [12] を用いて SPLADE の性能を向上させ、MS MARCO passage ranking タスクおよび BEIR ゼロショット評価ベンチマーク [26] において、最先端に近い結果をもたらす。

## 2 関連研究

- BERT Siameseモデル[25]に基づくDense retrievalは、Question AnsweringおよびIR[10, 11, 13, 16, 24, 30]における候補生成の標準的なアプローチとなっている。

arXiv:2109.10086v1 [cs.IR] 21 Sep 2021

Permission to make digital or hard copies of all or part of this work for personal or
classroom use is granted without fee provided that copies are not made or distributed
for profit or commercial advantage and that copies bear this notice and the full citation
on the first page. Copyrights for components of this work owned by others than ACM
must be honored. Abstracting with credit is permitted. To copy otherwise, or republish,
to post on servers or to redistribute to lists, requires prior specific permission and/or a
fee. Request permissions from permissions@acm.org.

Conference'17, July 2017, Washington, DC, USA

@ 2021 Association for Computing Machinery.

ACM ISBN 978-x-xxxx-xxxx-x/YY/MM ... $15.00
https://doi.org/10.1145/nnnnnnn.nnnnnnn

- これらのモデルのバックボーンは依然として同じであるが、近年の研究では、最先端の結果を得るための学習戦略の重要性が強調されており、その範囲は改良されたネガティブサンプリング[11, 16]から蒸留[12, 16]まで多岐にわたる。
- ColBERT[14]はさらに踏み込み、トークンレベルの相互作用を後段に持ち越すことで、第1段階の検索にモデルを効率的に適用できるようにし、細粒度の相互作用をモデル化する効果を享受できるようにした。
- ただし、その代償として(サブ)タームごとに埋め込みを保存する必要があり、大規模コレクションに対するこのアプローチの実際のスケーラビリティに懸念が生じている。
- 我々の知る限り、近似最近傍(ANN)探索を使用することがIR指標に与える影響について論じた研究はごくわずかである[2, 27]。
- MS MARCOコレクションのサイズが中程度であるため、結果は通常、厳密な総当たり探索で報告されており、したがって実際の計算コストに関する指標は得られていない。

- Denseインデックスに代わるものとして、ターム(term)ベースのインデックスがある。
- 標準的なBOWモデルを基盤として、Zamaniらは初めてSNRM[32]を提案した: このモデルは、表現に対する $\ell_1$ 正則化により、文書とクエリをスパースな高次元の潜在空間に埋め込む。
- しかしながら、SNRMの有効性は限定的であり、その効率性も疑問視されている[22]。

- BERTの成功に動機づけられ、事前学習済みLMからスパースアプローチへ知識を転移する試みが行われてきた。
- DeepCT[4-6]は、語彙空間全体における文脈化されたターム重み(BOWのターム重みに類似)の学習に焦点を当てた。
- しかしながら、文書に関連付けられた語彙は依然として変わらないため、この種のアプローチでは語彙ミスマッチを解決できない。
- これは、検索のためのクエリ拡張の使用[4]によって裏付けられている。
- この問題に対する最初の解決策は、doc2query[21]やdoc2query-T5[20]のような生成的アプローチを用いて文書を拡張し、文書に対する拡張語を予測することである。
- 文書拡張は文書に新しいタームを追加することで語彙ミスマッチに対抗するとともに、既存のタームを繰り返すことで重要なタームを強調し、暗黙的に再重み付けを行う。

- 最近、DeepImpact[18]はdoc2query-T5の拡張とDeepCTの再重み付けを組み合わせて、タームインパクトを学習した。
- しかしながら、これらの拡張技術は、その学習方法(クエリの予測)が本質的に間接的であるため、進歩が制限されている。
- この問題に対する第2の解決策として、最近の研究[1, 8, 17, 33]で採用されているのは、文書(またはクエリ)の各タームによって含意される語彙の各タームの重要度を推定すること、すなわち、文書またはクエリのトークンと語彙の全トークンの間の相互作用行列を計算することである。
- これに続いて、集約メカニズム(SparTerm[1]とSPLADE[8]ではおおむね総和、EPIC[17]とSPARTA[33]では最大値)が適用され、文書またはクエリ全体に対する語彙の各タームの重要度重みを計算できるようになる。

- しかしながら、EPICとSPARTAの(文書)表現は、top-kプーリングに頼らない限り、構造上十分にスパースではなく、これに対してSparTermでは高速な検索が可能である。
- さらに、SparTermは(SNRMと同様に)明示的なスパース性正則化を含んでおらず、これがその性能を妨げている。
- 一方、SPLADEはそのような正則化に依拠するとともに、その他の重要な変更も加えており、この種のアプローチの効率性と有効性の両方を高め、拡張と圧縮をエンドツーエンドで学習するモデルを提供している。
- さらに、COIL[9]は、タームごとに密な表現を学習して文脈化されたターム照合を行うことで、完全一致メカニズムを再考することを提案したが、その代償としてインデックスサイズが増大している。

## 3 第一段階ランキングのためのスパースな語彙表現

- 本節ではまず、最近 [8] で導入された SPLADE モデルについて詳細に説明する。

### 3.1 SPLADE

- SPLADE は、Masked Language Model (MLM) 層のロジットに基づいて、BERT WordPiece 語彙 ( $|V| = 30522$ ) における項の重要度を予測する。
- より正確には、入力クエリまたは文書系列 (WordPiece トークン化後) $t = (t_1, t_2, \ldots, t_N)$ と、それに対応する BERT 埋め込み $(h_1, h_2, \ldots, h_N)$ を考える。
- 入力系列のトークン $i$ に対する、トークン $j$ (語彙) の重要度 $w_{ij}$ を考える:

$$
w_{ij} = \mathrm{transform}(h_i)^\top E_j + b_j, \quad j \in \{1, \ldots, |V|\} \tag{1}
$$

- ここで $E_j$ はトークン $j$ に対する BERT 入力埋め込み、 $b_j$ はトークンレベルのバイアス、 $\mathrm{transform}(\cdot)$ は GeLU 活性化と LayerNorm を持つ線形層である。
- 式(1) は MLM 予測と等価であり、したがって事前学習済み MLM モデルから初期化することもできる。
- 最終的な表現は、log 飽和効果を適用した後 [8]、入力系列のトークンにわたって重要度予測子を合計することで得られる:

$$
w_j = \sum_{i \in t} \log\!\left(1 + \mathrm{ReLU}(w_{ij})\right) \tag{2}
$$

- **ランキング損失.**
- $s(q, d)$ を、式(2) からの $q$ と $d$ の表現の内積によって得られるランキングスコアとする。
- バッチ内のクエリ $q_i$ 、正例文書 $d_i^+$ 、(ハード) ネガティブ文書 $d_i^-$ (例: BM25 サンプリング由来)、およびバッチ内のネガティブ文書集合 (他のクエリの正例文書) $\{d_{i,j}^-\}_j$ が与えられたとき、コントラスティブ損失を考える。
- これは、文書 $d_i^+$ 、 $d_i^-$ および $\{d_{i,j}^-\}_j$ の中で文書 $d_i^+$ が関連していると判定される確率の最大化として解釈できる:

$$
\mathcal{L}_{\text{rank-IBN}} = -\log \frac{e^{s(q_i, d_i^+)}}{e^{s(q_i, d_i^+)} + e^{s(q_i, d_i^-)} + \sum_{j} e^{s(q_i, d_{i,j}^-)}} \tag{3}
$$

- バッチ内ネガティブ (IBN) サンプリング戦略は、画像検索モデルの学習で広く使用されており、第一段階ランカーの学習において有効であることが示されている [13, 16, 24]。

- **スパース表現の学習.**
- 第一段階検索のためにスパース表現を学習するというアイデアは、 $\ell_1$ 正則化を用いた SNRM [32] にまで遡る。
- 後に [22] は、表現の $\ell_1$ ノルムを最小化することは、ポスティングリストが均等に分布することを保証するものではないため、最も効率的なインデックスにはつながらないことを指摘した。
- 標準的なインデックスでは、項頻度分布の Zipf 則的な性質によりこのことはさらに顕著である。
- バランスの取れたインデックスを得るために、Paria ら [22] は FLOPS 正則化器を導入した。
- これは、クエリと文書のスコアを計算するのに必要な浮動小数点演算の平均回数の滑らかな緩和であり、したがって検索時間と直接関係している。
- これは、トークン $j$ に対する活性化 (すなわち項が非ゼロ重みを持つ) 確率 $p_j$ の連続緩和として $a_j$ を用いて定義され、サイズ $N$ のバッチ内の文書 $d$ について $\bar{a}_j = \frac{1}{N} \sum_{i=1}^{N} w_j^{(d_i)}$ によって推定される。
- これにより、以下の正則化損失が得られる:

$$
\ell_{\mathrm{FLOPS}} = \sum_{j \in V} \bar{a}_j^2 = \sum_{j \in V}\left(\frac{1}{N}\sum_{i=1}^{N} w_j^{(d_i)}\right)^2 \tag{4}
$$

- **全体損失.**
- ランキング損失と正則化損失で式(2) のモデルを同時に最適化することにより、SPLADE は文書とクエリのスパースで拡張対応の表現のエンドツーエンド学習において、両者の長所を兼ね備える:

$$
\mathcal{L} = \mathcal{L}_{\text{rank-IBN}} + \lambda_q \, \ell_{\mathrm{FLOPS}}^q + \lambda_d \, \ell_{\mathrm{FLOPS}}^d \tag{5}
$$

- ここで $\ell_{\mathrm{FLOPS}}$ は式 4 のスパース FLOPS 正則化である。
- クエリと文書に対して 2 つの異なる正則化重み ( $\lambda_d$ と $\lambda_q$ ) を使用する。
- これにより、高速な検索に不可欠なクエリのスパース性により強い圧力をかけることが可能になる。

### 3.2 プーリング戦略

- 我々は、式(2) の合計を max プーリング演算に変更することを提案する:

$$
w_j = \max_{i \in t} \log\!\left(1 + \mathrm{ReLU}(w_{ij})\right) \tag{6}
$$

- このモデルは SPARTA や EPIC、ある程度は ColBERT との類似性をより強く持つようになる。
- 実験の節で示すように、これは SPLADE の性能を大幅に改善する。
- 以下では、max プーリングを SPLADE のデフォルト構成とし、対応するモデルを SPLADE-max と呼ぶ。

### 3.3 SPLADE 文書エンコーダ

- max プーリング演算に加えて、SPLADE の文書のみのバージョンを考える。
- この場合、クエリ拡張やクエリ項重み付けは行われず、ランキングスコアは単に以下で与えられる:

$$
s(q, d) = \sum_{j \in q} w_j^{(d)} \tag{7}
$$

- このような拡張は興味深い効率の向上をもたらす。
- なぜなら、ランキングスコアが文書項の重みのみに依存するため、すべてをオフラインで事前計算でき、推論コストが結果として削減されるからである。
- それでも実験で示すように競争力のある結果を提供する。
- 我々はこのモデルを SPLADE-doc と呼ぶ。

### 3.4 蒸留とハードネガティブ

- 我々は、[12] で示された改善に従い、訓練手順に蒸留も組み込む。
- 蒸留の訓練は 2 ステップで行われる: (1) まず、[12] によって生成されたトリプレットを使用して、SPLADE 第一段階リトリーバとクロスエンコーダ・リランカ 1 の両方を訓練する。
- (2) 第 2 ステップでは、蒸留で訓練された SPLADE を用いてトリプレットを生成し (したがって BM25 よりも難しいネガティブを提供する)、前述のリランカを使用して Margin-MSE 損失に必要なスコアを生成する。
- 続いて、これらのトリプレットとスコアを使って SPLADE モデルをゼロから訓練する。
- 第 2 ステップの結果が、我々が DistilSPLADE-max と呼ぶものである。

## 4 実験設定と結果

- 我々はモデルを MS MARCO passage ranking dataset2 上で full ranking 設定により学習・評価した。
- 本データセットは約 8.8M の passage と、浅いアノテーション（クエリ 1 件あたり平均 ~ 1.1 件の関連 passage）を持つ数十万件の学習クエリを含む。
- development set には同様のラベルを持つ 6980 件のクエリが含まれており、TREC DL 2019 評価セットでは 43 件のクエリ集合に対して人間のアセッサによる詳細なアノテーションが提供されている [3]。

- **学習、インデックス、検索.**
- モデルは DistilBERT-base のチェックポイントで初期化した。
- モデルは ADAM オプティマイザを用い、学習率 2e-5、線形スケジューリング、warmup 6000 steps、バッチサイズ 124 で学習した。
- 150k iterations の学習後、500 件のクエリからなる検証セットでの MRR@10 を用いてベストチェックポイントを保持し、[11] と同様の近似検索の検証セットを使用した。
- SPLADE-doc アプローチについては、単に 50k steps だけ学習し、最後のチェックポイントを採用した。
- 入力系列の最大長は 256 とした。
- 学習の初期段階における正則化項の影響を緩和するため、[22] に従い $\lambda$ に対するスケジューラを用い、各学習 iteration ごとに $\lambda$ を 2 次関数的に増加させ、所定の step（我々の場合は 50k）以降は一定値に保つ。
- $\lambda$ の典型的な値は 1e-1 から 1e-4 の間である。
- インデックスの保存には Python 配列に基づく独自実装を用い、検索の並列化には Numba [15] を利用した。
- Models3 は PyTorch [23] と HuggingFace transformers [28] を用いて、メモリ 32GB の 4 基の Tesla V100 GPU 上で学習した。

- **評価.**
- 両データセットについて Recall@1000 を、また MS MARCO dev set および TREC DL 2019 についてはそれぞれ公式メトリクスである MRR@10 と NDCG@10 を報告する。
- 我々は本質的に first retrieval step に関心があるため、BERT に基づく re-rankers は対象とせず、first stage rankers のみと比較する。
- したがって MS MARCO leaderboard で報告されている結果は、ここで提示する結果とは比較できない。
- 比較対象とする sparse なアプローチは以下の通りである：(1) BM25、(2) DeepCT [4]、(3) doc2query-T5 [20]、(4) SparTerm [1]、(5) COIL-tok [9]、(6) DeepImpact [18]。
- さらに、対応する論文から結果を引用する形で、最先端の dense なアプローチである ANCE [29]、TCT-ColBERT [16]、TAS-B [11] とも比較する。

- MS MARCO dev および TREC DL 2019 の結果を表1に示す。
- SPLADE の性能は正則化強度 $\lambda$ に依存し、また、より効率的なモデルは一般に効果が低いため、表では実験のグリッドの中から、合理的な効率（FLOPS の観点で）を持ちつつ最も高性能なモデルを選択している。
- 図1は、異なる正則化強度で学習された SPLADE モデルの性能（MS MARCO dev set 上の MRR@10）と FLOPS の関係を示すことで、SPLADE における effectiveness と efficiency の実際のトレードオフを浮き彫りにしている。
- FLOPS メトリクスは、クエリと文書の間の浮動小数点演算の平均回数を見積もったものであり、期待値 Ba,d Ejevp, 9p として定義される（ここで pj は文書 d またはクエリ q におけるトークン j の活性化確率である）。
- これは MS MARCO コレクション上の約 100k 件の development クエリ集合から経験的に推定される。
- 全体として、以下を観察する：(1) 我々の改良されたモデルは、

1cross-encoder のチェックポイントとして https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-12-v2 を用いた事前学習済みチェックポイントを使用。

2https://github.com/microsoft/MSMARCO-Passage-Ranking

3コードは https://github.com/naver/splade で公開している。

<table>
<caption>表1: MS MARCO passage retrieval (dev set) と TREC DL 2019 における評価。</caption>
<tr>
<th>model</th>
<th colspan="2">MS MARCO dev MRR@10 R@1000</th>
<th colspan="2">NDCG@10 R@1000 TREC DL 2019</th>
</tr>
<tr>
<td>Dense retrieval</td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>Siamese (ours)</td>
<td>0.312</td>
<td>0.941</td>
<td>0.637</td>
<td>0.711</td>
</tr>
<tr>
<td>ANCE [29]</td>
<td>0.330</td>
<td>0.959</td>
<td>0.648</td>
<td>-</td>
</tr>
<tr>
<td>TCT-ColBERT [16]</td>
<td>0.359</td>
<td>0.970</td>
<td>0.719</td>
<td>0.760</td>
</tr>
<tr>
<td>TAS-B [11]</td>
<td>0.347</td>
<td>0.978</td>
<td>0.717</td>
<td>0.843</td>
</tr>
<tr>
<td>RocketQA [24]</td>
<td>0.370</td>
<td>0.979</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>Sparse retrieval</td>
<td></td>
<td></td>
<td colspan="2"></td>
</tr>
<tr>
<td>BM25</td>
<td>0.184</td>
<td>0.853</td>
<td>0.506</td>
<td>0.745</td>
</tr>
<tr>
<td>DeepCT [4]</td>
<td>0.243</td>
<td>0.913</td>
<td>0.551</td>
<td>0.756</td>
</tr>
<tr>
<td>doc2query-T5 [20]</td>
<td>0.277</td>
<td>0.947</td>
<td>0.642</td>
<td>0.827</td>
</tr>
<tr>
<td>SparTerm [1]</td>
<td>0.279</td>
<td>0.925</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>COIL-tok [9]</td>
<td>0.341</td>
<td>0.949</td>
<td>0.660</td>
<td>-</td>
</tr>
<tr>
<td>DeepImpact [18]</td>
<td>0.326</td>
<td>0.948</td>
<td>0.695</td>
<td>-</td>
</tr>
<tr>
<td>SPLADE [8]</td>
<td>0.322</td>
<td>0.955</td>
<td>0.665</td>
<td>0.813</td>
</tr>
<tr>
<td>Our methods</td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>SPLADE-max</td>
<td>0.340</td>
<td>0.965</td>
<td>0.684</td>
<td>0.851</td>
</tr>
<tr>
<td>SPLADE-doc</td>
<td>0.322</td>
<td>0.946</td>
<td>0.667</td>
<td>0.747</td>
</tr>
<tr>
<td>DistilSPLADE-max</td>
<td>0.368</td>
<td>0.979</td>
<td>0.729</td>
<td>0.865</td>
</tr>
</table>

- MS MARCO dev set および TREC DL 2019 のクエリの双方において、他の sparse retrieval 手法を大きな差で上回っている。
- (2) その結果は最先端の dense retrieval 手法と比肩しうる水準である。

- BEIR. 最後に、ゼロショット評価のための多様な IR データセットを包括する BEIR [26] ベンチマークのデータセットのサブセットを用いて、SPLADE のゼロショット性能を検証する。
- サブセットのみを用いるのは、データセットの一部（具体的には CQADupstack、BioASQ、Signal-1M、TREC-NEWS、Robust04）が容易に入手できないためである。
- 結果は表2に示す（NDCG@10）。
- 比較対象は、元のベンチマーク論文 [26] の中で最も高性能だったモデル（ColBERT [14]）と、ローリングベンチマーク4 において最も高性能であった上位 2 つのモデル（tuned BM25 と TAS-B [11]）とする。
- これらのベースラインに対する SPLADE の評価結果も併せて報告する。

### 4.1 max プーリングの影響

- まず、MS MARCO および TREC において、max プーリングは SPLADE のベースラインと比較して MRR@10 と NDCG@10 でほぼ 2 ポイントの改善をもたらす。
- これにより COIL や DeepImpact と競合する性能となる。
- さらに、図1 が示すように、SPLADE-max は有効性と効率性のトレードオフの観点で SPLADE よりも一貫して優れている。
- SPLADE-max は BEIR ベンチマークにおいても性能を改善している (表2 参照)。

### 4.2 文書拡張

- max プーリングを用いた我々の文書エンコーダモデルは、従来の SPLADE モデルと同等の性能に到達でき、MS MARCO 上で doc2query-T5 を上回る。
- このモデルはクエリエンコーダを持たないため、レイテンシなどの観点でより効率的である。
- 図2 は、効率性 (文書表現の平均サイズの観点) と有効性のバランスをどのように取れるかを示している。
- 比較的疎な表現の場合でも、doc2query-T5 のような手法と同等の性能を得ることができる (例えば、文書あたり平均 19 個の非ゼロ重みを持つモデルで MRR@10=29.6)。
- さらに、新しい文書コレクションへの学習と適用が容易である: doc2query-T5 ではビームサーチによる複数回の推論が必要であるのに対し、本手法では 1 回のフォワードパスで済む。

### 4.3 蒸留

- 蒸留を用いた学習により、表1 に示すように SPLADE の性能を大幅に向上させることができる。
- 図1 から、蒸留したモデルは FLOPS の高い領域で大きな改善をもたらす一方で

avg. document length (# of non-zero entries)

4https://docs.google.com/spreadsheets/d/1L8aACyPaXrL8iEelJLGqlMqXKPX2oSP_
R10pZoy77Ns

<table>
<caption>表2: BEIR (すぐに利用可能なすべてのデータセットを含むサブセット) における NDCG@10 の結果。</caption>
<tr>
<th rowspan="2">Corpus</th>
<th colspan="3">Baselines</th>
<th colspan="3">SPLADE</th>
</tr>
<tr>
<th>ColBERT</th>
<th>BM25</th>
<th>TAS-B</th>
<th>sum [8]</th>
<th>max</th>
<th>distil</th>
</tr>
<tr>
<td>MS MARCO</td>
<td>0.425</td>
<td>0.228</td>
<td>0.408</td>
<td>0.387</td>
<td>0.402</td>
<td>0.433</td>
</tr>
<tr>
<td>ArguAna</td>
<td>0.233</td>
<td>0.315</td>
<td>0.427</td>
<td>0.447</td>
<td>0.439</td>
<td>0.479</td>
</tr>
<tr>
<td>Climate-FEVER</td>
<td>0.184</td>
<td>0.213</td>
<td>0.228</td>
<td>0.162</td>
<td>0.199</td>
<td>0.235</td>
</tr>
<tr>
<td>DBPedia</td>
<td>0.392</td>
<td>0.273</td>
<td>0.384</td>
<td>0.343</td>
<td>0.366</td>
<td>0.435</td>
</tr>
<tr>
<td>FEVER</td>
<td>0.771</td>
<td>0.753</td>
<td>0.700</td>
<td>0.728</td>
<td>0.730</td>
<td>0.786</td>
</tr>
<tr>
<td>FiQA-2018</td>
<td>0.317</td>
<td>0.236</td>
<td>0.300</td>
<td>0.258</td>
<td>0.287</td>
<td>0.336</td>
</tr>
<tr>
<td>HotpotQA</td>
<td>0.593</td>
<td>0.603</td>
<td>0.584</td>
<td>0.635</td>
<td>0.636</td>
<td>0.684</td>
</tr>
<tr>
<td>NFCorpus</td>
<td>0.305</td>
<td>0.325</td>
<td>0.319</td>
<td>0.311</td>
<td>0.313</td>
<td>0.334</td>
</tr>
<tr>
<td>NQ</td>
<td>0.524</td>
<td>0.329</td>
<td>0.463</td>
<td>0.438</td>
<td>0.469</td>
<td>0.521</td>
</tr>
<tr>
<td>Quora</td>
<td>0.854</td>
<td>0.789</td>
<td>0.835</td>
<td>0.829</td>
<td>0.835</td>
<td>0.838</td>
</tr>
<tr>
<td>SCIDOCS</td>
<td>0.145</td>
<td>0.158</td>
<td>0.149</td>
<td>0.141</td>
<td>0.145</td>
<td>0.158</td>
</tr>
<tr>
<td>SciFact</td>
<td>0.671</td>
<td>0.665</td>
<td>0.643</td>
<td>0.626</td>
<td>0.628</td>
<td>0.693</td>
</tr>
<tr>
<td>TREC-COVID</td>
<td>0.677</td>
<td>0.656</td>
<td>0.481</td>
<td>0.655</td>
<td>0.673</td>
<td>0.710</td>
</tr>
<tr>
<td>Touché-2020 (v1)</td>
<td>0.275</td>
<td>0.614</td>
<td>0.173</td>
<td>0.289</td>
<td>0.316</td>
<td>0.364</td>
</tr>
<tr>
<td>Avg. all</td>
<td>0.455</td>
<td>0.440</td>
<td>0.435</td>
<td>0.446</td>
<td>0.460</td>
<td>0.500</td>
</tr>
<tr>
<td>Avg. zero-shot</td>
<td>0.457</td>
<td>0.456</td>
<td>0.437</td>
<td>0.451</td>
<td>0.464</td>
<td>0.506</td>
</tr>
<tr>
<td>Best on dataset</td>
<td>2</td>
<td>2</td>
<td>0</td>
<td>0</td>
<td>0</td>
<td>11</td>
</tr>
</table>

- の値において (FLOPS が約 4 で MRR@10 が 0.368)、低 FLOPS 領域でも依然として非常に効率的である (FLOPS が約 0.3 で MRR が 0.35) ことが分かる。
- さらに、DistilSPLADE-max は BEIR ベンチマークのほとんどのデータセットにおいて他のすべての手法を上回ることができる (表2 参照)。

## 5 結論

- 本論文では、SPLADE モデルのプーリング機構を再考し、ニューラル IR モデルにおける蒸留などの標準的な訓練手法を活用することで、SPLADE をさらに発展させた。
- 実験により、max プーリング手法が実際に大幅な改善をもたらすことが示された。
- 次に、document encoder はより高速な検索条件下において興味深いモデルである。
- 最後に、蒸留された SPLADE モデルは MS MARCO および TREC DL 2019 において最先端のモデルに迫る性能を達成し、ゼロショット評価では最近の dense モデルを明確に上回る結果を示した。

## 参考文献

[1] Yang Bai, Xiaoguang Li, Gang Wang, Chaoliang Zhang, Lifeng Shang, Jun Xu,
Zhaowei Wang, Fangshan Wang, and Qun Liu. 2020. SparTerm: Learning Term-
based Sparse Representation for Fast Text Retrieval. arXiv:2010.00768 [cs.IR]

[2] Leonid Boytsov. 2018. Efficient and Accurate Non-Metric k-NN Search with Appli-
cations to Text Matching. Ph.D. Dissertation. Carnegie Mellon University.

[3] Nick Craswell, Bhaskar Mitra, Emine Yilmaz, Daniel Campos, and Ellen M
Voorhees. 2020. Overview of the trec 2019 deep learning track. arXiv preprint
arXiv:2003.07820 (2020).

[4] Zhuyun Dai and Jamie Callan. 2019. Context-Aware Sentence/Passage Term
Importance Estimation For First Stage Retrieval. arXiv:1910.10687 [cs.IR]

[5] Zhuyun Dai and Jamie Callan. 2020. Context-Aware Document Term Weighting
for Ad-Hoc Search. Association for Computing Machinery, New York, NY, USA,
1897-1907. https://doi.org/10.1145/3366423.3380258

[6] Zhuyun Dai and Jamie Callan. 2020. Context-Aware Term Weighting For First
Stage Passage Retrieval. Association for Computing Machinery, New York, NY,
USA, 1533-1536. https://doi.org/10.1145/3397271.3401204

[7] Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. 2018. BERT:
Pre-training of Deep Bidirectional Transformers for Language Understanding.
CoRR abs/1810.04805 (2018). arXiv:1810.04805 http://arxiv.org/abs/1810.04805

[8] Thibault Formal, Benjamin Piwowarski, and Stéphane Clinchant. 2021. SPLADE:
Sparse Lexical and Expansion Model for First Stage Ranking. In Proceedings
of the 44th International ACM SIGIR Conference on Research and Development
in Information Retrieval (Virtual Event, Canada) (SIGIR '21). Association for
Computing Machinery, New York, NY, USA, 2288-2292. https://doi.org/10.1145/
3404835.3463098

[9] Luyu Gao, Zhuyun Dai, and Jamie Callan. 2021. COIL: Revisit Exact Lexical Match
in Information Retrieval with Contextualized Inverted List. In Proceedings of the
2021 Conference of the North American Chapter of the Association for Computa-
tional Linguistics: Human Language Technologies. Association for Computational
Linguistics, Online, 3030-3042. https://doi.org/10.18653/v1/2021.naacl-main.241

[10] Kelvin Guu, Kenton Lee, Zora Tung, Panupong Pasupat, and Ming-Wei
Chang. 2020. REALM: Retrieval-Augmented Language Model Pre-Training.
arXiv:2002.08909 [cs.CL]

[11]
Sebastian Hofstätter, Sheng-Chieh Lin, Jheng-Hong Yang, Jimmy Lin, and Allan
Hanbury. 2021. Efficiently Teaching an Effective Dense Retriever with Balanced
Topic Aware Sampling. In Proc. of SIGIR.

[12] Sebastian Hofstätter, Sophia Althammer, Michael Schröder, Mete Sertkan, and
Allan Hanbury. 2020. Improving Efficient Neural Ranking Models with Cross-
Architecture Knowledge Distillation. arXiv:2010.02666 [cs.IR]

[13] Vladimir Karpukhin, Barlas Oğuz, Sewon Min, Patrick Lewis, Ledell Wu, Sergey
Edunov, Danqi Chen, and Wen tau Yih. 2020. Dense Passage Retrieval for Open-
Domain Question Answering. arXiv:2004.04906 [cs.CL]

[14] Omar Khattab and Matei Zaharia. 2020. ColBERT: Efficient and Effective Passage
Search via Contextualized Late Interaction over BERT. In Proceedings of the 43rd
International ACM SIGIR Conference on Research and Development in Information
Retrieval (Virtual Event, China) (SIGIR '20). Association for Computing Machinery,
New York, NY, USA, 39-48. https://doi.org/10.1145/3397271.3401075

5] Siu Kwan Lam, Antoine Pitrou, and Stanley Seibert. 2015. Numba: A llvm-based
python jit compiler. In Proceedings of the Second Workshop on the LLVM Compiler
Infrastructure in HPC. 1-6.

[16] Sheng-Chieh Lin, Jheng-Hong Yang, and Jimmy Lin. 2021. In-Batch Negatives
for Knowledge Distillation with Tightly-Coupled Teachers for Dense Retrieval.
In Proceedings of the 6th Workshop on Representation Learning for NLP (RepL4NLP-
2021). Association for Computational Linguistics, Online, 163-173. https://doi.
org/10.18653/v1/2021.repl4nlp-1.17

[17] Sean MacAvaney, Franco Maria Nardini, Raffaele Perego, Nicola Tonellotto, Nazli
Goharian, and Ophir Frieder. 2020. Expansion via Prediction of Importance with
Contextualization. Proceedings of the 43rd International ACM SIGIR Conference on
Research and Development in Information Retrieval (Jul 2020). https://doi.org/10.
1145/3397271.3401262

18] Antonio Mallia, Omar Khattab, Torsten Suel, and Nicola Tonellotto. 2021. Learn-
ing Passage Impacts for Inverted Indexes. In Proceedings of the 44th International
ACM SIGIR Conference on Research and Development in Information Retrieval
(Virtual Event, Canada) (SIGIR '21). Association for Computing Machinery, New
York, NY, USA, 1723-1727. https://doi.org/10.1145/3404835.3463030

[19] Rodrigo Nogueira and Kyunghyun Cho. 2019. Passage Re-ranking with BERT.
arXiv:1901.04085 [cs.IR]

[20] Rodrigo Nogueira and Jimmy Lin. 2019. From doc2query to docTTTTTquery.

[21]
Rodrigo Nogueira, Wei Yang, Jimmy Lin, and Kyunghyun Cho. 2019. Document
Expansion by Query Prediction. arXiv:1904.08375 [cs.IR]

[22] Biswajit Paria, Chih-Kuan Yeh, Ian E. H. Yen, Ning Xu, Pradeep Ravikumar, and
Barnabás Póczos. 2020. Minimizing FLOPs to Learn Efficient Sparse Representa-
tions. arXiv:2004.05665 [cs.LG]

[23]
Adam Paszke, Sam Gross, Francisco Massa, Adam Lerer, James Bradbury, Gregory
Chanan, Trevor Killeen, Zeming Lin, Natalia Gimelshein, Luca Antiga, et al. 2019.
PyTorch: An Imperative Style, High-Performance Deep Learning Library .. In
NeurIPS.

[24]
Yingqi Qu, Yuchen Ding, Jing Liu, Kai Liu, Ruiyang Ren, Wayne Xin Zhao,
Daxiang Dong, Hua Wu, and Haifeng Wang. 2021. RocketQA: An Optimized
Training Approach to Dense Passage Retrieval for Open-Domain Question An-
swering. In Proceedings of the 2021 Conference of the North American Chapter
of the Association for Computational Linguistics: Human Language Technolo-
gies. Association for Computational Linguistics, Online, 5835-5847. https:
//doi.org/10.18653/v1/2021.naacl-main.466

[25] Nils Reimers and Iryna Gurevych. 2019. Sentence-BERT: Sentence Embeddings
using Siamese BERT-Networks. In Proceedings of the 2019 Conference on Em-
pirical Methods in Natural Language Processing. Association for Computational
Linguistics. http://arxiv.org/abs/1908.10084

[26] Nandan Thakur, Nils Reimers, Andreas Rücklé, Abhishek Srivastava, and Iryna
Gurevych. 2021. BEIR: A Heterogenous Benchmark for Zero-shot Evaluation
of Information Retrieval Models. CoRR abs/2104.08663 (2021). arXiv:2104.08663
https://arxiv.org/abs/2104.08663

[27] Zhengkai Tu, Wei Yang, Zihang Fu, Yuqing Xie, Luchen Tan, Kun Xiong, Ming
Li, and Jimmy Lin. 2020. Approximate Nearest Neighbor Search and Lightweight
Dense Vector Reranking in Multi-Stage Retrieval Architectures. In Proceedings of
the 2020 ACM SIGIR on International Conference on Theory of Information Retrieval.
97-100.

[28] Thomas Wolf, Lysandre Debut, Victor Sanh, Julien Chaumond, Clement Delangue,
Anthony Moi, Pierric Cistac, Tim Rault, Rémi Louf, Morgan Funtowicz, Joe
Davison, Sam Shleifer, Patrick von Platen, Clara Ma, Yacine Jernite, Julien Plu,
Canwen Xu, Teven Le Scao, Sylvain Gugger, Mariama Drame, Quentin Lhoest,
and Alexander M. Rush. 2020. HuggingFace's Transformers: State-of-the-art
Natural Language Processing. arXiv:1910.03771 [cs.CL]

[29] Lee Xiong, Chenyan Xiong, Ye Li, Kwok-Fung Tang, Jialin Liu, Paul Bennett,
Junaid Ahmed, and Arnold Overwijk. 2020. Approximate Nearest Neighbor
Negative Contrastive Learning for Dense Text Retrieval. arXiv:2007.00808 [cs.IR]

[30] Lee Xiong, Chenyan Xiong, Ye Li, Kwok-Fung Tang, Jialin Liu, Paul N. Bennett,
Junaid Ahmed, and Arnold Overwikj. 2021. Approximate Nearest Neighbor Neg-
ative Contrastive Learning for Dense Text Retrieval. In International Conference
on Learning Representations. https://openreview.net/forum?id=zeFrfgyZln

[31] Wei Yang, Kuang Lu, Peilin Yang, and Jimmy Lin. 2019. Critically Examining the
"Neural Hype". Proceedings of the 42nd International ACM SIGIR Conference on
Research and Development in Information Retrieval (Jul 2019). https://doi.org/10.
1145/3331184.3331340

[32] Hamed Zamani, Mostafa Dehghani, W. Bruce Croft, Erik Learned-Miller, and
Jaap Kamps. 2018. From Neural Re-Ranking to Neural Ranking: Learning a
Sparse Representation for Inverted Indexing. In Proceedings of the 27th ACM
International Conference on Information and Knowledge Management (Torino,
Italy) (CIKM '18). Association for Computing Machinery, New York, NY, USA,
497-506. https://doi.org/10.1145/3269206.3271800

[33] Tiancheng Zhao, Xiaopeng Lu, and Kyusong Lee. 2020. SPARTA: Efficient
Open-Domain Question Answering via Sparse Transformer Matching Retrieval.
