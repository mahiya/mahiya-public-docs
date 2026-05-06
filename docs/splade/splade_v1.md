# SPLADE: Sparse Lexical and Expansion Model for First Stage Ranking

<table>
<tr>
<th>Thibault Formal</th>
<th>Benjamin Piwowarski</th>
<th>Stéphane Clinchant</th>
</tr>
<tr>
<td>Naver Labs Europe</td>
<td>Sorbonne Université, CNRS, LIP6</td>
<td>Naver Labs Europe</td>
</tr>
<tr>
<td>Meylan, France</td>
<td>Paris, France</td>
<td>Meylan, France</td>
</tr>
<tr>
<td>Sorbonne Université, LIP6 Paris, France</td>
<td>benjamin.piwowarski@lip6.fr</td>
<td>stephane.clinchant@naverlabs.com</td>
</tr>
</table>

thibault.formal@naverlabs.com

## 概要

- ニューラル情報検索の分野では、ランキングパイプラインにおける第一段階のリトリーバの改善に向けた研究が継続的に行われている。
- 効率的な近似最近傍探索手法を用いた検索を行うために、密なエンベディングを学習する手法が有効であることが示されている。
- 一方で、文書とクエリに対する疎な表現の学習にも関心が高まっており、これは bag-of-words モデルが持つ望ましい特性、すなわち単語の厳密マッチングや転置インデックスによる効率性を継承できる可能性がある。
- 本研究では、明示的な疎性正則化と単語重みに対する対数飽和効果に基づく新しい第一段階ランカーを提案する。
- これにより、高度に疎な表現を実現し、最先端の密および疎な手法と競合する結果を達成する。
- 提案手法はシンプルで、単一段階のエンドツーエンド学習が可能である。
- さらに、疎性正則化の寄与を制御することで、有効性と効率性のトレードオフについても検討する。

## キーワード

neural networks, indexing, sparse representations, regularization

ACM Reference Format:

Thibault Formal, Benjamin Piwowarski, and Stéphane Clinchant. 2021.
SPLADE: Sparse Lexical and Expansion Model for First Stage Ranking.
In Proceedings of ACM Conference (Conference'17). ACM, New York, NY,
USA, 5 pages. https://doi.org/10.1145/nnnnnnn.nnnnnnn

## 1 はじめに

- BERT [7] のような大規模事前学習済み言語モデルの登場は、自然言語処理と情報検索の分野に大きな変革をもたらした。
- これらのモデルは、シンプルなファインチューニングによって様々なタスクに適応する強力な能力を示している。
- 2019年の初頭に、Nogueira と Cho [17] は MS MARCO passage re-ranking タスクにおいて、大幅な差をつけて当時の最高性能を達成し、LM ベースのニューラルランキングモデルへの道を切り開いた。
- 厳しい効率要件のため、これらのモデルは当初、二段階ランキングパイプラインにおける re-ranker として使用されており、第一段階の検索 (候補生成) は転置インデックスに依存する bag-of-words モデル (例えば BM25) で行われていた。
- BOW モデルは依然として強力なベースラインであり続けている [27] が、長年にわたる語彙ミスマッチ問題、つまり関連文書がクエリに現れる用語を含まない可能性があるという問題を抱えている。
- そのため、標準的な BOW アプローチを学習された (ニューラル) ランカーに置き換える試みが行われてきた。
- このようなモデルを設計する際には、効率性とスケーラビリティに関するいくつかの課題がある。
- したがって、計算の大部分をオフラインで行い、オンライン推論を高速化できる手法が必要である。
- 近似最近傍探索を用いた dense retrieval は印象的な結果を示している [8, 15, 26] が、用語マッチングを明示的にモデル化できないため、依然として BOW モデルと組み合わせて使用されている。
- そのため、最近ではクエリと文書のスパース表現を学習することへの関心が高まっている [1, 4, 19, 28, 29]。
- これにより、モデルは BOW モデルの望ましい特性、すなわち (潜在的な可能性のある) 用語の完全一致、転置インデックスの効率性、解釈可能性などを継承することができる。
- さらに、暗黙的または明示的 (潜在的、文脈化された) な拡張メカニズム — IR における標準的な拡張モデルと同様に — をモデル化することで、これらのモデルは語彙ミスマッチを軽減することができる。

- 本論文の貢献は次の3点である。
- (1) SparTerm [1] を基盤として、ハイパーパラメータの軽微な調整によって、元の論文で報告された結果を大幅に上回る改善が得られることを示す。
- (2) 対数活性化とスパース正則化に基づく、SParse Lexical AnD Expansion (SPLADE) モデルを提案する。
- SPLADE は効率的な文書拡張 [1, 16] を実行し、ANCE [26] のような dense モデル向けの複雑な学習パイプラインに対しても競争力のある結果を達成する。
- (3) 最後に、効率性 (浮動小数点演算回数の観点から) と有効性のトレードオフに影響を与えるために、スパース性正則化をどのように制御できるかを示す。

## 2 関連研究

- BERT Siamese モデル [22] に基づく密 (dense) 検索は、質問応答および情報検索 (IR) における候補生成の標準的なアプローチとなっている [8, 10, 12, 15, 25]。
- これらのモデルのバックボーンは同一のままだが、近年の研究では、最先端の結果を得るための学習戦略の重要な側面が強調されており、改良された負例サンプリング [8, 25] から蒸留 [11, 15] に至るまで多岐にわたる。
- ColBERT [13] はこれをさらに推し進めており、トークンレベルの相互作用を後段に遅延させることで、第一段階の検索にモデルを効率的に適用できるようにし、細粒度の相互作用をモデル化する有効性を享受しつつも、(サブ)単語ごとに埋め込みを保存するというコストを伴う ― これは、大規模コレクションに対するこのアプローチの実際のスケーラビリティに関する懸念を引き起こしている。
- 我々の知る限り、近似最近傍 (ANN) 探索を IR 指標に対して用いた場合の影響について議論した研究はごくわずかである [2, 23]。

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

- MS MARCO コレクションのサイズが中程度であるため、結果は通常、厳密な総当たり探索によって報告されており、そのため実際の計算コストに関する示唆が得られない。

- 密インデックスに対する代替手段として、語彙ベース (term-based) のインデックスがある。
- 標準的な BOW モデルを基盤として、Zamani らは初めて SNRM [28] を提案した。
- このモデルは、表現に対する $\ell_1$ 正則化により、文書とクエリを疎な高次元の潜在空間に埋め込む。
- しかし、SNRM の有効性は限定的なままであり、その効率性についても疑問が呈されている [20]。
- より最近では、事前学習済み言語モデル (LM) からの知識を疎なアプローチに転移させようとする試みがなされている。
- BERT に基づく DeepCT [4-6] は、語彙空間全体において文脈化された単語重みを学習することに焦点を当てており ― これは BOW の単語重みと類似している。
- しかし、文書に関連付けられた語彙は同じままであるため、この種のアプローチは語彙ミスマッチの問題を解決しない。
- これは、検索のためにクエリ拡張を用いている [4] ことからも認められている。
- この問題に対する第一の解決策は、doc2query [19] や docTTTTTquery [18] のような生成的アプローチを用いて文書を拡張し、文書に対する拡張語を予測することからなる。
- 文書拡張は文書に新しい単語を追加し ― それによって語彙ミスマッチに対抗する ― ともに既存の単語を繰り返すことで、暗黙的に重要な単語をブーストして再重み付けを行う。
- しかしこれらの手法は、その学習方法 (クエリの予測) によって制限されており、本質的に間接的であり、その進展を制限している。
- この問題に対する第二の解決策は、[1, 16, 29] のような最近の研究で選ばれているが、文書の各単語によって暗黙的に示される語彙の各単語の重要度を推定すること、すなわち、文書またはクエリのトークンと語彙のすべてのトークンとの間の相互作用行列を計算することである。
- これに、集約機構が続き (SparTerm [1] では概ね sum、EPIC [16] と SPARTA [29] では max)、これにより文書全体またはクエリ全体に対して語彙の各単語の重要度重みを計算することが可能となる。
- しかし、EPIC および SPARTA の (文書) 表現は、構造上、十分に疎ではない ― top-k プーリングに頼らない限り ― これは SparTerm とは対照的であり、SparTerm では高速な検索が可能である。
- さらに、後者は (SNRM のように) 明示的な疎性正則化を含んでおらず、これがその性能を阻害している。
- 我々の SPLADE モデルは、このような正則化と他の重要な変更に基づいており、この種のモデルの効率性と有効性の両方を向上させている。

## 3 一次ランキングのためのスパース語彙表現

- 本節では、まず SparTerm モデル [1] について詳細に説明し、その後で我々が提案する SPLADE モデルを紹介する。

### 3.1 SparTerm

- SparTerm は、Masked Language Model (MLM) 層のロジットに基づいて、BERT WordPiece 語彙 ( $|V| = 30522$ ) における項の重要度を予測する。
- より厳密には、入力クエリまたは文書の系列 (WordPiece トークナイズ後) を $t = (t_1, t_2, \ldots, t_N)$ とし、それに対応する BERT 埋め込みを $(h_1, h_2, \ldots, h_N)$ とする。
- 入力系列のトークン $i$ に対する、トークン $j$ (語彙) の重要度 $w_{ij}$ を以下のように考える:

$$
w_{ij} = \mathrm{transform}(h_i)^\top E_j + b_j, \quad j \in \{1, \ldots, |V|\} \tag{1}
$$

- ここで $E_j$ はトークン $j$ に対する BERT 入力埋め込み、 $b_j$ はトークンレベルのバイアス、 $\mathrm{transform}(\cdot)$ は GeLU 活性化と LayerNorm を伴う線形層である。
- 式 1 は MLM 予測と等価であるため、事前学習済みの MLM モデルから初期化することも可能である。
- 最終的な表現は、項の重みの非負性を保証するために ReLU を適用した後、入力系列のトークンに対して重要度予測子を総和することで得られる:

$$
w_j = g_j \sum_{i \in t} \mathrm{ReLU}(w_{ij}) \tag{2}
$$

- ここで $g_j$ は後述するバイナリマスク (ゲーティング) である。
- 上記の式は、語彙の各トークンに対してモデルが新たな重み $w_j$ を予測することから、[1, 16] でも観察されているように、一種のクエリ/文書拡張とみなすことができる。
- SparTerm [1] は、クエリと文書の表現において大量の次元をオフにする 2 つのスパース化方式を導入し、転置インデックスからの効率的な検索を可能にする:

- lexical-only は BOW マスキングであり、すなわちトークン $j$ が $t$ に出現する場合 $g_j = 1$ 、それ以外の場合は $0$ となる;

- expansion-aware は語彙/拡張を考慮したバイナリゲーティング機構であり、 $g_j$ は学習される。
- 元の入力を保持するため、トークン $j$ が $t$ に出現する場合は強制的に $1$ とされる。

- $s(q, d)$ を、式 (2) の $q$ と $d$ の表現の内積によって得られるランキングスコアとする。
- クエリ $q_i$ 、正例文書 $d_i^+$ 、負例文書 $d_i^-$ が与えられたとき、SparTerm は以下の損失を最小化することで学習される:

$$
\mathcal{L}_{\text{rank}} = -\log \frac{e^{s(q_i, d_i^+)}}{e^{s(q_i, d_i^+)} + e^{s(q_i, d_i^-)}} \tag{3}
$$

- **制約事項.**
- SparTerm の expansion-aware ゲーティングはやや複雑であり、モデルをエンドツーエンドで学習することができない: ゲーティング機構は事前に学習され、 $\mathcal{L}_{\text{rank}}$ によるマッチングモデルのファインチューニング中は固定されるため、モデルがランキングタスクに最適なスパース化戦略を学習することを妨げている。
- さらに、lexical 戦略と expansion-aware 戦略はほぼ同等の性能を示しており、拡張の実際の利点に疑問が残る。

### 3.2 SPLADE: SParse Lexical AnD Expansion model

- 以下では、SparTerm モデルに対する小さいながらも本質的な変更を提案し、その性能を劇的に改善する。

- **Model.**
- 式 2 の重要度推定に小さな変更を加え、log 飽和効果を導入する。
- これにより一部の項が支配的になるのを防ぎ、表現の自然なスパース性を保証する:

$$
w_j = \sum_{i \in t} \log\left(1 + \mathrm{ReLU}(w_{ij})\right) \tag{4}
$$

- log 飽和を用いることで一部の項が支配的になるのを防ぐ点は直感的に理解できるが (IR における公理的アプローチや $\log(\mathrm{tf})$ モデル [9] との類似性)、それに伴うスパース性は一見すると意外に思えるかもしれない。
- しかし、我々の実験によれば、これによってより良い実験結果が得られ、いかなる正則化も用いずにスパースな解を得ることが可能になる。

- **Ranking loss.**
- バッチ内のクエリ $q_i$ 、正例文書 $d_i^+$ 、(ハード) 負例文書 $d_i^-$ (例えば BM25 サンプリングから得られたもの)、およびバッチ内の負例文書集合 (他のクエリの正例文書) $\{d_{i,j}^-\}_j$ が与えられたとき、[8] のランキング損失を考える。
- これは、文書 $d_i^+$ が文書 $d_i^+$ 、 $d_i^-$ 、 $\{d_{i,j}^-\}$ の中で関連性が高い確率を最大化することと解釈できる:

$$
\mathcal{L}_{\text{rank-IBN}} = -\log \frac{e^{s(q_i, d_i^+)}}{e^{s(q_i, d_i^+)} + e^{s(q_i, d_i^-)} + \sum_j e^{s(q_i, d_{i,j}^-)}} \tag{5}
$$

- in-batch negatives (IBN) サンプリング戦略は、画像検索モデルの学習に広く用いられており、一次ランカーの学習においても効果的であることが示されている [8, 12, 15]。

- **Learning sparse representations.**
- 一次検索のためにスパース表現を学習するというアイデアは、SNRM [28] において $\ell_1$ 正則化を介して提案されたのが始まりである。
- その後、[20] は、表現の $\ell_1$ ノルムを最小化することは最も効率的なインデックスをもたらさないことを指摘した。
- なぜなら、ポスティングリストが均等に分布することを保証するものが何もないからである。
- 語彙の頻度分布が Zipf 的であることから、これは標準的なインデックスにおいてはなおさら当てはまる。
- バランスの取れたインデックスを得るために、Paria ら [20] は FLOPS 正則化項を導入した。
- これは、文書のスコアを計算するために必要な浮動小数点演算の平均回数の滑らかな緩和であり、したがって検索時間に直接関係する。
- これはトークン $j$ の活性化 (すなわち項が非ゼロの重みを持つ) 確率 $p_j$ の連続緩和として $a_j$ を用いて定義され、サイズ $N$ のバッチにおける文書 $d_i$ については $\bar{a}_j = \frac{1}{N} \sum_{i=1}^{N} w_j^{(d_i)}$ によって推定される。
- これは以下の正則化損失を与える

$$
\ell_{\mathrm{FLOPS}} = \sum_{j \in V} \bar{a}_j^2 = \sum_{j \in V} \left( \frac{1}{N} \sum_{i=1}^{N} w_j^{(d_i)} \right)^2
$$

- これは SNRM [28] で用いられている $\ell_1$ 正則化と異なり、 $a_j$ が二乗されていない: したがって $\ell_{\mathrm{FLOPS}}$ を用いることで、平均項重みの高い値を押し下げ、よりバランスの取れたインデックスが生まれる。

- **Overall loss.**
- 我々は、文書とクエリのスパースで拡張を考慮した表現のエンドツーエンド学習のために、両者の長所を組み合わせることを提案する。
- したがって、SparTerm のバイナリゲーティングを廃止し、代わりにランキング損失と正則化損失を同時に最適化することで log 飽和モデル (式 4) を学習する:

$$
\mathcal{L} = \mathcal{L}_{\text{rank-IBN}} + \lambda_q \mathcal{L}_{\text{reg}}^q + \lambda_d \mathcal{L}_{\text{reg}}^d \tag{6}
$$

- ここで $\mathcal{L}_{\text{reg}}$ はスパース正則化 ( $\ell_1$ または $\ell_{\mathrm{FLOPS}}$ ) である。
- クエリと文書に対して 2 つの異なる正則化重み ( $\lambda_d$ と $\lambda_q$ ) を用いており、これにより高速検索のために重要なクエリのスパース性により強い圧力をかけることが可能となっている。

## 4 実験設定と結果

- 我々は、フルランキング設定で MS MARCO passage ranking データセット1 上でモデルを学習・評価した。
- このデータセットには約 8.8M のパッセージと、浅いアノテーション (1 クエリあたり平均 ~1.1 件の関連パッセージ) を持つ数十万件の学習用クエリが含まれる。
- 開発セット (development set) は同様のラベルを持つ 6980 件のクエリから構成される一方、TREC DL 2019 の評価セットは 43 件のクエリに対する人間評価者によるきめ細かいアノテーションを提供する [3]。

- **学習・インデックス化・検索.**
- 我々はモデルを BERT-base のチェックポイントで初期化した。
- モデルは ADAM オプティマイザを用い、学習率 2e-5 で線形スケジューリングと 6000 ステップのウォームアップを行い、バッチサイズ 124 で学習した。
- 150k イテレーションの学習後、500 件のクエリからなる検証セット上での MRR@10 を用いてベストチェックポイントを保持する (なお、検証は再ランキングタスクで行うため、これは最適ではない点に注意)。
- 入力系列の最大長は 256 とした。
- 学習初期段階における正則化項の寄与を緩和するため、[20] に従い、 $\lambda$ のスケジューラを使用する。
- これは各学習イテレーションで $\lambda$ を二次的に増加させ、所定のステップ (本研究では 50k) に到達した時点でその値を一定に保つ。
- $\lambda$ の典型的な値は 1e-1 から 1e-4 の間に収まる。
- インデックスの保存には Python 配列に基づくカスタム実装を使用し、検索の並列化には Numba [14] を利用する。
- モデル2 は PyTorch [21] と HuggingFace transformers [24] を用いて、32GB メモリを搭載した 4 台の Tesla V100 GPU 上で学習されている。

- **評価.**
- 両データセットについて Recall@1000 を、また MS MARCO dev セットおよび TREC DL 2019 についてそれぞれ公式指標である MRR@10 および NDCG@10 を報告する。
- 我々は本質的に第一段階の検索に関心があるため、BERT に基づく再ランカーは考慮せず、第一段階のランカーのみと比較する。
- したがって MS MARCO リーダーボードに掲載された結果は、ここで提示する結果とは比較できない。
- 我々は以下の疎な手法と比較する: (1) BM25 (2) DeepCT [4] (3) doc2query-T5 [18] (4) および SparTerm [1]、加えて最先端の密な手法である ANCE [25] および TCT-ColBERT [15] とも比較する。
- これらは原論文の結果を報告している。
- 我々のランキングパイプラインで学習させた純粋に語彙的な SparTerm (ST lexical-only) も含めている。
- log-saturation の利点を示すため、Eq. (4) ではなく Eq. (2) を用いて学習させたモデルの結果も追加した (ST exp- $\ell_1$ および ST exp- $\ell_{\mathrm{FLOPS}}$ )。
- 疎モデルについては、可能な場合に Table 1 にクエリと文書間の浮動小数点演算の平均回数の推定値を示す。
- これは期待値 $E_{q,d}\left[\sum_{j \in V} p_j^{(q)} p_j^{(d)}\right]$ として定義され、ここで $p_j$ は文書 $d$ またはクエリ $q$ におけるトークン $j$ の活性化確率である。
- これは MS MARCO コレクション上で、約 100k 件の開発クエリの集合から経験的に推定される。

- 結果は表1に示されている。
- 全体として、以下のことが観察される: (1) 我々のモデルは他の疎な検索手法を大きく上回る (ただし TREC DL における recall@1000 を除く); (2) 結果は最先端の密な検索手法と競合する性能を示す。

- より具体的には、我々の ST lexical-only に対する学習方法は、すでに DeepCT の結果と、SparTerm 原論文で報告されている結果 (拡張を用いたモデルを含む) を上回っている。
- 追加の疎な拡張機構のおかげで、我々は MS MARCO dev セット上で最先端の密な手法と同等の結果を得ることができる (例: ST exp- $\ell_1$ で Recall@1000 が 0.96 近く) が、平均 FLOPS の数ははるかに大きい。

- 拡張モデルに log-saturation 効果を加えることで、SPLADE は疎性を大幅に増加させ、FLOPS を BOW 手法と同程度のレベルまで削減すると同時に、最良の第一段階ランカーと比較して性能上のコストを伴わない。
- さらに、

1 https://github.com/microsoft/MSMARCO-Passage-Ranking

2コードは https://github.com/naver/splade で公開している

<table>
<caption>表1: MS MARCO passage retrieval (dev セット) および TREC DL 2019 における評価</caption>
<tr>
<th>model</th>
<th colspan="2">MS MARCO dev MRR@10 R@1000</th>
<th colspan="3">NDCG@10 R@1000 TREC DL 2019 FLOPS</th>
</tr>
<tr>
<td>Dense retrieval</td>
<td></td>
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
<td>-</td>
</tr>
<tr>
<td>ANCE [25]</td>
<td>0.330</td>
<td>0.959</td>
<td>0.648</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>TCT-ColBERT [15]</td>
<td>0.335</td>
<td>0.964</td>
<td>0.670</td>
<td>0.720</td>
<td>-</td>
</tr>
<tr>
<td>Sparse retrieval</td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>BM25</td>
<td>0.184</td>
<td>0.853</td>
<td>0.506</td>
<td>0.745</td>
<td>0.13</td>
</tr>
<tr>
<td>DeepCT [4]</td>
<td>0.243</td>
<td>0.913</td>
<td>0.551</td>
<td>0.756</td>
<td>-</td>
</tr>
<tr>
<td>doc2query-T5 [18]</td>
<td>0.277</td>
<td>0.947</td>
<td>0.642</td>
<td>0.827</td>
<td>0.81</td>
</tr>
<tr>
<td>ST lexical-only [1]</td>
<td>0.275</td>
<td>0.912</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>ST expansion [1]</td>
<td>0.279</td>
<td>0.925</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td>Our methods</td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>ST lexical-only</td>
<td>0.290</td>
<td>0.923</td>
<td>0.595</td>
<td>0.774</td>
<td>1.84</td>
</tr>
<tr>
<td>ST exp-l1</td>
<td>0.314</td>
<td>0.959</td>
<td>0.668</td>
<td>0.800</td>
<td>4.62</td>
</tr>
<tr>
<td>ST exp-{FLOPS</td>
<td>0.312</td>
<td>0.954</td>
<td>0.671</td>
<td>0.813</td>
<td>2.83</td>
</tr>
<tr>
<td>SPLADE-{1</td>
<td>0.322</td>
<td>0.954</td>
<td>0.667</td>
<td>0.792</td>
<td>0.88</td>
</tr>
<tr>
<td>SPLADE-{FLOPS</td>
<td>0.322</td>
<td>0.955</td>
<td>0.665</td>
<td>0.813</td>
<td>0.73</td>
</tr>
</table>

- 計算コストを削減するという観点で、 $\ell_1$ に対する FLOPS 正則化の利点が観察される。
- SparTerm とは対照的に、SPLADE は単一のステップでエンドツーエンドに学習される点に留意されたい。
- また、ANCE [25] のような最先端の密なベースラインと比較して非常にシンプルであり、IR 指標への影響がまだ十分に評価されていない近似近傍探索に頼る必要がない。

- **有効性と効率のトレードオフ.**
- Figure 1 は、 $\lambda_q$ と $\lambda_d$ を変化させた場合の有効性 (MRR@10) と効率 (FLOPS) のトレードオフを示している (両方を変化させているため、プロットは滑らかではない)。
- ST exp- $\ell_{\mathrm{FLOPS}}$ は効率の点で BOW モデルおよび SPLADE に大きく後れを取っていることが観察される。
- 一方で、SPLADE は doc2query-T5 を上回りつつ、疎な BOW モデルと同等の効率レベルに到達している。
- 興味深いことに、強く正則化されたモデルでも依然として競合する性能を示す (例: FLOPS=0.05、MRR@10=0.296)。
- 最後に、 $\ell_1$ と比較した $\ell_{\mathrm{FLOPS}}$ によってもたらされる正則化効果は明確である: 同じ効率レベルにおいて、前者の性能は常に後者よりも低い。

- 表2: 文書および拡張語: 括弧内は語に関連付けられた重みを示す - 文書内で 2 回目以降に出現する語については省略され、ゼロの場合は取り消し線で示される

original document (doc ID: 7131647)

if (1.2) bow (2.56) legs (1.18) is caused (1.29) by (0.47) the bone (1.2) alignment
(1.88) issue (0.87) than you may be able (0.29) to correct (1.37) through (0.43)
bow legs correction (1.05) exercises. read more here .. if bow legs is caused by
the bone alignment issue than you may be able to correct through bow legs
correction exercises.

**expansion terms**

(leg, 1.62) (arrow, 0.7) (exercise, 0.64) (bones, 0.63) (problem, 0.41) (treatment,
0.35) (happen, 0.29) (create, 0.22) (can, 0.14) (worse, 0.14) (effect, 0.08) (teeth,
0.06) (remove, 0.03)

- **拡張の役割.**
- 実験により、拡張は再現率を増加させることで純粋に語彙的な手法に対して改善をもたらすことが示されている。
- さらに、拡張正則化されたモデルから得られる表現はより疎である: モデルは無関係な次元をオフにし、有用な次元を活性化することで、拡張と圧縮のバランスを取る方法を学習する。
- 10k 文書の集合において、表1の SPLADE- $\ell_{\mathrm{FLOPS}}$ は 1 文書あたり平均 20 語をドロップする一方で、32 個の拡張語を追加する。
- 我々の最も効率的なモデルの 1 つ (FLOPS=0.05) では、平均 34 語がドロップされ、新たに追加される拡張語は 5 個のみである。
- この場合、表現は極めて疎となる: 文書とクエリの非ゼロ値はそれぞれ平均 18 個と 6 個であり、ディスク上にインデックスを保存するのに 1.4 GB 未満で済む。
- 表2 は、モデルが重要な語を強調し、情報量のないほとんどの語を破棄することによって、語の重み付け直しを行う例を示している。
- 拡張は、暗黙的にステミング効果を加える (legs -> leg) か、あるいは関連するトピック語 (例: treatment) を追加することで、文書を豊かにすることを可能にする。

## 5 結論

- 近年、BERT に基づく密ベクトル検索は第一段階検索における優位性を示しており、従来のスパースモデルの競争力に疑問が投げかけられている。
- 本研究では、クエリ/文書拡張を再考したスパースモデルである SPLADE を提案した。
- 我々のアプローチは、in-batch ネガティブ、対数活性化、および FLOPS 正則化に基づき、効果的かつ効率的なスパース表現を学習する。
- SPLADE は初期検索の有力な候補である。
- 最新の最先端密ベクトル検索モデルに匹敵し、訓練手順は単純であり、スパース性/FLOPS は正則化を通じて明示的に制御可能であり、転置インデックス上で動作することができる。
- その単純さゆえに、SPLADE はこの研究方向におけるさらなる改善の確固たる基盤となる。

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

[8] Yingqi Qu Yuchen Ding, Jing Liu, Kai Liu, Ruiyang Ren, Xin Zhao, Daxiang
Dong, Hua Wu, and Haifeng Wang. 2020. RocketQA: An Optimized Training
Approach to Dense Passage Retrieval for Open-Domain Question Answering.
arXiv:2010.08191 [cs.CL]

[9] Hui Fang, Tao Tao, and ChengXiang Zhai. 2004. A Formal Study of Information
Retrieval Heuristics. In Proceedings of the 27th Annual International ACM SIGIR
Conference on Research and Development in Information Retrieval (Sheffield, United
Kingdom) (SIGIR '04). Association for Computing Machinery, New York, NY, USA,
49-56. https://doi.org/10.1145/1008992.1009004

[10] Kelvin Guu, Kenton Lee, Zora Tung, Panupong Pasupat, and Ming-Wei
Chang. 2020. REALM: Retrieval-Augmented Language Model Pre-Training.
arXiv:2002.08909 [cs.CL]

[11] Sebastian Hofstätter, Sophia Althammer, Michael Schröder, Mete Sertkan, and
Allan Hanbury. 2020. Improving Efficient Neural Ranking Models with Cross-
Architecture Knowledge Distillation. arXiv:2010.02666 [cs.IR]

[12] Vladimir Karpukhin, Barlas Oğuz, Sewon Min, Patrick Lewis, Ledell Wu, Sergey
Edunov, Danqi Chen, and Wen tau Yih. 2020. Dense Passage Retrieval for Open-
Domain Question Answering. arXiv:2004.04906 [cs.CL]

[13] Omar Khattab and Matei Zaharia. 2020. ColBERT: Efficient and Effective Passage
Search via Contextualized Late Interaction over BERT. In Proceedings of the 43rd
International ACM SIGIR Conference on Research and Development in Information
Retrieval (Virtual Event, China) (SIGIR '20). Association for Computing Machinery,
New York, NY, USA, 39-48. https://doi.org/10.1145/3397271.3401075

[14] Siu Kwan Lam, Antoine Pitrou, and Stanley Seibert. 2015. Numba: A llvm-based
python jit compiler. In Proceedings of the Second Workshop on the LLVM Compiler
Infrastructure in HPC. 1-6.

[15] Sheng-Chieh Lin, Jheng-Hong Yang, and Jimmy Lin. 2020. Distilling Dense Repre-
sentations for Ranking using Tightly-Coupled Teachers. arXiv:2010.11386 [cs.IR]

[16] Sean MacAvaney, Franco Maria Nardini, Raffaele Perego, Nicola Tonellotto, Nazli
Goharian, and Ophir Frieder. 2020. Expansion via Prediction of Importance with

Contextualization. Proceedings of the 43rd International ACM SIGIR Conference on
Research and Development in Information Retrieval (Jul 2020). https://doi.org/10.
1145/3397271.3401262

[17] Rodrigo Nogueira and Kyunghyun Cho. 2019. Passage Re-ranking with BERT.
arXiv:1901.04085 [cs.IR]

[18] Rodrigo Nogueira and Jimmy Lin. 2019. From doc2query to docTTTTTquery.

[19] Rodrigo Nogueira, Wei Yang, Jimmy Lin, and Kyunghyun Cho. 2019. Document
Expansion by Query Prediction. arXiv:1904.08375 [cs.IR]

[20] Biswajit Paria, Chih-Kuan Yeh, Ian E. H. Yen, Ning Xu, Pradeep Ravikumar, and
Barnabás Póczos. 2020. Minimizing FLOPs to Learn Efficient Sparse Representa-
tions. arXiv:2004.05665 [cs.LG]

[21] Adam Paszke, Sam Gross, Francisco Massa, Adam Lerer, James Bradbury, Gregory
Chanan, Trevor Killeen, Zeming Lin, Natalia Gimelshein, Luca Antiga, et al. 2019.
PyTorch: An Imperative Style, High-Performance Deep Learning Library .. In
NeurIPS.

[22] Nils Reimers and Iryna Gurevych. 2019. Sentence-BERT: Sentence Embeddings
using Siamese BERT-Networks. In Proceedings of the 2019 Conference on Em-
pirical Methods in Natural Language Processing. Association for Computational
Linguistics. http://arxiv.org/abs/1908.10084

[23] Zhengkai Tu, Wei Yang, Zihang Fu, Yuqing Xie, Luchen Tan, Kun Xiong, Ming
Li, and Jimmy Lin. 2020. Approximate Nearest Neighbor Search and Lightweight
Dense Vector Reranking in Multi-Stage Retrieval Architectures. In Proceedings of
the 2020 ACM SIGIR on International Conference on Theory of Information Retrieval.
97-100.

[24] Thomas Wolf, Lysandre Debut, Victor Sanh, Julien Chaumond, Clement Delangue,
Anthony Moi, Pierric Cistac, Tim Rault, Rémi Louf, Morgan Funtowicz, Joe
Davison, Sam Shleifer, Patrick von Platen, Clara Ma, Yacine Jernite, Julien Plu,
Canwen Xu, Teven Le Scao, Sylvain Gugger, Mariama Drame, Quentin Lhoest,
and Alexander M. Rush. 2020. HuggingFace's Transformers: State-of-the-art
Natural Language Processing. arXiv:1910.03771 [cs.CL]

[25] Lee Xiong, Chenyan Xiong, Ye Li, Kwok-Fung Tang, Jialin Liu, Paul Bennett,
Junaid Ahmed, and Arnold Overwijk. 2020. Approximate Nearest Neighbor
Negative Contrastive Learning for Dense Text Retrieval. arXiv:2007.00808 [cs.IR]

[26] Lee Xiong, Chenyan Xiong, Ye Li, Kwok-Fung Tang, Jialin Liu, Paul N. Bennett,
Junaid Ahmed, and Arnold Overwikj. 2021. Approximate Nearest Neighbor Neg-
ative Contrastive Learning for Dense Text Retrieval. In International Conference
on Learning Representations. https://openreview.net/forum?id=zeFrfgyZln

[27]
Wei Yang, Kuang Lu, Peilin Yang, and Jimmy Lin. 2019. Critically Examining the
"Neural Hype". Proceedings of the 42nd International ACM SIGIR Conference on
Research and Development in Information Retrieval (Jul 2019). https://doi.org/10.
1145/3331184.3331340

[28] Hamed Zamani, Mostafa Dehghani, W. Bruce Croft, Erik Learned-Miller, and
Jaap Kamps. 2018. From Neural Re-Ranking to Neural Ranking: Learning a
Sparse Representation for Inverted Indexing. In Proceedings of the 27th ACM
International Conference on Information and Knowledge Management (Torino,
Italy) (CIKM '18). Association for Computing Machinery, New York, NY, USA,
497-506. https://doi.org/10.1145/3269206.3271800

[29] Tiancheng Zhao, Xiaopeng Lu, and Kyusong Lee. 2020. SPARTA: Efficient
Open-Domain Question Answering via Sparse Transformer Matching Retrieval.
