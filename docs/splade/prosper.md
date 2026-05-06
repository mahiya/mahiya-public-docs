# LLMs as Sparse Retrievers: A Framework for First-Stage Product Search

Hongru Song
Yu-An Liu
State Key Laboratory of AI Safety,
Institute of Computing Technology,
Chinese Academy of Sciences
University of Chinese Academy of
Sciences
Beijing, China

{songhongru24s,liuyuan21b}@ict.ac.cn

Ruqing Zhang
Jiafeng Guo
State Key Laboratory of AI Safety,
Institute of Computing Technology,
Chinese Academy of Sciences
University of Chinese Academy of
Sciences
Beijing, China
{zhangruqing,guojiafeng}@ict.ac.cn

Maarten de Rijke
University of Amsterdam
Amsterdam, The Netherlands
m.derijke@uva.nl

<table>
<tr>
<th>Sen Li</th>
<th>Fuyu Lv</th>
<th>Xueqi Cheng</th>
</tr>
<tr>
<td>Wenjun Peng Researcher</td>
<td>Researcher Hangzhou, China</td>
<td rowspan="2">State Key Laboratory of AI Safety, Institute of Computing Technology, Chinese Academy of Sciences</td>
</tr>
<tr>
<td>Hangzhou, China</td>
<td>fuyu.lfy@alibaba-inc.com</td>
</tr>
<tr>
<td>lisen.lisen@alibaba-inc.com pengwj@mail.ustc.edu.cn</td>
<td></td>
<td>University of Chinese Academy of Sciences Beijing, China</td>
</tr>
</table>

cxq@ict.ac.cn

## アブストラクト

- 商品検索は現代の EC プラットフォームにおける重要な構成要素であり、毎日数十億件ものユーザクエリが発生している。
- 商品検索システムにおいて、第 1 段階の検索は高い再現率を達成しつつ、効率的なオンライン展開を保証する必要がある。
- スパース検索はこの文脈において、その解釈可能性とストレージ効率の観点から特に魅力的である。
- しかし、スパース検索手法は深刻な語彙ミスマッチ問題に悩まされており、商品検索シナリオにおいて最適とは言えない性能となっている。

- 意味解析の潜在能力を持つ大規模言語モデル (LLM) は、語彙ミスマッチ問題を緩和し、ひいては検索品質を向上させる有望な手段を提供する。
- しかしながら、LLM を商品検索におけるスパース検索に直接適用することには、2 つの主要な課題がある。
- (i) クエリと商品タイトルは典型的に短く、無関係な拡張語の生成や、ブランド名・型番のような重要な字面語の重み付け不足といった LLM 由来のハルシネーションの影響を非常に受けやすい。
- (ii) LLM の語彙空間は巨大であり、訓練を効果的に初期化することが困難となるため、このような超高次元空間において意味のあるスパース表現を学習することが難しい。
- これらの課題に対処するため、我々は LLM を SParsE Retriever として活用する PROduct 検索フレームワークである PROSPER を提案する。
- PROSPER は以下を組み込んでいる。
- (i) 残差補償機構を通じて重み付けが不十分な字面語を強化することで、語彙拡張におけるハルシネーションを緩和する literal residual network (字面残差ネットワーク)。
- (ii) 粗から細への (coarse-to-fine) スパース化戦略を介して効果的な訓練初期化を可能にする lexical focusing window (語彙集中ウィンドウ)。
- 広範なオフラインおよびオンライン実験により、PROSPER がスパースベースラインを大幅に上回り、先進的な密ベクトル検索器に匹敵する再現率性能を達成し、同時にオンラインで売上増加も達成することが示された。

## CCS分類

## · Information systems -> Retrieval models and ranking.

### キーワード

スパース検索、大規模言語モデル、商品検索

### ACM参考フォーマット:

Hongru Song, Yu-An Liu, Ruqing Zhang, Jiafeng Guo, Maarten de Rijke,
Sen Li, Wenjun Peng, Fuyu Lv, and Xueqi Cheng. 2018. LLMs as Sparse
Retrievers: A Framework for First-Stage Product Search. In Proceedings of
Make sure to enter the correct conference title from your rights confirmation
email (Conference acronym 'XX). ACM, New York, NY, USA, 16 pages. https:
//doi.org/XXXXXXXXXXXXXX

## 1 はじめに

- Eコマースプラットフォームは、日常生活に欠かせない存在となっている。
- 多くのオンライン消費者にとって、商品検索エンジンは入口であると同時に、膨大な商品群と利用者を結びつける中心的なハブとしての役割を果たしている。
- 最大の課題は、数億人規模のユーザーから寄せられる検索クエリを、十億規模の商品カタログに対し、厳しいレイテンシ制約のもとで効率的に処理することにある。
- こうした要求に応えるため、産業規模の検索エンジンでは一般に「インデックス・検索・ランク付け(index-retrieve-then-rank)」というパラダイムが採用されている [29]。
- ここで第一段階の

Permission to make digital or hard copies of all or part of this work for personal or
classroom use is granted without fee provided that copies are not made or distributed
for profit or commercial advantage and that copies bear this notice and the full citation
on the first page. Copyrights for components of this work owned by others than the
author(s) must be honored. Abstracting with credit is permitted. To copy otherwise, or
republish, to post on servers or to redistribute to lists, requires prior specific permission
and/or a fee. Request permissions from permissions@acm.org.

Conference acronym 'XX, Woodstock, NY

@ 2018 Copyright held by the owner/author(s). Publication rights licensed to ACM.
ACM ISBN 978-1-4503-XXXX-X/2018/06
https://doi.org/XXXXXXXXXXXXXX

- 検索 (retrieval) は極めて重要である。
- なぜなら、この段階が再現率の上限を決定づけ、ここで取りこぼされた関連商品は後段では復元できないためである。

- **Dense retrieval: 主流のパラダイムとその課題。**
- Dense retrievalは、ニューラルネットワークを用いてクエリと文書を低次元の密ベクトルにエンコードし、大規模な意味的マッチングを可能にする手法である [17, 22, 23]。
- しかし、産業規模のEコマース応用においては大きな課題を抱えている。
- (i) 密ベクトルは「ブラックボックス」としての性質を持ち、解釈性に欠け、モデルの判断根拠を理解することが難しい。
- (ii) インデックスとストレージのオーバーヘッドが大きい。
- 例えば、MS MARCO passage rankingデータセット [3] において、Dense retrieval手法では元のコーパスの数倍から数十倍のインデックスサイズが必要となる [34, 52]。

- **Sparse retrieval: 解釈性とストレージ効率への回帰。**
- Dense retrievalとは対照的に、Sparse retrievalは高次元かつスパースなベクトル上で動作する。
- 各次元は語彙中の特定の単語(term)に対応し、その値はその単語の重要度を表す [1, 13, 44]。
- 解釈性とストレージ効率という本質的な利点から、Sparse retrievalは産業規模の検索システムにおいて重要な構成要素であり続けている。
- Sparse retrievalの発展は、古典的な統計モデル [1, 44] から学習型Sparse retrieval [8, 13, 53] へと進化してきた。

- その大きなマイルストーンがSPLADE [13] である。
- SPLADEはBERTを用いて単語の拡張(term expansion)と重み付けを同時に学習し、検索精度を大幅に向上させた。
- しかしSPLADEは、本質的にBERTバックボーンの事前学習知識と意味理解能力に制約されており、語彙ミスマッチ(vocabulary mismatch)という根本的な問題に対処する能力が限定的である。
- さらに、我々の予備分析(セクション2.2参照)で示されるように、SPLADEのような強力なモデルであっても、商品検索のシナリオに直接適用すると、古典的なdense retrieverと比較して目に見える性能差が生じる。

- **LLMs as sparse retrievers: 課題。**
- 大規模言語モデル(LLM)は、その事前学習知識と意味解析の潜在能力 [38, 43, 46] により、意味的理解と解釈性・ストレージ効率の両立を通じて商品検索を発展させる有望な可能性を提示している。
- 我々は、LLMをSparse retrievalのバックボーンとして用いることを検討し、その意味理解能力を活用しつつ、Sparseな手法の利点を保持することを目指している。
- しかし予備実験の結果(セクション2.2)、SPLADEのBERTを単純にQwen2.5-3B [43] のようなLLMに置き換えるだけでは、2つの主要な問題が生じることが明らかになった。
- (i) 語彙拡張のハルシネーション (Lexical expansion hallucination)。
- モデルは拡張された単語や、さらには無関係な単語を過度に重視し、ブランド名や型番のようなユーザー意図を捉えるうえで不可欠なリテラル(literal)な単語の重みを低く見積もる傾向がある。
- (ii) 不安定な学習初期化。
- LLMの語彙空間は非常に大きいため、適切な誘導なしでは学習が大幅に困難になる。
- モデルは超高次元空間(例えばQwen2.5では15,000次元を超える)において、短いユーザークエリと商品タイトルを拡張することを学習しなければならず、これが学習の安定性と効率を損なう。

- **LLMs as sparse retrievers: 解決策。**
- 上述の問題に対処するため、我々はPROSPER (PROduct search using LLMs as SParsE Retrievers) を提案する。
- PROSPERは、アーキテクチャと学習の両面で貢献を導入する。
- (i) 我々はliteral residual network (LRN) を設計する。
- これは補償的な重み付け機構を用いて、ユーザークエリやアイテム中のリテラルな単語の重要度を増幅させる。
- これにより、モデルの注意をブランド名や型番のようなユーザーにとって重要なトークンに固定することで、ハルシネーションを効果的に緩和する。
- (ii) 我々はlexical focusing window (LFW) を導入する。
- これはFLOPS正則化 [41] と協調して、モデルを粗から細へ(coarse-to-fine)のスパース化プロセスへと導く。
- LFWは学習初期段階でハード制約として機能し、モデルに迅速にスパース化を達成させ、超高次元の表現学習からできるだけ早く脱出させる。
- 一方、FLOPS正則化は学習の進行に伴い細粒度の制御を提供し、最初から効率的かつ的確な学習を保証する。

- 我々の知る限り、本研究は商品検索におけるSparse retrievalにLLMを活用することを検討した最初の研究である。

- **実験的知見。**
- 我々はPROSPERを、公開データセットであるMulti-CPR Eコマースデータセットと、Taobao検索ログからサンプリングした実世界データセットの両方を用いたオフライン実験で評価する。
- PROSPERは、BM25ベースライン [44] と比較して主要指標である目標商品再現率(target product recall)で10.2%の大幅な改善を達成し、SPLADEベースライン [11] に対しても4.3%の向上を示しつつ、先進的なdense retrievalモデルと同等の性能を実現している。
- さらに、Taobao検索1におけるオンライン実験を実施し、主要指標であるGMVで0.64%の改善を達成した。

## 2 準備

- 第一段階の商品検索の正式な定義は付録 A に記載する。
- 本セクションでは、提案手法の基盤となる SPLADE フレームワークを紹介し、商品検索において SPLADE を実装する際に直面した課題を概観する。

### 2.1 SPLADE

- **モデルアーキテクチャ。**
- 入力クエリまたはドキュメントの系列(WordPiece トークナイズ後)を $S = (t_1, t_2, \ldots, t_N)$ 、その対応する BERT 埋め込みを $h = (h_1, h_2, \ldots, h_N)$ とすると、SPLADE は各隠れ表現を masked language modeling head によって語彙サイズのベクトル $H_i \in \mathbb{R}^{|V|}$ に射影する。
- $H_i$ の $j$ 番目の次元は、入力トークン $i$ に対する語彙トークン $j$ の重要度を表しており、実際には language modeling head の出力ロジットに相当する。
- 最終表現は、各トークンのロジットに ReLU 活性化と log 飽和効果を適用した後、トークン位置にわたって max-pooling を行うことで得られる:

$$
w_j = \max_{i \in t} \log(1 + \mathrm{ReLU}(w_{ij})) \tag{1}
$$

- ここで $w_{ij}$ は入力トークン $i$ に対する語彙トークン $j$ の重要度を表し、 $w_j$ は表現中の項 $j$ の最終的な重み付けである。

- **モデル学習。**
- SPLADE はランキング損失と正則化項を組み合わせて学習される。
- ランキング損失では、in-batch negatives [30, 42] と hard negative sampling [51] という 2 つの負例サンプリング戦略を用いる。
- バッチ内のクエリ $q_i$ 、正例ドキュメント $d_i^+$ 、hard negative ドキュメント $d_i^-$ (例えば BM25 サンプリング由来)、およびバッチ内の負例ドキュメント集合(他のクエリの正例ドキュメント) $\{d_{ij}^-\}_j$ が与えられたとき、対比学習のためにモデルは InfoNCE 損失 [47] で学習される:

$$
\mathcal{L}_{\text{rank-IBN}} = -\log \frac{e^{s(q_i, d_i^+)}}{e^{s(q_i, d_i^+)} + e^{s(q_i, d_i^-)} + \sum_j e^{s(q_i, d_{ij}^-)}} \tag{2}
$$

- ここで $s(q, d)$ はクエリ表現とドキュメント表現の内積によって得られるランキングスコアを表す。

1Taobao (https://www.taobao.com/) is one of China's largest e-commerce platforms.

- 学習された表現のスパース性を促進するため、SPLADE は FLOPS 正則化 [41] を採用している。
- これはスコアリングに必要な浮動小数点演算の平均回数を滑らかに近似したものであり、検索レイテンシに直接結びついている。
- これは $a_j$ をトークン $j$ の活性化(すなわち項が非ゼロの重みを持つ)確率 $p_j$ の連続緩和として用いて定義され、サイズ $N$ のバッチ内のドキュメント $d$ に対して $\bar{a}_j = \frac{1}{N} \sum_{i=1}^{N} w_j^{(d_i)}$ によって推定される。
- FLOPS 損失は次のように定義される:

$$
\ell_{\mathrm{FLOPS}} = \sum_{j \in V} \bar{a}_j^2 = \sum_{j \in V} \left( \frac{1}{N} \sum_{i=1}^{N} w_j^{(d_i)} \right)^2 \tag{3}
$$

- この正則化は SNRM [53] で用いられる $\ell_1$ 正則化と異なり、平均項重みが高くなることをペナルティ化することで、よりバランスの取れたインデックス分布を促進する。
- 全体的な学習目的関数はランキング損失と正則化項を組み合わせたものとなる:

$$
\mathcal{L} = \mathcal{L}_{\text{rank-IBN}} + \lambda_q \ell_{\mathrm{FLOPS}}^q + \lambda_d \ell_{\mathrm{FLOPS}}^d \tag{4}
$$

- ここで $\lambda_q$ と $\lambda_d$ はそれぞれクエリとドキュメントに対する正則化強度を調整するハイパーパラメータであり、それぞれに対して異なるスパース性制御を可能にする。
- SPLADE の後継版 [11, 12] では蒸留などの追加学習手法が導入されているが、本研究はそうしたより複雑な手法と直交する対比学習に焦点を当てている。

### 2.2 探索と課題

- SPLADE [11, 13] は、特にパッセージ検索におけるいくつかのベンチマークで dense retrieval に匹敵する性能を示してきたが、商品検索シナリオにおける実用的有効性は未だ十分に検証されていない。

- **パッセージ検索と商品検索の違い。**
- 従来のパッセージ検索では、パッセージは内容が豊富で多くのノイズ項を含んでいるため、モデルは拡張に重要な項を識別しつつノイズ項を除去することが求められる。
- しかし商品検索では、ユーザクエリも商品タイトルも本質的にキーワードの集合であり情報密度が高いため、以下のような明確な課題が生じる: (i) ユーザクエリに対しては、モデルは短く具体的なユーザニーズを正確に理解する必要があり、ここではすべての文字通りのクエリ項が通常重要となる。
- (ii) 商品タイトルに対しては、商品タイトルが簡潔であることから、モデルは潜在的なクエリ項を網羅的にカバーできるよう表現を十分に豊かに拡張する必要がある。

- **商品検索における SPLADE の実装。**
- Multi-CPR E-commerce テストデータセット [32] 上で BERT ベースの SPLADE モデルを用いた初期実験では、Hit@1000 で 89.6% を達成した。
- これは妥当な値ではあるが、DPR が達成した 92.1% や、MS MARCO passage ranking データセット [3] で報告されている 96% 超の値には及ばない。

- **商品検索のための LLM による SPLADE の強化。**
- 近年、研究者は LLM をスパース検索に適応させる試みを始めている(詳細な関連研究は付録 B を参照)。
- Zeng ら [54] は LLM ベースのスパース検索器のスケーリング則を研究しており、CSPLADE は Nv-Embed [26] および echo embedding [45] に倣い、LLM を用いて SPLADE を強化する際に単方向アテンションが引き起こす情報フローの問題を解決した。

- これらの研究に触発され、まず BERT を Qwen-2.5-3B [43] に置き換えたところ、Multi-CPR E-commerce テストデータセット [32] における Hit@1000 スコアは 91.3% に向上した。
- さらに、

<table>
<caption>Table 1: LLM ベース SPLADE における語彙拡張ハルシネーションの例。項は重みの降順でランク付けされている。文字通りの項は黒色、有用な拡張は緑色、ノイズとなる拡張は赤色で示されている。</caption>
<tr>
<th>Query</th>
<th>Top-Weighted Query Terms</th>
</tr>
<tr>
<td>爱立舍机油滤芯 (Elysee oil filter)</td>
<td>油(oil),滤(filter),芯(core),心(heart),机(engine), oil,燃(fuel),柴(diesel),筛(sieve),泵(pump), 污(dirt),cpu,Machine,舶(ship),脂(fat),爱(love)</td>
</tr>
<tr>
<td>老捷豹副水箱 (Jaguar water tank) ® .</td>
<td>箱(tank),豹(Jaguar),水(water),副(aux),捷 (Jaguar), (racoon), &amp;}(jackal), water, *(old), 缸(tank),虎(tiger),沈(Shen), ford,狮(lion)</td>
</tr>
</table>

- LLM のアテンション機構を最適化して表現品質を高める先行研究 [4, 45, 52] も参考にして、最大 92.4% までの性能向上を達成したが、目的の商品のランキングは依然として最適とはいえなかった。

- **ケーススタディと課題。**
- ケース分析からは、深刻な語彙拡張ハルシネーションが明らかになった(Table 1 参照): (i) ブランドのような文字通りの項が過小評価されたままだった(例えば "爱立舍机油滤芯" において "Elysee" が見落とされた)。
- (ii) 曖昧またはまれなクエリでは無関係な拡張が現れた(例えば "老捷豹副水箱" においてモデルは無関係な動物に関する項を拡張した)。
- さらに、LLM は通常非常に大きな語彙を持つ。
- 例えば、Qwen-2.5 モデル [43] は 150,000 を超える次元を含んでおり、これはユーザクエリ(Taobao-Internal データセットで平均 6 項)や商品タイトル(Taobao-Internal データセットで平均 25 項)の短い長さに対して過剰である。
- 適切な制約なしには、高次元空間のスパース化は学習初期段階を不安定にし、モデルが意味のあるスパース表現を学習することを妨げてしまう。

## 3 手法

- 図1に示すように、PROSPER フレームワークは以下の2つの主要領域で革新を取り入れている。
- (i) モデルアーキテクチャでは、語彙拡張ハルシネーション(lexical expansion hallucination)を緩和するために literal residual network を導入する。
- (ii) モデル学習では、より的を絞った学習初期化を提供するために lexical focusing window を導入する。

### 3.1 モデルアーキテクチャ

- **LLM ベースの表現.**
- SPLADE [11] を基盤として、本手法では意味理解能力を強化するために LLM をバックボーンモデルとして使用する。
- 入力クエリまたはアイテム系列(トークナイズ後) $S = (t_1, t_2, \ldots, t_N)$ に対し、LLM から最終層の隠れ状態 $h = (h_1, h_2, \ldots, h_N)$ を抽出する。
- 各隠れ表現は次に、language modeling head (LM head) を通して語彙サイズのベクトルに射影され、各トークン位置 $i$ における logits $H_i \in \mathbb{R}^{|V|}$ を得る。
- 最終層の隠れ状態 $h$ と logits $H$ を抽出した後、それらを literal residual network に入力する。

- **Literal residual network (LRN).**
- LRN の核心となる考え方は、LLM がまず literal な用語に注目し、その後関連語へと拡張するように誘導することであり、ユーザーの具体的なニーズを表す product brand や product model のような重要な用語に十分な重みを割り当てることである。

- LLM から抽出された隠れ状態 $h$ と logits $H$ に対し、まず ReLU 活性化と log-saturation 変換を適用する。

$$
\tilde{h}_i = \log(1 + \mathrm{ReLU}(h_i)), \quad \tilde{H}_{ij} = \log(1 + \mathrm{ReLU}(H_{ij})) \tag{5}
$$

- ここで $h_i$ は $i$ 番目の入力トークンに対する隠れ状態ベクトルであり、 $H_{ij}$ は $i$ 番目の入力トークンに対する $j$ 番目の語彙項の重要度を表す。

- 次に、これらの表現をトークン位置にわたってプーリングする必要がある。
- SPLADE は max-pooling を使用する [11] が、これは LLM にとっては最適ではない。
- BERT における bidirectional attention とは異なり、LLM は各トークンが先行するトークンにのみ注目できる causal attention を採用している。
- この制約を緩和するために、入力系列の最終トークン位置の表現を取る last-pooling [4, 46] を採用する。
- これは系列全体からの情報を効果的に集約できるためである。
- 基本表現 $w$ は、変換された logits $\tilde{H}$ を last-pooling することで得られる。

$$
w_j = \mathrm{Last}(\tilde{H}_{ij}) \tag{6}
$$

- ここで $w_j$ は語彙中の $j$ 番目の項に対する重みである。

- 同時に、変換された隠れ状態 $\tilde{h}$ を last-pooling することで、プーリング済みの隠れ状態表現を得る。

$$
h_{\mathrm{last}} = \mathrm{Last}(\tilde{h}) \tag{7}
$$

- 次に、LRN はこのベクトル $h_{\mathrm{last}}$ を全結合層 FClayer に通し、隠れ次元から語彙次元へと射影することで、強化ベクトル $w' \in \mathbb{R}^{|V|}$ を生成する。

$$
w' = \mathrm{FClayer}(h_{\mathrm{last}}) \tag{8}
$$

- 基本表現 $w$ と強化ベクトル $w'$ の両方を得た後、それらを集約して最終表現 $W$ を導出する。

$$
W = w + I \odot (\max(w') - w') \tag{9}
$$

- ここで $I$ は系列 $S$ 中の literal な用語に対応する位置で値1を取り、それ以外で0を取る指標ベクトルであり、 $\odot$ は要素ごとの乗算を表し、 $\max(w')$ は $w'$ における全次元中の最大重みを表す。
- 重み $\max(w') - w'$ は literal residual value として機能し、literal な用語の重みを強化するために用いられる。
- 次に、最終表現 $W$ と基本表現 $w$ を用いてモデルを学習する。

- **議論.**
- LRN の動作は補償的な重み付け機構のようなものである。
- 基本重み $w_{t_i}$ を持つ literal な用語 $t_i$ について、 $w_{t_i}$ が低い場合、これはモデルが literal な用語 $t_i$ に十分注目していないことを示しており、より多くの重みで補償することでモデルがこの用語により注目するようにする。
- 逆に、 $w_{t_i}$ がすでに高い場合、これはモデルがその用語に十分注目していることを示しており、補償は少なめに与えられる。
- この柔軟な literal な用語の重み補償機構を通じて、モデルが product brand、product model、その他のユーザーの具体的なニーズを表す用語へと徐々に注目を向けるよう誘導することができる。

### 3.2 モデル学習

- **Coarse-to-fine な疎化.**
- FLOPS 正則化はスパース性を制御するために導入されたが、これはソフトな機構として動作するため、学習の重要な初期段階においてモデルを効果的に誘導するには不十分である。
- 我々は、疎化は coarse-to-fine 戦略に従うべきであると主張する。
- すなわち、学習初期では高次元空間から効率的に脱出し強固な基盤を確立するために迅速な疎化を強制すべきであり、後期段階では検索品質と疎性のバランスを取るために段階的な精緻化を採用すべきである。

- **Lexical focusing window.**
- Coarse-to-fine の考えに基づき、学習初期を誘導するために Lexical Focusing Window (LFW) を提案する。
- LFW は条件付き top-k プーリング演算子 $\mathrm{TopK}_k$ を適用することで動作し、表現 $W$ における非ゼロ次元の数がウィンドウサイズ $k$ を超える場合にのみプーリングを適用する。

$$
\mathrm{TopK}_k(W) = \begin{cases} \mathrm{TopK}(W, k) & \text{if } \|W\|_0 > k \\ W & \text{if } \|W\|_0 \le k \end{cases} \tag{10}
$$

- ここで $\|\cdot\|_0$ は $\ell_0$ ノルムであり、ベクトル中の非ゼロ要素を数える。
- 標準的な TopK 関数は $k$ 個の最大重みを保持し、その他をゼロに設定する。
- この条件付き適用により、LFW は主に学習の初期かつ密な段階で作用し、表現が自然に疎になるにつれて緩やかにフェードアウトすることが保証される。

- LFW と FLOPS 正則化は相乗的に機能する。
- (i) 学習初期段階では、LFW はハード制約として作用し、モデルを最も重要な用語の限定された集合に集中させ、迅速かつ的を絞った疎化を可能にする。
- (ii) 表現が安定した後は、LFW の役割は減少し、FLOPS 正則化器が引き継いで細かな調整を行う。

- **学習目的関数.**
- LRN アーキテクチャと LFW 機構が定義されたところで、最終的な学習目的関数を定式化することができる。
- SPLADE と同様に、本手法の学習目的関数はクエリとアイテムの表現間の類似度スコアを必要とする contrastive ranking loss に基づいている。
- 元の SPLADE は標準的な内積を採用しているが、我々はクエリ側に $\ell_2$ 正規化を導入する。
- これは実験において疎化と検索性能の両方を改善することが分かった修正である(付録D.2 を参照)。
- 類似度スコアは LFW 演算子を用いて以下のように計算される。

$$
S_{\mathrm{LFW}}(W_q, W_d) = \frac{\mathrm{TopK}_{k_q}(W_q)}{\|\mathrm{TopK}_{k_q}(W_q)\|_2} \cdot \mathrm{TopK}_{k_d}(W_d) \tag{11}
$$

- ここで $W_q$ と $W_d$ は LRN 出力からのクエリとアイテムの表現であり、 $k_q$ と $k_d$ はそれぞれの LFW サイズであり、 $\|\cdot\|_2$ は $\ell_2$ ノルムである。
- 我々の分析では、ウィンドウサイズの動的縮小は有意な改善を生まなかったことが示されており、その主な利点は頑健で効率的な学習開始を可能にすることであることが確認された。

- 我々の学習目的関数は、in-batch negatives [30] を組み込んだ InfoNCE 損失関数 [47] を使用する。
- あるクエリ表現 $W_{q_i}$ 、その正例の商品表現 $W_{d_i^+}$ 、および in-batch negatives の集合 $\{W_{d_{ij}^-}\}_j$ (バッチ内の他のクエリの正例ドキュメント)に対し、ランキング損失は以下のとおりである。

$$
\mathcal{L}_{\text{rank-LFW}} = -\log \frac{e^{S_{\mathrm{LFW}}(W_{q_i}, W_{d_i^+})}}{e^{S_{\mathrm{LFW}}(W_{q_i}, W_{d_i^+})} + \sum_j e^{S_{\mathrm{LFW}}(W_{q_i}, W_{d_{ij}^-})}} \tag{12}
$$

- 全体の学習目的関数は、このランキング損失とクエリおよびアイテム両方に対する FLOPS 正則化項 [41] を組み合わせる。

$$
\mathcal{L}' = \mathcal{L}_{\text{rank-LFW}} + \lambda_q \ell_{\mathrm{FLOPS}}^q + \lambda_d \ell_{\mathrm{FLOPS}}^d \tag{13}
$$

- ここで $\lambda_q$ と $\lambda_d$ は FLOPS の正則化のバランスを取るハイパーパラメータである。
- なお、FLOPS 正則化は基本表現 $W_q$ と $W_d$ に適用される。

## 4 オフライン実験

- 本節では、商品検索シナリオにおいて一連のオフライン実験を行い、PROSPER を包括的に評価する。

### 4.1 実験設定

- **データセット。**
- 公開ベンチマークと実世界の産業環境の両方を代表する2つのデータセットで実験を行う。
- (i) Multi-CPR E-commerce [32]。
- Multi-CPR は公開されているマルチドメインの中国語パッセージ検索データセットであり、その E-commerce サブセットを利用する。
- (ii) Taobao-Internal。
- 実世界の産業環境において提案手法をさらに検証するため、2025年6月の Taobao Search の実際のユーザークリックログから約107万件のクエリ-アイテムペアをサンプリングして、新しいデータセットを構築した。

- Multi-CPR E-commerce データセットは人手でアノテーションされており、より直接的な関連性シグナルを提供する。
- 一方、Taobao-Internal データセットはユーザークリックログから構築されており、クエリとアイテム間の関連性シグナルはより複雑かつ多様である。
- クエリやアイテムの長さ・件数などの詳細なデータセット情報は付録C.1に示す。

- **ベースライン。**
- Dense ベースラインとして以下と比較する。
- (i) DPR [22]、古典的な dense 検索ベースライン。
- (ii) BGE シリーズ [50]、強力な dense テキスト埋め込みモデルのシリーズで、比較には bge-large-zh-v1.5 と bge-base-zh-v1.5 を使用する。
- Sparse ベースラインとして以下を使用する。
- (i) BM25 [44]、古典的な sparse 手法。
- BERT-base-chinese と Qwen2.5-3B のトークナイザーをそれぞれ使用する BM25BERT および BM25Qwen と比較する。
- (ii) Doc2Query [40]、seq2seq モデルを用いて文書に対する潜在的なクエリを生成することで語彙ミスマッチを緩和する手法。
- (iii) DeepCT [5, 8]、BERT を活用してリテラル項の重要度を評価する手法。
- (iv) SPLADE [11, 13]、本研究の主要なベースライン。
- SPLADE [13] と SPLADE-v2 [11] の両方を使用し、公平な比較のために学習プロセスを調整した。
- (v) BERT バックボーンを Qwen2.5-3B モデルに置き換えた SPQwen-backbone [54] を実装した。
- さらに、先行研究 [4, 26, 45, 52] に従い、表現品質を向上させるために LLM のアテンション機構を最適化することを検討した。
- 入力シーケンスを複製した SPQwen-echoembedding [45, 52] と、双方向アテンション機構を持つ SPQwen-bidattention [4, 26, 52] である。

- **モデルバリアント。**
- 提案する各構成要素の有効性を検証するため、PROSPER のいくつかのバリアントを作成した。

- コアとなるモデル設計を分析するため、以下のバリアントを実装した。
- (i) PROSPERBERT、Qwen2.5-3B [43] バックボーンを BERT-base-chinese [9] に置き換えたもの。
- (ii) PROSPERmax-pooling、SPLADE の max-pooling 戦略を用いるもの。
- (iii) PROSPERbid-attention、causal attention の代わりに双方向アテンションを用いるもの [4, 52]。
- (iv) PROSPERecho-emb、入力シーケンスを複製して双方向の受容野をシミュレートするもの [26, 45, 52]。

- LRN の役割を調査するためのバリアントは以下の通りである。
- (i) PROSPERw/o-LRN、LRN モジュールを完全に除去したもの。
- (ii) PROSPERLRN-add、残差接続を直接加算 (W = w + IO w') に置き換えたもの。
- (iii) クエリ (PROSPERLRN-q) もしくはアイテム (PROSPERLRN-d) のみに LRN を適用するバリアント。

- LFW の評価のため、以下を実験した。
- (i) LFW を除去 (PROSPERw/o-LFW)。
- (ii) 動的なウィンドウサイズ (PROSPERLFW-dynamic) の使用。
- (iii) クエリ (kg) およびアイテム (kd) について様々な固定ウィンドウサイズの使用。

- リテラル項と拡張項の貢献を調査するため、以下をテストした。
- (i) PROSPERliteral と PROSPERexpansion、それぞれリテラル項のみまたは拡張項のみで学習・評価することで、それぞれ単独の寄与を理解するもの。
- (ii) PROSPERmask-lit と PROSPERmask-expan、モデルは通常通り学習するが、マッチング・評価段階でリテラル項または拡張項のいずれかをマスクアウトすることで、十分に学習されたモデルにおける各項の役割を分析するもの。

- **実装の詳細。**
- デフォルトのバックボーンモデルとして Qwen2.5-3B を使用し、lexical focusing window のサイズは kq = 256、

<table>
<caption>表2: Multi-CPR E-commerce および Taobao-Internal データセットでの主要結果(%)。最良の結果を太字で示す。「-」は元の Multi-CPR 論文 [32] で報告されていない指標を示す。</caption>
<tr>
<th rowspan="2"></th>
<th rowspan="2">手法</th>
<th colspan="5">Multi-CPR E-commerce</th>
<th colspan="3">Taobao Internal</th>
</tr>
<tr>
<th>Hit@1</th>
<th>Hit@10</th>
<th>Hit@100</th>
<th>Hit@1000</th>
<th>MRR@10</th>
<th>Recall@10</th>
<th>Recall@100</th>
<th>Recall@1000</th>
</tr>
<tr>
<td rowspan="3">Dense ベースライン</td>
<td>DPR</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>92.1</td>
<td>27.04</td>
<td>42.50</td>
<td>72.61</td>
<td>91.07</td>
</tr>
<tr>
<td>BGE-base-zh-v1.5</td>
<td>26.6</td>
<td>54.1</td>
<td>80.4</td>
<td>93.7</td>
<td>34.70</td>
<td>50.83</td>
<td>75.87</td>
<td>92.93</td>
</tr>
<tr>
<td>BGE-large-zh-v1.5</td>
<td>26.1</td>
<td>55.2</td>
<td>81.9</td>
<td>93.1</td>
<td>35.10</td>
<td>50.66</td>
<td>76.89</td>
<td>93.45</td>
</tr>
<tr>
<td rowspan="9">Sparse ベースライン</td>
<td>BM25Qwen</td>
<td>14.3</td>
<td>37.1</td>
<td>62.6</td>
<td>83.7</td>
<td>20.60</td>
<td>39.80</td>
<td>65.53</td>
<td>84.68</td>
</tr>
<tr>
<td>BM25BERT</td>
<td>16.5</td>
<td>40.9</td>
<td>66.9</td>
<td>85.5</td>
<td>23.48</td>
<td>41.23</td>
<td>67.84</td>
<td>86.21</td>
</tr>
<tr>
<td>Doc2Query</td>
<td>-</td>
<td>-</td>
<td>-</td>
<td>82.6</td>
<td>23.85</td>
<td>42.06</td>
<td>68.41</td>
<td>86.72</td>
</tr>
<tr>
<td>DeepCT</td>
<td>21.9</td>
<td>46.4</td>
<td>72.2</td>
<td>87.5</td>
<td>29.14</td>
<td>46.64</td>
<td>73.26</td>
<td>86.90</td>
</tr>
<tr>
<td>SPLADE</td>
<td>17.2</td>
<td>42.7</td>
<td>70.6</td>
<td>89.2</td>
<td>25.87</td>
<td>44.41</td>
<td>72.67</td>
<td>89.96</td>
</tr>
<tr>
<td>SPLADE-v2</td>
<td>18.4</td>
<td>44.1</td>
<td>71.3</td>
<td>89.6</td>
<td>26.40</td>
<td>45.28</td>
<td>73.41</td>
<td>90.38</td>
</tr>
<tr>
<td>SPQwen-backbone</td>
<td>18.2</td>
<td>43.7</td>
<td>72.3</td>
<td>91.3</td>
<td>25.46</td>
<td>45.12</td>
<td>73.46</td>
<td>91.79</td>
</tr>
<tr>
<td>SPQwen-echoembedding</td>
<td>19.7</td>
<td>44.0</td>
<td>74.2</td>
<td>92.4</td>
<td>26.72</td>
<td>45.27</td>
<td>74.35</td>
<td>92.84</td>
</tr>
<tr>
<td>SP Qwen-bidattention</td>
<td>19.5</td>
<td>43.8</td>
<td>73.5</td>
<td>91.8</td>
<td>26.41</td>
<td>45.39</td>
<td>73.89</td>
<td>92.10</td>
</tr>
<tr>
<td rowspan="5">本研究</td>
<td>PROSPER</td>
<td>25.3</td>
<td>50.7</td>
<td>78.1</td>
<td>93.9</td>
<td>32.85</td>
<td>50.90</td>
<td>76.20</td>
<td>94.08</td>
</tr>
<tr>
<td>PROSPERBERT</td>
<td>23.6</td>
<td>49.2</td>
<td>75.8</td>
<td>91.5</td>
<td>31.83</td>
<td>50.43</td>
<td>75.97</td>
<td>93.68</td>
</tr>
<tr>
<td>PROSPER max-pooling</td>
<td>22.6</td>
<td>49.5</td>
<td>78.3</td>
<td>93.6</td>
<td>30.85</td>
<td>48.45</td>
<td>76.33</td>
<td>93.75</td>
</tr>
<tr>
<td>PROSPER echo-emb</td>
<td>24.5</td>
<td>50.7</td>
<td>80.3</td>
<td>94.1</td>
<td>32.82</td>
<td>50.18</td>
<td>77.20</td>
<td>94.43</td>
</tr>
<tr>
<td>PROSPER bid-attention</td>
<td>22.3</td>
<td>51.4</td>
<td>78.7</td>
<td>93.6</td>
<td>30.72</td>
<td>51.06</td>
<td>76.51</td>
<td>93.80</td>
</tr>
</table>

- ka = 512 とした。
- すべてのモデルは 8 枚の NVIDIA H20 96GB GPU を使用し、学習率 3e-5、デバイスあたりバッチサイズ 64、AdamW オプティマイザ [33] により 5 エポック学習した。
- FLOPS 正則化パラメータ Aq と Ad はそれぞれ 5e-3 と 1e-3 に設定した。
- 全体性能比較を超える解析実験はすべて公開データセットの Multi-CPR E-commerce のみで実施し、再現性を高め、今後の研究との直接比較を可能にした。
- より詳細な実装設定は付録C.2に示す。

- **評価指標**
- 各データセットの特性に合わせて異なる評価指標を採用する。
- (i) Multi-CPR E-commerce データセットでは、各クエリが単一の関連アイテムに対応するため、MRR@10 および Hit@k(k=1, 10, 100, 1000)を使用する。
- (ii) Taobao-Internal データセットでは、各クエリが複数 (1〜10) の関連アイテムを持ちうるため、Recall@k(k=10, 100, 1000)を使用する。
- 商品検索において、Recall@1000 はより大きな候補集合内で関連アイテムを取得するシステムの能力を測るものであり、第一段階の検索において極めて重要である。

### 4.2 実験結果

- **全体性能。**
- PROSPER と各種ベースラインとの包括的な比較を行った。
- 表2に示すように、両データセットでの主要結果から以下のいくつかの重要な知見が得られた。
- (i) 提案手法の PROSPER は、両データセットを通してすべての sparse ベースラインを一貫してかつ有意に上回る。
- これは実世界のシナリオで sparse 検索に LLM を活用することの優れた有効性を示している。
- なお、PROSPERBERT も SPLADE-v2 を有意に上回ることは特筆に値し、提案する LRN が Qwen2.5 のみならず BERT モデルでも有効であることを示している。
- これは、本手法がバックボーンアーキテクチャに依存せず、語彙拡張の幻覚問題を効果的に緩和することを示唆している。
- (ii) Dense ベースラインと比較すると、PROSPER は同等の

- 性能を達成している。
- BGE シリーズのような高度な dense モデルは、公開データセットの Hit@1, 10, 100 および MRR@10 において優れた性能を達成しており、上位位置でターゲット商品を正確にランキングする dense 検索の利点を示している。
- 一方、PROSPER は Hit@1000 および Recall@1000 指標で優れた性能を示し、候補集合における関連アイテムのカバレッジが優れていることを示している。
- この優位性は、第一段階の検索において特に重要である。
- なぜなら、その主目的は完璧な初期ランキングを実現することではなく、関連アイテムを後続のランキング段階に確実に含めることだからである。
- (iii) 各バリアントは PROSPER をさらに検証している。
- PROSPER と PROSPERBERT 間の性能差は、Qwen2.5 をバックボーンとして使用することの大きな利点を強調している。
- PROSPER と PROSPERmax-pooling の比較により、last-token pooling 戦略は SPLADE で用いられる max-pooling アプローチを上回ることが、特に Hit@1 および MRR@10 指標で観察される。
- PROSPERecho-emb バリアントは、入力シーケンスを繰り返すことでシーケンス全体にわたる情報をより活用できることを示しており、特に Hit@1000 と Recall 指標で控えめな性能向上が見られる。
- しかし、シーケンス複製による計算コストの増加は、実際にこのアプローチを展開する際にはより慎重さが必要であることを意味する。
- 興味深いことに、PROSPERbid-attention で双方向アテンションに切り替えても、causal attention モデルに対して一貫した改善は見られなかった。
- これは、アテンション機構を強制的に双方向に変更することで、LLM 内の事前学習済み知識が破壊される可能性があるためと推測される。

- **LRN の影響。**
- 提案する LRN の有効性を深く評価するため、異なるバリアントを用いた一連の実験を行った。
- 図2に示すように、結果は提案する LRN 機構が検索性能の向上において重要な役割を果たすことを明確に示している。
- LRN を除去 (PROSPERw/o-LRN) すると、すべての指標で劇的な性能低下が生じる。
- 興味深いことに、PROSPERLRN-q と PROSPERLRN-d はいずれも LRN なしのベースラインに対して類似の性能改善を達成しており、LRN

<table>
<caption>表3: LFW が検索性能に与える影響(%)。</caption>
<tr>
<th>バリアント</th>
<th>Hit@1</th>
<th>Hit@10</th>
<th>Hit@100</th>
<th>Hit@1000</th>
</tr>
<tr>
<td>ka=1024, kq=512</td>
<td>22.3</td>
<td>49.2</td>
<td>77.7</td>
<td>93.5</td>
</tr>
<tr>
<td>ka=512, kg=256</td>
<td>25.3</td>
<td>50.7</td>
<td>78.1</td>
<td>93.9</td>
</tr>
<tr>
<td>ka=256, kq=128</td>
<td>23.7</td>
<td>50.2</td>
<td>77.0</td>
<td>93.4</td>
</tr>
<tr>
<td>ka=128, kg=64</td>
<td>23.5</td>
<td>49.1</td>
<td>77.2</td>
<td>92.9</td>
</tr>
<tr>
<td>ka=64, kq=32</td>
<td>21.9</td>
<td>48.3</td>
<td>74.3</td>
<td>91.9</td>
</tr>
<tr>
<td>PROSPERLFW-dynamic</td>
<td>24.6</td>
<td>49.0</td>
<td>77.8</td>
<td>93.4</td>
</tr>
<tr>
<td>PROSPERw/o-LFW</td>
<td>13.3</td>
<td>36.2</td>
<td>65.6</td>
<td>87.2</td>
</tr>
</table>

- 機構がクエリ表現とアイテム表現の両方に有益であることを示している。
- さらに、PROSPER と PROSPERLRN-add の比較から、より直感的な直接加算アプローチに対する補償的重み付け機構の優位性が明らかになる。

- **LFW の影響。**
- LFW の有効性を評価するため、異なる focusing window サイズの設定で PROSPER を評価した。
- 表3に示すように、以下のことがわかる。
- (i) LFW なし (PROSPERw/o-LFW) では、モデルの性能はすべての指標で劇的に低下する。
- これは、学習中にモデルのアテンションを最も関連性の高い項に誘導することが本質的に重要であるという我々の仮説を裏付けている。
- (ii) 異なるウィンドウサイズの中で、kq = 512、kd = 256 の設定が全体として最良の性能を達成し、最も関連性の高い項に焦点を絞ることと十分な語彙カバレッジを維持することの間で最適なバランスを取っている。
- (iii) 動的な LFW アプローチ PROSPERLFW-dynamic(クエリには (256, 128, 64)、アイテムには (512, 256, 128))は、最適な固定ウィンドウ設定を超えない。
- これは、適切に選択された固定ウィンドウサイズが効果的な学習に十分であり、ウィンドウサイズを動的に調整するという追加の複雑さがそれほど大きな利益をもたらさない可能性があることを示唆している。
- さらに、LFW あり/なしでの学習中におけるクエリおよびアイテム表現の sparsity 進化を調査し、LFW が学習初期段階での次元削減を高速化するとともに、より早い安定化を実現することを発見した(付録D.1参照)。

- **リテラル項 vs 拡張項。**
- リテラル項と拡張項の寄与を分析するため、図3でいくつかのバリアントを比較し、以下を発見した。
- (i) リテラル項のみで学習された PROSPERliteral モデルは、強力な BM25 ベースラインを大きく上回り(例: Hit@10 で +9.5 ポイント)、拡張なしでも項の重要度を評価する本モデルの有効性を示している。
- (ii) リテラル項は精度に優れる。
- これは、PROSPERliteral と PROSPERmask-expan が、拡張項のみを用いる対応物の PROSPERexpansion と

- PROSPERmask-lit を Hit@10 や Hit@100 などの指標で大きく上回ることから明らかである。
- (iii) 拡張項は recall を補完するうえで極めて重要である。
- 単独で学習された場合、PROSPERexpansion の Hit@1000 における recall は PROSPERliteral とほぼ一致する。
- さらに説得力のあることに、コンポーネントをマスキングして十分に学習されたモデルを評価すると、拡張項のみのバリアント (PROSPERmask-lit) は Hit@1000 でリテラル項のみのバリアント (PROSPERmask-expan) を凌駕する。

- 要約すると、リテラル項と拡張項は補完的な強みを持つ。
- リテラル項または拡張項のいずれかを単独で使用しても妥当な recall を達成できるが、それぞれに異なる利点があることがわかった。
- PROSPER はこれら2つの側面を巧みに統合することにより、優れた全体性能を実現する。

- **有効性と効率性のトレードオフ。**
- 産業用検索システムの重要な側面は、検索の有効性と計算効率のトレードオフである。
- # FLOPS [13] で計測した計算コストに対するモデル性能 (MRR@10) をプロットして、このトレードオフを評価する。
- この文脈において、# FLOPS はクエリ表現とアイテム表現間の重複項の平均数を表す。
- FLOPS 正則化強度と LFW サイズを調整することで # FLOPS を制御する。
- 図4に示すように、以下を発見した。
- (i) PROSPER と SPLADE はいずれも低い計算コストで強力な性能を達成できるが、PROSPER は一貫してより優れたトレードオフを示す。
- (ii) PROSPER は効率と有効性のバランスにおいて大きな可能性を示す。
- BM25 と比較して、PROSPERliteral と PROSPERmask-expan は同等のコストで検索品質の劇的な改善を達成する。

- さらに、モデルサイズのスケーリングを調査したところ、より大きなモデルでも顕著な性能向上は見られなかった(付録D.3参照)ため、後続のオンライン実験のバックボーンとしては Qwen2.5-1.5B モデルを選択することとした。

- **オフラインケーススタディ。**
- PROSPER がどのように項の拡張と重み付けを最適化するかについて具体的な洞察を提供するため、付録E.1に詳細なオフラインケーススタディを示す。
- 2.2節で言及した2つの例の最適化結果を提示する。
- さらに、付録には拡張および重み付け結果のより包括的な例を含めている。


## 5 オンライン実験

- 本セクションでは、Taobao検索エンジンにおけるPROSPERのデプロイについて紹介し、対応するオンライン評価結果と分析を提示する。

### 5.1 システムデプロイ

- Taobao検索エンジンは「インデックス-検索-ランキング」のパラダイム[29]に従う。
- 図5に示すように、提案するスパース検索モデルPROSPERをTaobao検索エンジンの検索システムにデプロイする。
- 第1段階の商品検索では、PROSPER(学習型スパース検索)と従来の転置インデックス、マルチモーダル検索、生成型検索、密検索、パーソナライズ検索を組み合わせたハイブリッドシステムを採用しており、多様なユーザーニーズを包括的に満たしている。

- PROSPERを第1段階の商品検索にデプロイする際、まず商品コーパスに対してオフライン推論を行い、商品を対応するタームの転置リストに関連付け、重みを保存して転置インデックスを構築する。
- クエリ処理の際には、ユーザークエリをモデルに入力してその表現タームを取得し、それを用いて転置インデックス参照によって関連アイテムを検索する。
- このプロセスでは、効率を最適化するためにBlock-Max Maxscore[10, 29, 36]アルゴリズムを利用する。
- 最終的に、後続のランキング段階のために高い関連性を持つ候補ドキュメント集合を取得する。

### 5.2 オンライン実験設定

- PROSPERの実装にはバックボーンモデルとしてQwen2.5-1.5Bを選択する。
- 学習データの構築では、2025年7月のTaobao検索から約3億3000万件の実ユーザークリック履歴を学習データとしてサンプリングし、1エポックの学習を行う。
- オンライン推論では、商品プールから約8000万件の高品質商品と1億7000万件のユーザークエリに対してオフライン推論を実行する。
- オンラインマッチング効率を最適化するため、検索にはクエリ側から重み上位16タームのみを保持する。

- 推論結果をTaobao検索の実オンライントラフィックバケット(全トラフィックの約1%)にデプロイし、PROSPERをデプロイしない別のオンライントラフィックバケットを比較ベースラインとして使用する。
- 両バケットはPROSPERのデプロイ有無を除いて同一の設定を維持する。
- それ以外の実験設定はオフライン実験と一致させている。

- オンライン評価では、いくつかの重要指標を採用する: 総誘導純流通取引総額(TG-GMV)、直接誘導純流通取引総額(DG-GMV)、純ユニークビジター(UV)、コンバージョン率(CVR)である。
- 直接誘導とは検索直後にユーザーが購入することを指し、総誘導は直接購入、ライブ配信購入、広告誘導購入など複数の購入チャネルを含む。

### 5.3 オンライン実験結果

- **オンラインA/Bテスト結果。**
- 10日間のA/Bテストを実施した結果、PROSPERをデプロイしたバケットはベースラインバケットと比較していくつかの主要指標で有意な改善を示した。
- 詳細な結果は表4に示す。
- これらの主要指標を超えて、その他の指標も良好な傾向を示し、重要なことに、他の段階(ランキング、広告、レコメンドなど)の指標に対する負の影響は見られず、優れたオンライン増分効果を達成した。

<table>
<caption>表4: オンラインA/Bテスト結果</caption>
<tr>
<th>指標</th>
<th>TG-GMV</th>
<th>DG-GMV</th>
<th>UV</th>
<th>CVR</th>
</tr>
<tr>
<td>改善率</td>
<td>+0.64%</td>
<td>+0.28%</td>
<td>+0.19%</td>
<td>+0.22%</td>
</tr>
</table>

- **オンラインケーススタディ。**
- オンライン指標に加えて、オンライン環境においてPROSPERによってリコールされた商品のケースも分析する。
- 広範なケース分析を通じて、PROSPERは相当数の独自リコール結果を示し、他の検索手法ではリコールされなかったがTaobao社内のクエリ-ドキュメント関連性分析モデルによる評価でユーザーニーズに関連すると判断された商品を効果的に補完していることが分かった(詳細なオンラインケーススタディについては付録E.2を参照)。
- これは、PROSPERがリコール性能を効果的に補完し、検索エンジンがユーザーニーズをより良く満たすことを可能にしていることを示している。

## 6 結論

- 本論文では、商品検索における学習型スパース検索 (learned sparse retrieval) への LLM の応用を探究した。
- LRN と LFW を通じて、提案する PROSPER フレームワークは語彙拡張のハルシネーションと学習初期化の課題に効果的に対処し、オフラインおよびオンラインの実験結果の双方で改善を達成した。

- **限界と今後の課題.**
- PROSPER は十分な性能を発揮するものの、モデルのロジットを直接利用して語の拡張と重み付けを行う方式では、依然として一部のノイズ語が混入することは避けられない。
- 今後の研究では、CoT [49] 推論を取り入れて拡張語をフィルタリング・洗練する手法を検討する予定である。
- さらに、商品検索パイプラインのランキング段階における学習型スパース検索の応用についても調査し、スパース表現が多段階検索アーキテクチャをいかに強化できるかを探究していく。

## 参考文献

[1] 2021. 35 A Statistical Interpretation of Term Specificity and Its Application in
Retrieval (1972). 339-347.

[2] Yang Bai, Xiaoguang Li, Gang Wang, Chaoliang Zhang, Lifeng Shang, Jun Xu,
Zhaowei Wang, Fangshan Wang, and Qun Liu. 2020. SparTerm: Learning Term-
based Sparse Representation for Fast Text Retrieval. arXiv:2010.00768 [cs] doi:10.
48550/arXiv.2010.00768

[3] Payal Bajaj, Daniel Campos, Nick Craswell, Li Deng, Jianfeng Gao, Xiaodong
Liu, Rangan Majumder, Andrew McNamara, Bhaskar Mitra, Tri Nguyen, Mir
Rosenberg, Xia Song, Alina Stoica, Saurabh Tiwary, and Tong Wang. 2018.
MS MARCO: A Human Generated MAchine Reading COmprehension Dataset.
arXiv:1611.09268 [cs.CL] https://arxiv.org/abs/1611.09268

[4] Parishad BehnamGhader, Vaibhav Adlakha, Marius Mosbach, Dzmitry Bahdanau,
Nicolas Chapados, and Siva Reddy. 2024. LLM2Vec: Large Language Models Are
Secretly Powerful Text Encoders. arXiv:2404.05961 [cs] doi:10.48550/arXiv.2404.
05961

[5] Zhuyun Dai and Jamie Callan. 2019. Context-Aware Sentence/Passage Term
Importance Estimation For First Stage Retrieval. arXiv:1910.10687 [cs.IR] https:
//arxiv.org/abs/1910.10687

[6] Zhuyun Dai and Jamie Callan. 2019. Deeper Text Understanding for IR with
Contextual Neural Language Modeling. In Proceedings of the 42nd International
ACM SIGIR Conference on Research and Development in Information Retrieval
(Paris, France) (SIGIR'19). Association for Computing Machinery, New York, NY,
USA, 985-988. doi:10.1145/3331184.3331303

[7] Zhuyun Dai and Jamie Callan. 2020. Context-Aware Document Term Weight-
ing for Ad-Hoc Search. In Proceedings of The Web Conference 2020 (Taipei, Tai-
wan) (WWW '20). Association for Computing Machinery, New York, NY, USA,
1897-1907. doi:10.1145/3366423.3380258

[8] Zhuyun Dai and Jamie Callan. 2020. Context-Aware Term Weighting For First
Stage Passage Retrieval. In Proceedings of the 43rd International ACM SIGIR Con-
ference on Research and Development in Information Retrieval (Virtual Event,
China) (SIGIR '20). Association for Computing Machinery, New York, NY, USA,
1533-1536. doi:10.1145/3397271.3401204

[9] Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. 2019. BERT:
Pre-training of Deep Bidirectional Transformers for Language Understanding. In
Proceedings of the 2019 Conference of the North American Chapter of the Association
for Computational Linguistics: Human Language Technologies, Volume 1 (Long and
Short Papers), Jill Burstein, Christy Doran, and Thamar Solorio (Eds.). Association
for Computational Linguistics, Minneapolis, Minnesota, 4171-4186. doi:10.18653/
v1/N19-1423

[10] Constantinos Dimopoulos, Sergey Nepomnyachiy, and Torsten Suel. 2013. Opti-
mizing top-k document retrieval strategies for block-max indexes. In Proceedings
of the Sixth ACM International Conference on Web Search and Data Mining (Rome,
Italy) (WSDM '13). Association for Computing Machinery, New York, NY, USA,
113-122. doi:10.1145/2433396.2433412

[11] Thibault Formal, Carlos Lassance, Benjamin Piwowarski, and Stéphane Clinchant.
2021. SPLADE v2: Sparse Lexical and Expansion Model for Information Retrieval.
arXiv:2109.10086 [cs] doi:10.48550/arXiv.2109.10086

[12] Thibault Formal, Carlos Lassance, Benjamin Piwowarski, and Stéphane Clinchant.
2022. From Distillation to Hard Negative Sampling: Making Sparse Neural
IR Models More Effective. In Proceedings of the 45th International ACM SIGIR
Conference on Research and Development in Information Retrieval (Madrid, Spain)
(SIGIR '22). Association for Computing Machinery, New York, NY, USA, 2353-2359.
doi:10.1145/3477495.3531857

[13] Thibault Formal, Benjamin Piwowarski, and Stéphane Clinchant. 2021. SPLADE:
Sparse Lexical and Expansion Model for First Stage Ranking. In Proceedings
of the 44th International ACM SIGIR Conference on Research and Development
in Information Retrieval (Virtual Event, Canada) (SIGIR '21). Association for
Computing Machinery, New York, NY, USA, 2288-2292. doi:10.1145/3404835.
3463098

[14] Luyu Gao and Jamie Callan. 2021. Condenser: A Pre-training Architecture for
Dense Retrieval. In Proceedings of the 2021 Conference on Empirical Methods in
Natural Language Processing, Marie-Francine Moens, Xuanjing Huang, Lucia
Specia, and Scott Wen-tau Yih (Eds.). Association for Computational Linguistics,
Online and Punta Cana, Dominican Republic, 981-993. doi:10.18653/v1/2021.
emnlp-main.75

[15] Luyu Gao and Jamie Callan. 2022. Unsupervised Corpus Aware Language Model
Pre-training for Dense Passage Retrieval. In Proceedings of the 60th Annual Meeting
of the Association for Computational Linguistics (Volume 1: Long Papers), Smaranda
Muresan, Preslav Nakov, and Aline Villavicencio (Eds.). Association for Computa-
tional Linguistics, Dublin, Ireland, 2843-2853. doi:10.18653/v1/2022.acl-long.203

[16] Luyu Gao, Xueguang Ma, Jimmy Lin, and Jamie Callan. 2022. Tevatron: An
Efficient and Flexible Toolkit for Dense Retrieval. arXiv:2203.05765 [cs.IR] https:
//arxiv.org/abs/2203.05765

[17] Jiafeng Guo, Yingiong Cai, Yixing Fan, Fei Sun, Ruqing Zhang, and Xueqi Cheng.
2022. Semantic Models for the First-stage Retrieval: A Comprehensive Review.
ACM Transactions on Information Systems 40, 4 (2022), 1-42. arXiv:2103.04831 [cs]

doi:10.1145/3486250

[18]
Sebastian Hofstätter, Sheng-Chieh Lin, Jheng-Hong Yang, Jimmy Lin, and Allan
Hanbury. 2021. Efficiently Teaching an Effective Dense Retriever with Balanced
Topic Aware Sampling. In Proceedings of the 44th International ACM SIGIR Confer-
ence on Research and Development in Information Retrieval (Virtual Event, Canada)
(SIGIR '21). Association for Computing Machinery, New York, NY, USA, 113-122.
doi:10.1145/3404835.3462891

[19] Sebastian Hofstätter, Sophia Althammer, Michael Schröder, Mete Sertkan, and
Allan Hanbury. 2021. Improving Efficient Neural Ranking Models with Cross-
Architecture Knowledge Distillation. arXiv:2010.02666 [cs.IR] https://arxiv.org/
abs/2010.02666

[20] Gautier Izacard, Mathilde Caron, Lucas Hosseini, Sebastian Riedel, Piotr Bo-
janowski, Armand Joulin, and Edouard Grave. 2022. Unsupervised Dense
Information Retrieval with Contrastive Learning. arXiv:2112.09118 [cs.IR]
https://arxiv.org/abs/2112.09118

[21] Jeff Johnson, Matthijs Douze, and Hervé Jégou. 2021. Billion-Scale Similarity
Search with GPUs. IEEE Transactions on Big Data 7, 3 (2021), 535-547. doi:10.
1109/TBDATA.2019.2921572

[22] Vladimir Karpukhin, Barlas Oguz, Sewon Min, Patrick Lewis, Ledell Wu, Sergey
Edunov, Danqi Chen, and Wen-tau Yih. 2020. Dense Passage Retrieval for Open-
Domain Question Answering. In Proceedings of the 2020 Conference on Empirical
Methods in Natural Language Processing (EMNLP), Bonnie Webber, Trevor Cohn,
Yulan He, and Yang Liu (Eds.). Association for Computational Linguistics, Online,
6769-6781. doi:10.18653/v1/2020.emnlp-main.550

[23]
Omar Khattab and Matei Zaharia. 2020. ColBERT: Efficient and Effective Passage
Search via Contextualized Late Interaction over BERT. In Proceedings of the 43rd
International ACM SIGIR Conference on Research and Development in Information
Retrieval (Virtual Event, China) (SIGIR '20). Association for Computing Machinery,
New York, NY, USA, 39-48. doi:10.1145/3397271.3401075

24] Weize Kong, Jeffrey M. Dudek, Cheng Li, Mingyang Zhang, and Michael Ben-
dersky. 2023. SparseEmbed: Learning Sparse Lexical Representations with Con-
textual Embeddings for Retrieval. In Proceedings of the 46th International ACM
SIGIR Conference on Research and Development in Information Retrieval (Taipei,
Taiwan) (SIGIR '23). Association for Computing Machinery, New York, NY, USA,
2399-2403. doi:10.1145/3539618.3592065

25] Weize Kong, Jeffrey M. Dudek, Cheng Li, Mingyang Zhang, and Michael Ben-
dersky. 2023. SparseEmbed: Learning Sparse Lexical Representations with Con-
textual Embeddings for Retrieval. In Proceedings of the 46th International ACM
SIGIR Conference on Research and Development in Information Retrieval (SIGIR
'23). Association for Computing Machinery, New York, NY, USA, 2399-2403.
doi:10.1145/3539618.3592065

[26] Chankyu Lee, Rajarshi Roy, Mengyao Xu, Jonathan Raiman, Mohammad Shoeybi,
Bryan Catanzaro, and Wei Ping. 2025. NV-Embed: Improved Techniques for
Training LLMs as Generalist Embedding Models. arXiv:2405.17428 [cs] doi:10.
48550/arXiv.2405.17428

[27] Yibin Lei, Liang Ding, Yu Cao, Changtong Zan, Andrew Yates, and Dacheng
Tao. 2023. Unsupervised Dense Retrieval with Relevance-Aware Contrastive
Pre-Training. In Findings of the Association for Computational Linguistics: ACL
2023, Anna Rogers, Jordan Boyd-Graber, and Naoaki Okazaki (Eds.). Association
for Computational Linguistics, Toronto, Canada, 10932-10940. doi:10.18653/v1/
2023.findings-acl.695

[28] Minghan Li, Sheng-Chieh Lin, Xueguang Ma, and Jimmy Lin. 2023. SLIM: Sparsi-
fied Late Interaction for Multi-Vector Retrieval with Inverted Indexes. In Proceed-
ings of the 46th International ACM SIGIR Conference on Research and Development
in Information Retrieval (Taipei, Taiwan) (SIGIR '23). Association for Computing
Machinery, New York, NY, USA, 1954-1959. doi:10.1145/3539618.3591977

[29] Sen Li, Fuyu Lv, Ruqing Zhang, Dan Ou, Zhixuan Zhang, and Maarten de Rijke.
2024. Text Matching Indexers in Taobao Search. In Proceedings of the 30th ACM
SIGKDD Conference on Knowledge Discovery and Data Mining (Barcelona, Spain)
(KDD '24). Association for Computing Machinery, New York, NY, USA, 5339-5350.
doi:10.1145/3637528.3671654

[30] Sheng-Chieh Lin, Jheng-Hong Yang, and Jimmy Lin. 2021. In-Batch Negatives
for Knowledge Distillation with Tightly-Coupled Teachers for Dense Retrieval.
In Proceedings of the 6th Workshop on Representation Learning for NLP (RepL4NLP-
2021), Anna Rogers, Iacer Calixto, Ivan Vulić, Naomi Saphra, Nora Kassner,
Oana-Maria Camburu, Trapit Bansal, and Vered Shwartz (Eds.). Association for
Computational Linguistics, Online, 163-173. doi:10.18653/v1/2021.repl4nlp-1.17

[31] Zheng Liu, Chaofan Li, Shitao Xiao, Yingxia Shao, and Defu Lian. 2024. Llama2Vec:
Unsupervised Adaptation of Large Language Models for Dense Retrieval. In
Proceedings of the 62nd Annual Meeting of the Association for Computational Lin-
guistics (Volume 1: Long Papers) (Bangkok, Thailand, 2024-08), Lun-Wei Ku, Andre
Martins, and Vivek Srikumar (Eds.). Association for Computational Linguistics,
3490-3500. doi:10.18653/v1/2024.acl-long.191

[32] Dingkun Long, Qiong Gao, Kuan Zou, Guangwei Xu, Pengjun Xie, Ruijie Guo, Jian
Xu, Guanjun Jiang, Luxi Xing, and Ping Yang. 2022. Multi-CPR: A Multi Domain
Chinese Dataset for Passage Retrieval. In Proceedings of the 45th International
ACM SIGIR Conference on Research and Development in Information Retrieval
(Madrid, Spain) (SIGIR '22). Association for Computing Machinery, New York,

NY, USA, 3046-3056. doi:10.1145/3477495.3531736

[33] Ilya Loshchilov and Frank Hutter. 2019. Decoupled Weight Decay Regularization.
arXiv:1711.05101 [cs.LG] https://arxiv.org/abs/1711.05101

[34] Xueguang Ma, Liang Wang, Nan Yang, Furu Wei, and Jimmy Lin. 2024. Fine-
Tuning LLAMA for Multi-Stage Text Retrieval. In Proceedings of the 47th Interna-
tional ACM SIGIR Conference on Research and Development in Information Retrieval
(Washington DC, USA) (SIGIR '24). Association for Computing Machinery, New
York, NY, USA, 2421-2425. doi:10.1145/3626772.3657951

[35]
Sean MacAvaney, Franco Maria Nardini, Raffaele Perego, Nicola Tonellotto, Nazli
Goharian, and Ophir Frieder. 2020. Expansion via Prediction of Importance with
Contextualization. In Proceedings of the 43rd International ACM SIGIR Conference
on Research and Development in Information Retrieval (Virtual Event, China) (SIGIR
'20). Association for Computing Machinery, New York, NY, USA, 1573-1576.
doi:10.1145/3397271.3401262

[36] Antonio Mallia, Torten Suel, and Nicola Tonellotto. 2024. Faster Learned Sparse
Retrieval with Block-Max Pruning. arXiv:2405.01117 [cs.IR] https://arxiv.org/
abs/2405.01117

[37]
Hieu Man, Nghia Trung Ngo, Franck Dernoncourt, and Thien Huu Nguyen.
2024. ULLME: A Unified Framework for Large Language Model Embeddings
with Generation-Augmented Learning. In Proceedings of the 2024 Conference
on Empirical Methods in Natural Language Processing: System Demonstrations,
Delia Irazu Hernandez Farias, Tom Hope, and Manling Li (Eds.). Association for
Computational Linguistics, Miami, Florida, USA, 230-239. doi:10.18653/v1/2024.
emnlp-demo.24

[38]
] Shervin Minaee, Tomas Mikolov, Narjes Nikzad, Meysam Chenaghlu, Richard
Socher, Xavier Amatriain, and Jianfeng Gao. 2025. Large Language Models: A
Survey. arXiv:2402.06196 [cs.CL] https://arxiv.org/abs/2402.06196

9] Rodrigo Nogueira, Zhiying Jiang, Ronak Pradeep, and Jimmy Lin. 2020. Docu-
ment Ranking with a Pretrained Sequence-to-Sequence Model. In Findings of the
Association for Computational Linguistics: EMNLP 2020, Trevor Cohn, Yulan He,
and Yang Liu (Eds.). Association for Computational Linguistics, Online, 708-718.
doi:10.18653/v1/2020.findings-emnlp.63

[40] Rodrigo Nogueira, Wei Yang, Jimmy Lin, and Kyunghyun Cho. 2019. Document
Expansion by Query Prediction. arXiv:1904.08375 [cs.IR] https://arxiv.org/abs/
1904.08375

[41] Biswajit Paria, Chih-Kuan Yeh, Ian E. H. Yen, Ning Xu, Pradeep Ravikumar, and
Barnabás Póczos. 2020. Minimizing FLOPs to Learn Efficient Sparse Representa-
tions. arXiv:2004.05665 [cs.LG] https://arxiv.org/abs/2004.05665

[42]
Yingqi Qu, Yuchen Ding, Jing Liu, Kai Liu, Ruiyang Ren, Wayne Xin Zhao,
Daxiang Dong, Hua Wu, and Haifeng Wang. 2021. RocketQA: An Optimized
Training Approach to Dense Passage Retrieval for Open-Domain Question An-
swering. In Proceedings of the 2021 Conference of the North American Chapter
of the Association for Computational Linguistics: Human Language Technologies,
Kristina Toutanova, Anna Rumshisky, Luke Zettlemoyer, Dilek Hakkani-Tur,
Iz Beltagy, Steven Bethard, Ryan Cotterell, Tanmoy Chakraborty, and Yichao
Zhou (Eds.). Association for Computational Linguistics, Online, 5835-5847.
doi:10.18653/v1/2021.naacl-main.466

[43] Qwen, :, An Yang, Baosong Yang, Beichen Zhang, Binyuan Hui, Bo Zheng, Bowen
Yu, Chengyuan Li, Dayiheng Liu, Fei Huang, Haoran Wei, Huan Lin, Jian Yang,
Jianhong Tu, Jianwei Zhang, Jianxin Yang, Jiaxi Yang, Jingren Zhou, Junyang
Lin, Kai Dang, Keming Lu, Keqin Bao, Kexin Yang, Le Yu, Mei Li, Mingfeng Xue,
Pei Zhang, Qin Zhu, Rui Men, Runji Lin, Tianhao Li, Tianyi Tang, Tingyu Xia,
Xingzhang Ren, Xuancheng Ren, Yang Fan, Yang Su, Yichang Zhang, Yu Wan,
Yuqiong Liu, Zeyu Cui, Zhenru Zhang, and Zihan Qiu. 2025. Qwen2.5 Technical
Report. arXiv:2412.15115 [cs.CL] https://arxiv.org/abs/2412.15115

[44] Stephen Robertson and Hugo Zaragoza. 2009. The Probabilistic Relevance Frame-
work: BM25 and Beyond. Found. Trends Inf. Retr. 3, 4 (April 2009), 333-389.
doi:10.1561/1500000019

[45] Jacob Mitchell Springer, Suhas Kotha, Daniel Fried, Graham Neubig, and
Aditi Raghunathan. 2024. Repetition Improves Language Model Embeddings.
arXiv:2402.15449 [cs] doi:10.48550/arXiv.2402.15449

[46] Chongyang Tao, Tao Shen, Shen Gao, Junshuo Zhang, Zhen Li, Zhengwei Tao,
and Shuai Ma. 2024. LLMs Are Also Effective Embedding Models: An In-depth
Overview. arXiv:2412.12591 [cs] doi:10.48550/arXiv.2412.12591

[47]
Aaron van den Oord, Yazhe Li, and Oriol Vinyals. 2019. Representation Learning
with Contrastive Predictive Coding. arXiv:1807.03748 [cs.LG] https://arxiv.org/
abs/1807.03748

[48] Liang Wang, Nan Yang, Xiaolong Huang, Linjun Yang, Rangan Majumder, and
Furu Wei. 2024. Improving Text Embeddings with Large Language Models. In
Proceedings of the 62nd Annual Meeting of the Association for Computational
Linguistics (Volume 1: Long Papers), Lun-Wei Ku, Andre Martins, and Vivek
Srikumar (Eds.). Association for Computational Linguistics, Bangkok, Thailand,
11897-11916. doi:10.18653/v1/2024.acl-long.642

[49] Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Brian Ichter, Fei
Xia, Ed H. Chi, Quoc V. Le, and Denny Zhou. 2022. Chain-of-thought prompting
elicits reasoning in large language models. In Proceedings of the 36th International
Conference on Neural Information Processing Systems (New Orleans, LA, USA)
(NIPS '22). Curran Associates Inc., Red Hook, NY, USA, Article 1800, 14 pages.

## LLMs as Sparse Retrievers: A Framework for First-Stage Product Search

[50] Shitao Xiao, Zheng Liu, Peitian Zhang, and Niklas Muennighoff. 2023.
C-Pack: Packaged Resources To Advance General Chinese Embedding.
arXiv:2309.07597 [cs.CL]

[51] Lee Xiong, Chenyan Xiong, Ye Li, Kwok-Fung Tang, Jialin Liu, Paul Bennett,
Junaid Ahmed, and Arnold Overwijk. 2020. Approximate Nearest Neighbor
Negative Contrastive Learning for Dense Text Retrieval. arXiv:2007.00808 [cs.IR]
https://arxiv.org/abs/2007.00808

[52] Zhichao Xu, Aosong Feng, Yijun Tian, Haibo Ding, and Lin Lee Cheong.
2025. CSPLADE: Learned Sparse Retrieval with Causal Language Models.
arXiv:2504.10816 [cs] doi:10.48550/arXiv.2504.10816

[53] Hamed Zamani, Mostafa Dehghani, W. Bruce Croft, Erik Learned-Miller, and
Jaap Kamps. 2018. From Neural Re-Ranking to Neural Ranking: Learning a
Sparse Representation for Inverted Indexing. In Proceedings of the 27th ACM
International Conference on Information and Knowledge Management (Torino,

Italy) (CIKM '18). Association for Computing Machinery, New York, NY, USA,
497-506. doi:10.1145/3269206.3271800

[54] Hansi Zeng, Julian Killingback, and Hamed Zamani. 2025. Scaling Sparse and
Dense Retrieval in Decoder-Only LLMs. arXiv:2502.15526 [cs] doi:10.48550/arXiv.
2502.15526

[55] Tiancheng Zhao, Xiaopeng Lu, and Kyusong Lee. 2021. SPARTA: Efficient Open-
Domain Question Answering via Sparse Transformer Matching Retrieval. In
Proceedings of the 2021 Conference of the North American Chapter of the Association
for Computational Linguistics: Human Language Technologies, Kristina Toutanova,
Anna Rumshisky, Luke Zettlemoyer, Dilek Hakkani-Tur, Iz Beltagy, Steven
Bethard, Ryan Cotterell, Tanmoy Chakraborty, and Yichao Zhou (Eds.). Associa-
tion for Computational Linguistics, Online, 565-575. doi:10.18653/v1/2021.naacl-
main.47

## A 問題定義

- 商品検索において、第 1 段階の検索の目的は、ユーザクエリに関連する商品をできるだけ多く再現 (recall) し、後続のランキング段階の候補集合として提供することである。
- 形式的には、商品検索における第 1 段階検索タスクは次のように定義される。
- クエリ集合 $Q = \{q_1, q_2, \ldots, q_m\}$ と商品データベース $I = \{d_1, d_2, \ldots, d_n\}$ が与えられ、各クエリ $q_i$ に対してデータベースは関連商品アイテム集合 $I_{q_i} \subseteq I$ を含むものとする。
- 検索モデルは、各クエリ $q_i$ について商品データベース $I$ から上位 $k$ 件の検索結果 $R_i = \{d_{r_1}, d_{r_2}, \ldots, d_{r_k}\}$ を返す必要があり、その目的は関連商品集合 $I_{q_i}$ からできるだけ多くの商品を検索して高い再現率を達成することである。
- クエリ集合全体での平均再現率は次のように定義される:

$$
\mathrm{Recall} = \frac{1}{|\mathcal{Q}|} \sum_{i=1}^{|\mathcal{Q}|} \frac{|R_i \cap I_{q_i}|}{|I_{q_i}|} \tag{14}
$$

- ここで $|R_i \cap I_{q_i}|$ はクエリ $q_i$ の検索結果に含まれる関連商品の数を表し、 $|I_{q_i}|$ はクエリ $q_i$ に対する関連商品の総数を表す。

## B 関連研究

- **Dense retrieval.**
- ニューラルネットワークの強力な表現能力を活用して、密検索モデルはテキストを密な埋め込みにマッピングすることで優れた検索性能を実現しており、学術界・産業界の双方から幅広い注目を集めている [9, 14, 17, 22]。
- DPR [22] は BERT [9] を用いた dual-encoder アーキテクチャを導入し、文書のオフラインエンコーディングによる効率的な検索を可能にした。
- 一方、ColBERT [23] はトークンレベルでの後期相互作用 (late interaction) によって有効性を高めた。
- さらに教師なし事前学習 [15, 20, 27]、ハードネガティブマイニング [51]、知識蒸留 [18, 19] などの進展により、密検索モデルの性能は継続的に向上してきた。
- 近年、研究者たちは検索タスクにおける LLM の可能性を探り始めている [26, 31, 37, 46, 48]。
- しかし LLM は因果的アテンション機構を用いており、各トークンはシーケンス内の前のトークンにしかアテンドできないため、包括的なテキスト表現を学習する能力が制限される。
- これに対処するため、LLM2Vec [4] と NV-Embed [26] は適応学習を伴う双方向アテンションを導入し、Echo embedding [45] は入力を複製することでトークンを完全な文脈に晒した。
- しかしながら、密な埋め込みは完全なブラックボックスである不透明性と高いインデックス記憶コストを抱えており、大規模な産業応用には課題がある。

- **Sparse retrieval.**
- 疎検索 [1, 13, 44] は、明示的な単語レベルのシグナルに基づいて関連度を計算する。
- BM25 [44] のような古典的なモデルは統計的な単語重み付けと転置インデックスに依存し、その効率性とロバスト性により強力なベースラインを提供する。
- より豊かな意味を捉えるため、学習型の疎検索手法はニューラルネットワークを取り入れて単語により情報量の多い重みを割り当てる [5-8, 53]。
- しかし、これらの手法は依然として字義的な単語の重複に大きく依存している。
- クエリと文書の間には大きな長さの非対称性があるため、語彙のミスマッチが恒常的に発生する。

- これに対処するため、一部の手法では重み付けに加えて単語拡張も行ったが [35, 39, 40, 55]、その性能は密モデルに後れを取っていた。
- SPLADE [13] は SparTerm [2] をベースに、単語重みのプーリング戦略を最適化し、疎化のために FLOPS 損失 [41] を導入した。
- 後のバージョンではハードネガティブと蒸留が追加され、パッセージ検索において密モデル並みの性能を達成し [11, 12]、さらに後続研究はクエリと文書の細粒度な相互作用を探求している [24, 25, 28]。
- SPLADE と近年の LLM ベースの密検索に触発され、研究者は LLM を疎検索に適応させる試みを始めている。
- Zeng ら [54] は LLM ベースの疎検索器のスケーリング則を研究し、CSPLADE [52] は NV-Embed [26] と Echo embedding [45] を基盤として、SPLADE [13] を LLM に適用する際のアテンション関連の課題に取り組んだ。
- しかし、モデルバックボーンの置き換えを除けば、これらの研究の中核的な方法論は依然として SPLADE と類似しており、商品検索ドメインへの汎化性は確認されていない。

## C 実験設定の詳細

### C.1 データセット詳細

- 評価データセットの詳細は以下の通りです:

- · Multi-CPR E-commerce [32]。
- Multi-CPR は公開されている多分野の中国語パッセージ検索データセットです。
- 本実験では、Taobao 上の実世界の検索シナリオから取得された E-commerce サブセットを利用します。
- このサブセットは 100 万件以上のパッセージから成るコーパスを含み、そのうち 10 万件のクエリ-パッセージ対を訓練セットとして、1,000 件のクエリをテストセットとして使用します。
- 訓練セットおよびテストセットの各クエリは、人手でアノテーションされた単一の正例アイテムと対応付けられており、一対一の対応が保証されています。

- · Taobao-Internal。
- 本手法を実世界の産業環境でさらに検証するために、2025年6月の Taobao Search の実ユーザクリックログから約 107 万件のクエリ-アイテム対をサンプリングして新規データセットを構築しました。
- ユーザクリックを関連性の正解 (ground truth) とみなします。
- 本データセットでは、1 つのクエリに対して 1 件から 10 件のクリックされたアイテムが対応する場合があります。
- 27 万件のクエリ-アイテム対からなる訓練セットと、1,000 件のクエリおよびそれに対応するクリック済みアイテムからなるテストセットを作成しました。

- Qwen-2.5-3B トークナイザによりトークナイズした後の詳細なトークン長統計を Table 5 に示します。
- 表に示すように、

<table>
<caption>Table 5: データセットの完全なトークン長統計。</caption>
<tr>
<th rowspan="2">データセット</th>
<th colspan="3">クエリ長</th>
<th colspan="3">アイテム長</th>
</tr>
<tr>
<th>最小</th>
<th>平均</th>
<th>最大</th>
<th>最小</th>
<th>平均</th>
<th>最大</th>
</tr>
<tr>
<td>Multi-CPR</td>
<td>1</td>
<td>5</td>
<td>23</td>
<td>2</td>
<td>25</td>
<td>92</td>
</tr>
<tr>
<td>Taobao-Internal</td>
<td>2</td>
<td>6</td>
<td>25</td>
<td>2</td>
<td>25</td>
<td>74</td>
</tr>
</table>

- クエリとアイテムの平均長は短くなっています。
- これは、本研究のバックボーンである Qwen-2.5-3B の語彙サイズが 150,000 を超えることと対比すると特に顕著であり、本タスクの極端なスパース性を浮き彫りにしています。

### C.2 実装詳細

- バックボーンモデルには Qwen2.5 [43] を採用し、その 1.5B、3B、7B 版で実験を行います。
- 特に断りのない限り、デフォルトのバックボーンは Qwen2.5-3B です。
- lexical focusing window については、デフォルトサイズを kq = 256、kd = 512 とします。
- 動的ウィンドウのバリアントでは、クエリに対して (256, 128, 64)、アイテムに対して (512, 256, 128) のサイズを使用します。
- 動的ウィンドウ戦略は訓練中に適応的にウィンドウサイズを縮小します。
- 具体的には、クエリまたはアイテムの 90% 以上について活性化次元数が現在のウィンドウサイズを下回った時点で、ウィンドウは自動的に系列内の次に小さいサイズへ縮小されます。
- この適応的メカニズムにより、lexical focusing window は実際にデータ中で観測されるスパース性パターンに対して常に適切なサイズに保たれ、訓練中に表現が自然にスパース化していく際の過剰な制約を防止します。
- クエリおよびアイテムの最大系列長は 64 に設定しますが、入力が重複するため PROSPERecho-emb のみ 128 とします。
- ベースラインについては、密ベクトル検索器 (dense retriever) は Tevatron [16] ライブラリを用いて訓練し、インデックス構築と検索は Faiss [21] により処理します。
- スパース検索器は格納と照合に Taobao 内部のデータベースを使用します。
- BM25 ベースラインには標準的なハイパーパラメータ k1 = 1.2、b = 0.75、平滑化パラメータ δ = 0.25 を使用します。

- すべてのモデルは、両データセットにおいて 8 基の NVIDIA H20 96GB GPU を用いて 5 エポック訓練します。
- 各データセットについて、訓練セットから 500 件のクエリをランダムサンプリングして検証セットを構成し、各エポック後にモデル性能の評価に使用します。
- 最終モデルは検証セット上で最も性能の良いものを選択します。
- 学習率は 3e-5 とし、約 0.3 エポックの線形ウォームアップを行い、デバイスあたりのバッチサイズは 64 とします。
- 最適化アルゴリズムには AdamW [33] を使用し、weight decay は 0.1 とします。
- FLOPS 正則化パラメータ Aq および Ad もそれぞれ目標値である 5e-3 と 1e-3 に向けて二次関数的に増加させます (本実験では約 1.5 エポックかけて行います)。

## D 補助実験

### D.1 疎化戦略の分析

- 図6は、LFW が訓練中の疎化プロセスにどのような影響を与えるかについて詳細な分析を提供しており、LFW が訓練の初期段階での迅速な次元削減を可能にし、LFW を用いないモデルと比較してより速い安定化を達成することを示している。
- 粗から密へ (coarse-to-fine) のアプローチにより、初期の次元削減後の細かな調整を FLOPS 正則化が担うことができ、その結果、計算コストを削減しつつ高い意味的品質を維持する、より焦点の絞られた疎な表現が得られる。

### D.2 正規化の影響

- 正規化の影響を分析するため、以下の手法を検証する。
- (i) PROSPERall-norm はクエリベクトルとアイテムベクトルの両方に {2 正規化を適用するもので、スコアリング関数を標準的な cosine similarity と等価にする。
- (ii) PROSPERw/o-norm はすべての正規化を取り除き、標準的な dot product によるスコアとなる。
- (iii) PROSPERd-norm はアイテムベクトルにのみ {2 正規化を適用する。
- (iv) PROSPER{1-norm はクエリベクトルに {1 正規化を適用し、項の重み付けへの効果を探る。

- 表6は、商品検索における類似度関数の重要な役割を明らかにしている。
- 商品検索には非対称的なアプローチが必要である。
- すなわち、クエリにはユーザーの意図を捉えるための正確な項の表現が必要であり、一方でアイテムには多様なクエリにマッチするための豊富な意味的カバレッジが必要となる。
- 本分析は、クエリ表現にのみ {2 正規化を適用することが、クエリ項の相対的な重要度を強調しつつアイテム項の絶対的な重みを保持するという点で、このバランスを完璧に達成することを示している。
- この非対称的なアプローチは、すべての変種を大幅に上回る。
- 標準的な dot product (PROSPERw/o-norm) と cosine similarity (PROSPERall-norm) はこの本質的な非対称性に対処できず、{1 正規化 (PROSPER{1-norm) は重みの総和が 1 になることを強制するため過剰な疎化を引き起こす。
- 興味深いことに、アイテム表現のみを正規化する場合 (PROSPERd-norm) も性能が劣り、アイテムの絶対的な重みを保持することが本質的に重要であることを裏付けている。

<table>
<caption>表6: 異なる類似度関数が検索性能に与える影響。</caption>
<tr>
<th>Variant</th>
<th>Hit@1</th>
<th>Hit@10</th>
<th>Hit@100</th>
<th>Hit@1000</th>
</tr>
<tr>
<td>PROSPER</td>
<td>25.3</td>
<td>50.7</td>
<td>78.1</td>
<td>93.9</td>
</tr>
<tr>
<td>PROSPER 1-norm</td>
<td>15.8</td>
<td>39.9</td>
<td>68.0</td>
<td>90.0</td>
</tr>
<tr>
<td>PROSPER w/o-norm</td>
<td>17.0</td>
<td>40.9</td>
<td>68.0</td>
<td>90.0</td>
</tr>
<tr>
<td>PROSPER all-norm</td>
<td>17.1</td>
<td>39.7</td>
<td>67.2</td>
<td>87.2</td>
</tr>
<tr>
<td>PROSPER d-norm</td>
<td>16.1</td>
<td>42.3</td>
<td>71.7</td>
<td>91.1</td>
</tr>
</table>

### D.3 パラメータスケーリング

- モデルサイズの影響を調査するため、1.5B、3B、7B の 3 つの異なる規模の Qwen2.5 バックボーンを用いて PROSPER の実験を行う。
- 図7に示すように、本タスクには明確なスケーリング則は見られない。
- より大きなモデルではある程度の性能向上が得られるものの、重要な Hit@1000 の再現率指標における性能はすべての規模でほぼ同等である。
- したがって、後続のオンライン実験では、有効性とデプロイメントコストの間で最適なトレードオフを実現するため、Qwen2.5-1.5B モデルを大規模オンラインテストのバックボーンとして使用する。

## E ケーススタディ

- 本セクションでは、現実世界のシナリオにおける PROSPER の有効性を示すために、オフラインおよびオンラインの両方のケーススタディを提示する。
- オフラインケーススタディでは、用語拡張と重み付けの最適化結果を分析し、オンラインケーススタディでは、Taobao 検索のマルチチャネル検索システムにおいて発見された排他的なリコール結果を検証する。

### E.1 オフラインケーススタディ

- PROSPER が用語拡張と重み付けをどのように最適化するかについて具体的な洞察を提供するため、予備セクションで言及した 2 つの例について最適化結果を示す詳細なケーススタディを提示する。
- Table 7 は、"爱立舍机油滤芯"(Elysee oil filter)と "老捷豹副水箱"(Old Jaguar water tank)について、用語拡張と重み付けパターンの最適化前後を示している。
- この表は、PROSPER がどのように語彙拡張のハルシネーションを効果的に削減しつつ有用な意味的拡張を維持し、より焦点を絞った関連性の高い用語表現につながるかを示している。
- さらに、Table にはより包括的な拡張と重み付け結果の例が含まれている。
- 加えて、Table 8 にはより多くのオフラインケースも示されている。

### E.2 オンラインケーススタディ

- オンラインのケース分析では、PROSPER によって排他的にリコールされた商品に焦点を当て、検索全体のパフォーマンスへの独自の貢献を強調する。
- このシステムでは、各検索チャネルに固有の識別子が割り当てられており、PROSPER は 8 番目のチャネル(インデックス 7)として指定されている。
- 各商品の検索ソースは "recall_types" と呼ばれるビットマスクを使用して追跡される。
- "recall_types" の値が 2^7 = 128 である場合、その商品は PROSPER のみによってリコールされたことを示す。
- リコールされたアイテムの関連性は、Taobao 内部のクエリ-アイテム関連性モデルによって評価され、"rnr" スコアが付与される: 2 は高度に関連、1 は関連、0 は非関連を示す。
- Table 9 に示すように、"recall_types" と "rnr" はいずれも表内の各商品の下部にある緑色の枠内に注記されている。
- 実際には、各ユーザークエリに対して、PROSPER による排他的なリコール結果が複数あり、また他のチャネルによるマルチチャネルリコール結果も多数存在する。
- 便宜上、表では各サンプルクエリに対して PROSPER による 1 件の排他的リコール結果と、他チャネルからの 2 件のリコール結果を提示する。

- Table 9 のケースで示されているように、他のチャネルが既に強力なリコール性能を示している一般的なクエリの場合でも、それらは関連性の高い商品をいくつか取得できないことがある。
- PROSPER はこれらの欠落したアイテムをリコールすることで、このギャップを効果的に埋める。
- これにより、初期検索段階でユーザーニーズをより包括的に満たし、Taobao 検索エンジンのパフォーマンスを向上させ、プラットフォームの増分オンライン収益に貢献することが保証される。

- Table 7: SPQwen-backbone と PROSPER による用語拡張と重み付け最適化のケーススタディ。
- この表は、2 つの代表的な商品検索クエリに対する最適化前後のトップウェイト用語を示している。
- 用語は重みの降順でランク付けされている。
- リテラル用語は黒、有用な拡張は緑、ノイズの多い拡張は赤で示されている。

<table>
<tr>
<th>Query</th>
<th>Top-Weighted Terms(SPQwen-backbone)</th>
<th>Top-Weighted Terms(PROSPER)</th>
</tr>
<tr>
<td rowspan="2">爱立舍机油滤芯 (Elysee oil filter)</td>
<td>油(oil),滤(filter),芯(core),心(heart), 机(engine), oil, 燃(fuel),柴(diesel),</td>
<td rowspan="2">机油(engine oil),滤(filter),立(Li),爱(Ai), 舍(She),芯(core),过滤(filtration),发动机 (engine),油(oil), filter, 引擎(engine),汽油 (gasoline), oil,保养(maintenance),燃油(fuel)</td>
</tr>
<tr>
<td>筛(sieve),泵(pump),污(dirt), cpu, Machine,舶(ship),脂(fat),爱(love)</td>
</tr>
<tr>
<td>老捷豹副水箱 (Jaguar water tank) 謝 C</td>
<td>箱(tank),豹(Jaguar),水(water), 副(aux),捷(Jaguar),狸(racoon), 豺(jackal), water, 老(old),缸(tank), 虎(tiger),沈(Shen), ford,狮(lion)</td>
<td>水(water),箱(tank),捷(Jie),老(old), 副(auxiliary),豹(leopard),Jaguar,冷却(cooling),散热 (heat dissipation),water,发动机(engine),引擎(engine), 水泵(water pump),路虎(Land Rover)</td>
</tr>
</table>

<table>
<caption>Table 8: PROSPER のオフラインクエリおよびアイテムケース集。この表は、各用語とその英訳を、重みを括弧内に示して提示している。用語は重みの降順でランク付けされている。リテラル用語は黒、有用な拡張は緑、ノイズの多い拡張は赤で示されている。</caption>
<tr>
<th>Query</th>
<th>Top-Weighted Terms(Query)</th>
<th>Rank-1 Item</th>
<th>Top-Weighted Terms(Item)</th>
</tr>
<tr>
<td>新南方电烤箱商用 (New south China electric oven for commercial use)</td>
<td>烤/bake (0.37),电/electric (0.35),箱 /box (0.35),南方/southern 商用 /commercial(0.28),新/new (0.16), 南/south (0.15), Southern (0.13), South (0.13),炉/stove (0.13),灶 Istove (0.12),厨房/kitchen (0.12),广 东/Guangdong (0.12),电器/electrical appliances (0.11),烧烤/bbq (0.11)</td>
<td>新南方烤箱商用电40C二 层四盘大型鸡鸭面包蛋 糕披萨电烘炉大容量 (New South China oven commercial 40C two layers four plates large chicken, duck bread cake pizza electric oven large capacity)</td>
<td>烤/bake (5.50),箱/box(5.37),南方/southern (5.25), 面包/bread (5.21),电/electric (5.06),炉/stove (5.00), 商/business (4.75),蛋糕/cake (4.75),烘/bake (4.62), 四/four (4.34),用电/electricity usage (4.31), C (4.12), 盘/plate (3.79),4(3.65),鸭/duck (3.43),二/two(3.17), 层/layer (3.17),大型/large (3.07),萨/sa (2.98),容量 /capacity (2.98),新/new (2.96),披/pi (2.96),鸡 /chicken(2.87), 大/big (2.85), 0(2.53),南/south (2.32), oven (2.2031), South (2.1719), Southern (2.0625),</td>
</tr>
<tr>
<td>康乃馨编织 (Carnations woven)</td>
<td>编织/knitting (0.50),康/kang (0.33), 馨/xin (0.26), 乃/nai (0.21),花 /flower (0.21),编/weave (0.20),玫瑰 /rose (0.18),鲜花/fresh flower (0.18), 编制/weaving (0.16),9 1 n /flower (0.16),菊花/chrysanthemum (0.14), 花卉/flowers (0.14),花朵/blossom (0.13),編/weave (0.13),工艺/craft (0.13),针/needle (0.12),</td>
<td>康乃馨花束毛线钩针图 解仿真花教程DIY手工制 作礼品摆件装饰 (Carnation bouquet yarn crochet pattern artificial flower tutorial DIY handmade gift decoration)</td>
<td>针/needle (5.69),花/flower (5.53),康/kang(5.19),钩 /hook (5.06),手工/handmade (5.00),线/thread (4.94), 毛/wool (4.91),仿真/artificial (4.88),图/diagram (4.69),馨/xin (4.22),制作/make (4.00),教程/tutorial (3.94),摆/display (3.69),件/piece(3.52),装饰 /decoration (3.44),解/solution (3.00),束/bundle (2.86), 礼品/gift (2.78), DI/DI (2.75), Y/Y (2.56),鲜花/fresh flower (2.45),乃/nai (2.38),玫瑰/rose (2.38)</td>
</tr>
<tr>
<td>皮肤康清洗液 (Skin cleanser)</td>
<td>康/kang (0.44),皮肤/skin (0.40),液 /liquid (0.37),清洗/cleaning (0.34) 洗/wash (0.17),清/clear (0.16),消毒 /disinfect (0.14), disin (0.14), Kon/Kon (0.13),消/eliminate (0.13), ケアIcare (0.12),Clin (0.12),皮肤病 /dermatosis (0.11),临床/clinical (0.11),康复/rehabilitation (0.11),排 毒/detox (0.11),脱/off(0.11)</td>
<td>兆春牌皮肤康清皮肤康 洗液外用私处止痒洗剂 西安康春正品 (Zhaochun brand skin Kangqing skin Kangqing wash external genital itching wash Xi 'an Kangchun genuine product)</td>
<td>康/kang (6.34),皮肤/skin (6.28),春/spring (5.88),牌 /brand (5.44),洗/wash (5.41),剂/agent (5.31),清/clear (5.19),私/private(4.88),液/liquid (4.56),痒/itch (4.53),外/external (4.25),西安/Xi'an (4.13),止/stop (3.91),兆/zhao (3.72),用/use (3.03),处/part (2.81),皮 肤病/dermatosis (2.67)(1),正品/genuine (2.56), skin (2.47),中药/Chinese medicine (2.44), Spring (2.39), Skin (2.39),春季/spring season (2.39),</td>
</tr>
</table>

- Table 9: Taobao のハイブリッド検索システムにおける PROSPER による排他的な商品リコールのオンラインケーススタディ。
- 左列は PROSPER によって排他的にリコールされた商品("recall_types" = 128)を示し、右列は他のチャネルでリコールされた同じクエリの商品を示す。
- "rnr" スコアは関連性レベルを示す。

<table>
<tr>
<th colspan="5">Exclusive Product Recalled by PROSPER</th>
<th colspan="6">Products Recalled by</th>
<th colspan="5">Other Channels</th>
</tr>
<tr>
<th colspan="5" rowspan="7">Query: Full cowhide women's shoes with half a toe TOUCH SHOES ☐ 位置:1 宝贝 ID:893352323 后台叶子类目:50012033(包头 3 278 抱》 全牛皮~半拖鞋女夏外穿2025新款包头英伦风平底穆勒鞋懒人乐福 鞋 rs_score rerank_score ha3_score 商品360 recall_types: 128 rr: 2.0 ¥158.00 ¥508.00 月购买人數:33 总成交量:1063 月收货人数:14</th>
<th></th>
<th colspan="5" rowspan="4">☐ 位置:宝贝 ID:8244642348 后台叶子类目:50012033(包头 4 09 拖) 【现货促销89】 真皮勃肯鞋半拖鞋女春秋外穿厚底博肯鞋包头拖鞋 男</th>
<th rowspan="4"></th>
<th colspan="4" rowspan="4">☐ 位置:宝贝 ID: 9229351052 后台叶子类目:50012033(包头 8 84 拖) 天丽 达芙妮头层牛皮半拖鞋女夏外穿2025新款粗跟女士包头凉拖鞋 ☒ 穆勒鞋 rs_score rerank_score ha3_score 商品360</th>
</tr>
<tr>
<td></td>
</tr>
<tr>
<th></th>
</tr>
<tr>
<th></th>
</tr>
<tr>
<td></td>
<td colspan="2" rowspan="3">rs_score rerank_score recall_types: 4 rnr: 2.0 ¥610.00 ¥610.00 月购买人数:167 总成交量:7320</td>
<td rowspan="2">ha3_score</td>
<td>商品360</td>
<td></td>
<td></td>
<td colspan="3" rowspan="3">recall_types: 516 rnr: 2.0 ¥259.90 ¥328.00 月购买人数:24 总成交量:50 月收货人数:14</td>
<td></td>
</tr>
<tr>
<td>qzt</td>
<td rowspan="2">:102</td>
<td rowspan="2"></td>
<td rowspan="2"></td>
<td rowspan="2"></td>
</tr>
<tr>
<td></td>
<td>月收货人数</td>
</tr>
<tr>
<td colspan="5">Query: Unique beautiful summer purple top</td>
<td>#</td>
<td colspan="3">☐ 位置:宝贝 ID:897034032 后台叶子类</td>
<td>目:50000697(</td>
<td>毛针</td>
<td></td>
<td colspan="4">☐ 位置:宝贝 ID:92684438573 后台叶子类目:</td>
</tr>
<tr>
<th rowspan="6"></th>
<th colspan="4">☐ 位置:1 宝贝 ID:9031549393 后台叶子类目:50000671 (T</th>
<th></th>
<th colspan="3" rowspan="3">1 257 织衫) 紫色正肩冰丝针织v領短袖t女2025夏季掐 衣</th>
<th colspan="2"></th>
<th></th>
<th colspan="4" rowspan="3">2 6 162104 (衬衫) ☒ 天下 法式紫色一字肩衬衫女装夏季2025新款爆款衬衣独特漂亮超好 看上衣</th>
</tr>
<tr>
<th colspan="4">8 41 恤》</th>
<th></th>
<th>腰短款bm</th>
<th>卡通设计感上</th>
<th rowspan="2"></th>
</tr>
<tr>
<th colspan="4">天册 多巴胺超好看紫色宽松显瘦V领短袖T恤女2025夏季独特漂亮掐</th>
<th></th>
<th colspan="2"></th>
</tr>
<tr>
<th>腰上衣</th>
<th></th>
<th></th>
<th></th>
<th></th>
<th>rs_score</th>
<th>rerank_score</th>
<th>ha3_score</th>
<th>商品360</th>
<th></th>
<th></th>
<th>rs_score</th>
<th>rerank_score</th>
<th>ha3_score</th>
<th>商品360</th>
</tr>
<tr>
<td>rs_score</td>
<td>rerank_score</td>
<td>ha3_score</td>
<td>商品360</td>
<td></td>
<td colspan="2" rowspan="3">recall_types: rnr: ¥79.00 ¥199.00 月购买人数:695 总成交量</td>
<td rowspan="2">2.0</td>
<td></td>
<td rowspan="2"></td>
<td rowspan="2"></td>
<td colspan="4" rowspan="3">recall_types: 2 rnr: 2.0 ¥59.90 ¥99.90 月购买人数:122 总成交量:312 月收货人数:49</td>
</tr>
<tr>
<td colspan="4" rowspan="2">recall_types: 128 rnr: 2.0 ¥39.90 ¥75.90 月购买人数:19 总成交量:69 月收货人数:14</td>
<td>qzt</td>
<td></td>
</tr>
<tr>
<td></td>
<td></td>
<td>:1656 月收货人</td>
<td>数:338</td>
<td></td>
<td></td>
</tr>
<tr>
<th colspan="5">Query: A curved, fitted shirt with a lower hem</th>
<th colspan="6" rowspan="3">Sicily ☐ 位置:宝贝 ID:79931969950 后台叶子类目: 1 3 162104(衬衫) 西西里 学院风条纹领带短袖衬衫女夏季修身掐腰减龄弧形下摆_</th>
<th rowspan="3">陽</th>
<th colspan="4" rowspan="2">店 ☐ 位置:宝贝 ID:70741508414 后台叶子类目:50000671 (T 3 3 仙) 【包邮】美式复古Polo领单排扣长袖衬衫女显瘦辣妹弧形下摆短T恤</th>
</tr>
<tr>
<th rowspan="4">VERO MODA - 1. 1</th>
<th colspan="4" rowspan="2">☐ 位置:4 宝贝 ID:89554611387 后台叶子类目: 1 3 162104 (衬衫) ☒ 天記 Vero Moda衬衫2025夏季新款落肩袖针织拼接弧形下摆純棉</th>
</tr>
<tr>
<th colspan="2">rs_score rerank_score</th>
<th>ha3_score</th>
<th>商品360</th>
</tr>
<tr>
<th>325231008</th>
<th></th>
<th></th>
<th></th>
<th></th>
<th>rs_score</th>
<th>rerank_score</th>
<th>ha3_score</th>
<th>商品</th>
<th>360</th>
<th></th>
<th></th>
<th colspan="2" rowspan="2">4 rnr: 2.0</th>
<th></th>
</tr>
<tr>
<td>rs_score</td>
<td>rerank_score</td>
<td>ha3_score</td>
<td>商品360</td>
<td></td>
<td colspan="2">recall_types: 229 rnr:</td>
<td>2.0</td>
<td></td>
<td></td>
<td></td>
<td>recall_types:</td>
<td></td>
</tr>
<tr>
<td rowspan="2">·274" 商场回款 1件之减19%起</td>
<td colspan="4" rowspan="2">recall_types: 128 rnr: 1.0 ¥305.00 ¥549.00 月购买人数:47 总成交量:156 月收货人数:29</td>
<td></td>
<td colspan="3" rowspan="2">¥55.00 ¥55.00 月购买人数:15 总成交量:166 月收货人数</td>
<td></td>
<td></td>
<td rowspan="2"></td>
<td colspan="3" rowspan="2">¥54.99 ¥54.99 月购买人数:0 总成交量:98 月收货人数:0</td>
<td></td>
</tr>
<tr>
<td></td>
<td>:8</td>
<td></td>
<td></td>
</tr>
<tr>
<td colspan="5">Query: Pilates dedicated vest size large</td>
<td colspan="4"></td>
<td colspan="2"></td>
<td></td>
<td colspan="4"></td>
</tr>
<tr>
<th rowspan="5">KOWale 固定胸墊 交叉美背</th>
<th colspan="4" rowspan="2">☐ 位置:1 宝贝 ID:903568720 后台叶子类目:50022890 (健身 6 847 衣)</th>
<th>麥肉女孩</th>
<th colspan="2" rowspan="3">☐ 位置:宝贝 ID:864882294 1 723 胖mm大码运动内衣女高强度文 夏</th>
<th colspan="3" rowspan="3">后台叶子类目:125074041 (运动 胸跑步防震防下垂大胸瑜伽健身背心 文胸)</th>
<th rowspan="3"></th>
<th colspan="4" rowspan="3">☐ 位置:宝贝 ID:851257270 后台叶子类目;125024039(运动 6 348 背心) ☒ 天碗 ARIALEISURE 运动背心女吊带普拉提瑜伽服上衣美背健身运动 内衣</th>
</tr>
<tr>
<td></td>
</tr>
<tr>
<th colspan="4">天猫 瑜伽服女2025新款背心跑步运动健身专业普拉提训练大码上衣 套装夏</th>
<th>高强度 收副乳 100-200FF 4</th>
</tr>
<tr>
<td>rs_score</td>
<td>rerank_score</td>
<td>ha3_score</td>
<td>商品360</td>
<td></td>
<td>rs_score</td>
<td>rerank_score</td>
<td>ha3_score</td>
<td>商品360</td>
<td></td>
<td></td>
<td>rs_score</td>
<td>rerank_score</td>
<td>ha3_score</td>
<td>商品360</td>
</tr>
<tr>
<td colspan="3">recall_types: 128 rnr: 2.0</td>
<td></td>
<td>第2件減10/3件减30/4件減40</td>
<td colspan="2">recall_types: 4 rnr: 2.0</td>
<td></td>
<td></td>
<td>171</td>
<td>189 qzt</td>
<td colspan="3">recall_types: 132 rnr: 2.0</td>
<td></td>
</tr>
<tr>
<td colspan="5">¥39.90 ¥79.90 月购买人数:51 总成交量:364 月收货人数:24</td>
<td></td>
<td colspan="2">¥79.00 ¥150.00 月购买人数:3842 总成交量</td>
<td>:13955 月收货人</td>
<td>数:2689</td>
<td></td>
<td></td>
<td colspan="4">¥189.00 ¥207.00 月购买人数:428 总成交量:2316 月收货人数:269</td>
</tr>
<tr>
<td colspan="5">Query: Mao la is a specialty of Kaili, Guizhou</td>
<td>BAKT</td>
<td colspan="2">位置:宝贝 ID:946788201</td>
<td>后台叶子类目</td>
<td>:50009822(</td>
<td>火锅</td>
<td></td>
<td colspan="4">位置:宝贝 ID:536506562 后台叶子类目:50009822(火锅</td>
</tr>
<tr>
<th rowspan="5">姜蒜糟辣椒</th>
<th colspan="4" rowspan="3">☐ 位置:宝贝 ID:53447154 后台叶子类目:50009827 (辣椒粉 13 8292 料/蘸料) 杜姨妈姜蒜糟辣椒贵州特产酸辣椒剁椒糟辣鱼头调料辣酱凉菜调味 品</th>
<th>人家果肉看得见</th>
<th colspan="2" rowspan="3">☐ 1 780 天福 毛辣果酸汤 【零添加防腐】 ☒ 里特产</th>
<th rowspan="3">酿六月酿三月 调料)</th>
<th colspan="2" rowspan="2">火锅底料正宗酸辣凱</th>
<th rowspan="3"></th>
<th colspan="4" rowspan="3">☐ 2 083 调料) 红酸汤料牛凯里酸汤鱼贵州特产酸毛辣果猪脚火锅底料生肥牛的调 料 rs_score rerank_score ha3_score 商品360</th>
</tr>
<tr>
<td></td>
</tr>
<tr>
<th></th>
<th></th>
<th></th>
</tr>
<tr>
<td>rs_score</td>
<td>rerank_score</td>
<td>ha3_score</td>
<td>商品360</td>
<td>口添加 毛辣果酸汤</td>
<td>rs_score</td>
<td>rerank_score</td>
<td>ha3_score</td>
<td>商品360</td>
<td></td>
<td rowspan="2"></td>
<td colspan="4" rowspan="3">recall_types: 517 rnr: 2.0 ¥10.08 ¥16.80 月购买人数:73 总成交量:29208 月收货人数:56</td>
</tr>
<tr>
<td colspan="3">recall_types: 128 rnr: 1.0</td>
<td></td>
<td>清腐劑 色素 Tai</td>
<td colspan="3">recall_types: 513 rnr: 2.0</td>
<td rowspan="2"></td>
<td rowspan="2"></td>
</tr>
<tr>
<td></td>
<td colspan="4">¥12.00 ¥12.00 月购买人数:14 总成交量:2102 月收货人数:11</td>
<td></td>
<td colspan="3">¥16.80 ¥90.00 月购买人数:37 总成交量:286月收货人数:25</td>
<td></td>
</tr>
<tr>
<td colspan="5">Query: Eucalyptus leaves are everlasting flowers</td>
<td colspan="4"></td>
<td></td>
<td></td>
<td></td>
<td colspan="4"></td>
</tr>
<tr>
<td colspan="5" rowspan="6">☐ 位置:宝贝 ID: 9219426470 后台叶子类目:124496004(永生 4 64 花) 特级永生花花束绣球尤加利叶真花干花高级感玄关客厅通用装饰摆 件 rs_score rerank_score ha3_score 商品360 recall_types: 128 rnr: 2.0 ¥138.00 ¥138.00 月购买人数:11 总成交量:23月收货人数:4</td>
<td></td>
<td colspan="5" rowspan="2">☐ 位置:宝贝 ID:8601335267 后台叶子类目:124496004(永生 1 86 花) 蘭 苹果尤加利叶永生花干花桌面款客厅网红插花基地直发保鲜花 ☒</td>
<td rowspan="2"></td>
<td colspan="4" rowspan="3">☐ 位置:宝贝 ID:739537649 后台叶子类目:124496004(永生 2 954 花) 尤加利叶永生花苹果桉钢钱桉装饰摆设插花配叶软装陈设真树叶干 花</td>
</tr>
<tr>
<td>天</td>
</tr>
<tr>
<td></td>
<td>rs_score</td>
<td>rerank_score</td>
<td>ha3_score 商</td>
<td>品360</td>
<td></td>
<td></td>
</tr>
<tr>
<td></td>
<td colspan="2">recall_types: 644 rnr: 2.0</td>
<td></td>
<td></td>
<td></td>
<td></td>
<td colspan="2">rs_score rerank_score</td>
<td>ha3_score</td>
<td>商品360</td>
</tr>
<tr>
<td colspan="6" rowspan="2">¥9.90 ¥21.90 月购买人数:646 总成交量:4010 月收货人数:495</td>
<td></td>
<td colspan="4" rowspan="2">recall_types: 644 rnr: 2.0 ¥28.80 ¥48:00 月购买人数:58 总成交量:2821 月收货人数:41</td>
</tr>
<tr>
<td></td>
</tr>
</table>
