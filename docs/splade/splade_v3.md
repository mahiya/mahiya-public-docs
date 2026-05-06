# SPLADE-v3: New baselines for SPLADE

Carlos Lassance
Cohere (Work done while at Naver)
cadurosar at gmail dot com

Hervé Déjean, Thibault Formal, Stéphane Clinchant
Naver Labs Europe
first.lastname at naverlabs dot com

## 概要

- 本稿は、SPLADE ライブラリの最新バージョンのリリースに付随するものである。
- 学習構造への変更点について述べ、最新のモデル系列である SPLADE-v3 を提示する。
- この新バージョンを BM25、SPLADE++、ならびに re-ranker と比較し、40 を超えるクエリセットに対するメタ分析を通じてその有効性を示す。
- SPLADE-v3 は SPLADE モデルの限界をさらに押し広げる。
- すなわち、BM25 および SPLADE++ の双方に対して統計的に有意に高い有効性を示しつつ、cross-encoder による re-ranker と比べても遜色ない性能を達成している。
- 具体的には、MS MARCO dev セットにおいて 40 を超える MRR@10 を達成し、BEIR ベンチマークにおける out-of-domain の結果を 1〜2% 改善している。


## 1 はじめに

- 本テクニカルレポートは、SPLADE ライブラリ1 の最新バージョンのリリースに付随するものである。
- 学習構造全体に対する単純な変更によって得られた改善を踏まえると、正式な論文発表に求められるような新規性が乏しいとはいえ、新しいモデルをリリースする価値は十分にあると考えている。
- そこで本レポートでは、SPLADE-v3 と名付けた新しい一連のモデルを記録し、コミュニティに対してより優れた SPLADE の「ベースライン」を提供することを目的とする。
- 我々はこの新しいバージョンのコードを、最近のほとんどの研究で使用してきた。


## 2 学習手法の改善

- ここでは、SPLADE モデルの学習に対して行われたいくつかの改善について詳述する。

### 2.1 バッチあたり複数のネガティブ

- Tevatron [9] に倣い、ライブラリでは現在、複数のハードネガティブを用いた学習が可能となっている。
- ネガティブの数を増やすことで、特に in-domain [3] 設定における結果が改善されることがわかったが、out-of-domain への汎化性能にはあまり寄与しない。
- 我々は SPLADE++ [5] モデルから得られたネガティブを使用し、100 件のネガティブを採用する。
- 内訳は top-50 から 50 件、top-1k からランダムに選んだ 50 件である。

### 2.2 蒸留スコアの改善

- SPLADE の有効性をさらに高めるため、単一モデルに依存する標準的な手法 [11, 5, 4]2 ではなく、cross-encoder リランカーのアンサンブルを用いて蒸留スコアを生成する。
- 我々は 2 種類のスコアを生成する: 1. スコアの単純なアンサンブル、および 2. "rescored" 版 (アフィン変換を用いて、データ統計量 (平均および標準偏差スコア値) のいくつかを以前の蒸留設定で得られたものと類似させたもの) 3。
- スコアの生成には HuggingFace 上の以下のオープンソースモデルを使用する。

1
https://github. com/naver/splade 2 特に cross-encoder/ms-marco-MiniLM-L-6-v2

3
https://huggingface. co/datasets/sentence-transformers/msmarco-hard-negatives

1\. cross-encoder/ms-marco-MiniLM-L-6-v2 +

2\. naver/trecdl22-crossencoder-rankT53b-repro

3\. naver/trecdl22-crossencoder-debertav3

4\. naver/trecdl22-crossencoder-debertav2

5\. naver/trecdl22-crossencoder-electra

- ここで、最初のもの (+) は SPLADE++ [5] のスコアを生成したモデルであり、残りは 2022 年版 TREC Deep Learning タスク [2] のために MS MARCO 上で我々が学習したモデルである。

- 我々は MS MARCO の学習セットの 500k 件のクエリそれぞれを、100 件のネガティブおよびポジティブとペアにしてリランカーに入力する。
- スコアは ranx [1] の min-max 集約を用いてクエリごとに正規化される。
- これにより我々の "ensemble" スコアが生成される。
- "rescored" スコアを生成するため、アンサンブルスコアの統計量を調査し、平均スコアと標準偏差が以前のスコアに近似するようアフィン変換を施す (*)。
- 経験的に、分布を変えることが蒸留 (特に MarginMSE [10] の場合) において有効であることがわかったが、その理由については詳しく調査していない。

### 2.3 2つの蒸留損失

- IR の文脈では、2 つの主要な蒸留損失が有効であることが示されている: KL-Div [14] (Eff-SPLADE [11] で使用) と MarginMSE [10] (SPLADE v2 [4] および SPLADE++ [4] で使用) である。
- 追加のネガティブが与えられた状況において、我々は経験的に MarginMSE (resp. KL-Div) が Recall (resp. Precision) により焦点を当てることに気付いた。
- そこで我々は両者を異なる重み (KL-Div には $$\lambda_{KL} = 1$$ 、MarginMSE には $$\lambda_{MSE} = 0.05$$ - 交差検証に基づく) で組み合わせることを選択し、これは全体としてより良い結果をもたらした。

### 2.4 SPLADE のさらなるファインチューニング

- 我々はまた、SPLADE++SelfDistil4 (SPLADE++EnsembleDistil [5] と比較してわずかなゼロショットの向上を示す) から開始し、前述の変更を適用することで、CoCondenser [8] や DistilBERT[16] のチェックポイントから開始する場合と比較してより良い有効性が得られることに気付いた。
- この効果の原因についてはまだ確信が持てていないが、Zeng et al. [21] で調査されたようなカリキュラム学習の一種が起こり、観察された改善につながっている可能性があると考えている。
- ただし、これについてはさらなる調査が必要である。


## 3 新しいベースライン: SPLADE-v3

- **SPLADE-v3** ベースとなる SPLADE-v3 モデル5 は SPLADE++SelfDistil から出発し、SPLADE++SelfDistil からサンプリングされたクエリあたり 8 個のネガティブを用いて、KL-Div と MarginMSE の混合で学習されている。
- その他のハイパーパラメータはすべて、これまでの SPLADE の各バージョンと同様である。
- 重要な点として、我々のすべての実験において、タイトルを含まないオリジナルの MS MARCO コレクション [12, 13] を使用していることに注意されたい。

- **評価** モデルの有効性を評価するため、RANGER [18, 19] で導入されたメタアナリシス手法を用いる。
- ir_datasets ライブラリ [15] を活用し、最大 44 種類のクエリセットを使用する。
- これらは様々なデータセットに由来し、1. MS MARCO passages (4 クエリセット)、2. MS MARCO v2 passages (4 クエリセット)、3. BEIR (13 クエリセット)、4. LoTTE (12 クエリセット)、5. Antique、6. TREC-CAR (y1) (2 クエリセット)、7. Natural Questions、8. TriviaQA、9. TREC-TB (3 クエリセット)、10. TREC-MQ (2 クエリセット) を含む。
- 有効性の測定には nDCG*@10 を用いる。
- ここで nDCG* は、データセットがポジティブとネガティブの両方の判定を持つ場合に、(検索された top-k に含まれる) 判定済み文書のみを考慮した nDCG を意味する。
- それ以外の場合は、標準的な nDCG@10 を使用する。

- **BM25 との比較** まず、本手法を BM25 と比較し、メタアナリシスの結果を図1に示す。
- 44 のクエリセットの大部分で統計的に有意な改善が見られ、有効性が統計的に低下したクエリセットはわずか 3 つにとどまる。
- これらのクエリセットは Webis Touché-2020 と 2 つの TREC-MQ クエリセットである。
- Touché-2020 については、実際の問題が何であるかは依然として不明であるが、この観察は学習型ランキングモデルにおいて繰り返し報告されている [5, 11, 20]。
- TREC-MQ については、長い文書をパッセージに分解する必要があるという問題があるかもしれない。

4 naver/splade-cocondenser-selfdistil 5 naver/splade-v3

<!-- PageNumber="2" -->

- サマリ効果が大きいことに注目してほしい。
- これは、比較全体を通じて SPLADE-v3 が BM25 を大幅に上回っていることを意味する (効率の面では劣るとしても)。

- **SPLADE++SelfDistil との比較** 次に、初期化に用いた以前の SPLADE モデルである SPLADE++SelfDistil と SPLADE-v3 を比較する。
- 理想的には、テストされたいずれのクエリセットにおいても有効性の低下があってはならない。
- メタアナリシスを図2に示す。
- Quora のみが有意な有効性低下を被ったが、他のほとんどのデータセットでは有効性が向上しており、全体のサマリ効果は新しいベースラインに対して正となっている。

- **再ランカーとの比較** 最後に、SPLADE-v3 をクロスエンコーダ型再ランカーと比較する。
- 具体的には、SPLADE-v3 が返す上位 $$k = 50$$ 件の文書を再ランクする 2 つのモデル、MiniLM6 と DeBERTaV37 を検討し、結果をそれぞれ図3と図4に示す。
- 再ランキングにはより大きな $$k$$ を使うことも可能であるが、特に十分にチューニングされた一段目検索器を再ランクする場合、50 件の文書を再ランクすることはすでに効率と有効性の良好なトレードオフを構成すると考える。
- MiniLM については、95 % 信頼区間を考慮するとサマリ効果がほぼ 0 に近く、元の結果と再ランク後の結果の間には大きな差がないことが分かる。
- 例外として、MiniLM の有効性における「外れ値」とも言えるいくつかのデータセットがある。
- 一方、DeBERTaV3 の場合は逆の傾向が見られ、ほとんどのクエリセットで再ランカーが SPLADE-v3 を上回っている。
- 例外は ArguAna であり、その「反論」タスクは再ランカーにとってより複雑である可能性がある。


## 4 SPLADE-v3-DistilBERT、SPLADE-v3-Lexical、SPLADE-v3-Doc

- 加えて、私たちは他の3つの SPLADE-v3 のバリアントもリリースする:

1\. SPLADE-v3-DistilBERT8 は、代わりに DistilBERT から学習を開始するため、推論時の「フットプリント」がより小さい。

2\. SPLADE-v3-Lexical9 は、クエリ拡張を取り除いたものであり、これにより検索時の FLOPS を削減する (そして効率を向上させる) [6]。

3\. SPLADE-v3-Doc10 は、CoCondenser から学習を開始し、クエリ側では計算を一切行わない - これは単純なバイナリの Bag-of-Words とみなすことができる [4, 6]。

- 表1 はデータセットごとの平均として結果をまとめたものであり、BEIR の 13 データセットにおける詳細な結果は表2 に示されている。
- SPLADE-v3-Lexical は MS MARCO および LoTTE において (非常に) 効果的であるが、BEIR (ドメイン外) では苦戦していることが分かる。
- DistilBERT バージョンは BERT バージョンから明らかに性能が低下しているが、それでも BEIR においては Lexical バージョンよりも効果的である。
- SPLADE-v3-Doc は全体として最も効果が低いアプローチであり、特に「ゼロショット」では顕著であって、これはクエリ側における (たとえ) 最小限の計算であっても重要であることを示している。
- しかしながら、その性能は最先端の密な bi-encoder と比較してもなお競争力があり、特にその効率性 (クエリのエンコーディングが不要であり、走査するポスティングリストの数が少ない) を考慮すると優れている。

<table>
<caption>表1: データセットごとの平均としての結果の比較。MS MARCO (MSM) については MRR@10、TREC については nDCG@10、BEIR (13 データセット) については nDCG@10 の平均、LoTTE [17] については Forum (LoTTE-F) および Search (LoTTE-S) タスクのプール対象外サブセット全てにわたる Success@5 の平均を報告する。また、効率性の大まかな指標として FLOPS の値も報告する [7]。</caption>
<tr>
<th>Model</th>
<th>MSM</th>
<th>TREC19</th>
<th>TREC20</th>
<th>BEIR 13</th>
<th>LoTTE-S</th>
<th>LoTTE-F</th>
<th>FLOPS</th>
</tr>
<tr>
<td>SPLADE++SD</td>
<td>37.6</td>
<td>73.0</td>
<td>71.8</td>
<td>50.7</td>
<td>-</td>
<td>-</td>
<td>1.4</td>
</tr>
<tr>
<td>SPLADE-v3</td>
<td>40.2</td>
<td>72.3</td>
<td>75.4</td>
<td>51.7</td>
<td>74.7</td>
<td>66.0</td>
<td>1.2</td>
</tr>
<tr>
<td>SPLADE-v3-DistilBERT</td>
<td>38.7</td>
<td>75.2</td>
<td>74.4</td>
<td>50.0</td>
<td>70.3</td>
<td>62.8</td>
<td>1.4</td>
</tr>
<tr>
<td>SPLADE-v3-Lexical</td>
<td>40.0</td>
<td>71.2</td>
<td>73.6</td>
<td>49.1</td>
<td>74.2</td>
<td>64.5</td>
<td>0.6</td>
</tr>
<tr>
<td>SPLADE-v3-Doc</td>
<td>37.8</td>
<td>71.5</td>
<td>70.3</td>
<td>47.0</td>
<td>71.1</td>
<td>59.0</td>
<td>1.4</td>
</tr>
</table>

6
cross-encoder/ms-marco-MiniLM-L-6-v2

8
naver/splade-v3-distilbert

7
naver/trecdl22-crossencoder-debertav3

9
naver/splade-v3-lexical
10
naver/splade-v3-doc

<!-- PageNumber="3" -->

<table>
<caption>表2: BEIR [20] の 13 データセットにおける nDCG@10。</caption>
<tr>
<th>Dataset</th>
<th>SPLADE++SD</th>
<th>SPLADE-v3</th>
<th>SPLADE-v3-DistilBERT</th>
<th>SPLADE-v3-Lexical</th>
<th>SPLADE-v3-Doc</th>
</tr>
<tr>
<td>ArguAna</td>
<td>51.8</td>
<td>50.9</td>
<td>48.4</td>
<td>52.7</td>
<td>46.7</td>
</tr>
<tr>
<td>Climate-FEVER</td>
<td>23.7</td>
<td>23.3</td>
<td>22.8</td>
<td>21.8</td>
<td>15.9</td>
</tr>
<tr>
<td>DBPedia-entity</td>
<td>43.6</td>
<td>45.0</td>
<td>42.6</td>
<td>42.8</td>
<td>36.1</td>
</tr>
<tr>
<td>FEVER</td>
<td>79.6</td>
<td>79.6</td>
<td>79.6</td>
<td>78.5</td>
<td>68.9</td>
</tr>
<tr>
<td>FiQA-2018</td>
<td>34.9</td>
<td>37.4</td>
<td>33.9</td>
<td>36.4</td>
<td>33.6</td>
</tr>
<tr>
<td>HotpotQA</td>
<td>69.3</td>
<td>69.2</td>
<td>67.8</td>
<td>68.5</td>
<td>66.9</td>
</tr>
<tr>
<td>NFCorpus</td>
<td>34.5</td>
<td>35.7</td>
<td>34.8</td>
<td>34.7</td>
<td>33.8</td>
</tr>
<tr>
<td>NQ</td>
<td>53.3</td>
<td>58.6</td>
<td>54.9</td>
<td>56.1</td>
<td>52.1</td>
</tr>
<tr>
<td>Quora</td>
<td>84.9</td>
<td>81.4</td>
<td>81.7</td>
<td>73.4</td>
<td>77.5</td>
</tr>
<tr>
<td>SCIDOCS</td>
<td>16.1</td>
<td>15.8</td>
<td>14.8</td>
<td>15.9</td>
<td>15.2</td>
</tr>
<tr>
<td>SciFact</td>
<td>71.0</td>
<td>71.0</td>
<td>68.5</td>
<td>71.5</td>
<td>68.8</td>
</tr>
<tr>
<td>TREC-COVID</td>
<td>72.5</td>
<td>74.8</td>
<td>70.0</td>
<td>63.6</td>
<td>68.1</td>
</tr>
<tr>
<td>Touché-2020</td>
<td>24.2</td>
<td>29.3</td>
<td>30.1</td>
<td>22.7</td>
<td>27.0</td>
</tr>
<tr>
<td>Average</td>
<td>50.7</td>
<td>51.7</td>
<td>50.0</td>
<td>49.1</td>
<td>47.0</td>
</tr>
</table>


## 5 結論

- 本テクニカルレポートでは、SPLADE-v3 モデルのリリースについて述べた。
- 広範な評価を通じて、この新しい SPLADE モデル群が以前のバージョンと比較して統計的に有意に高い有効性を示すことを明らかにした。
- ゼロショット設定を含むほとんどのクエリセットにおいて、SPLADE-v3 は BM25 を上回り、一部のリランカーに匹敵する性能さえ達成している。


## 参考文献

[1] E. Bassani. ranx: A blazing-fast python library for ranking evaluation and comparison. In
European Conference on Information Retrieval, pages 259-264. Springer, 2022.

[2] N. Craswell, B. Mitra, E. Yilmaz, D. F. Campos, J. Lin, E. M. Voorhees, and I. Soboroff.
Overview of the trec 2022 deep learning track. In Text Retrieval Conference, 2022.

[3] H. Déjean, S. Clinchant, C. Lassance, S. Lupart, and T. Formal. Benchmarking middle-trained
language models for neural search. arXiv preprint arXiv:2306.02867, 2023.

[4] T. Formal, C. Lassance, B. Piwowarski, and S. Clinchant. Splade v2: Sparse lexical and
expansion model for information retrieval, 2021.

[5] T. Formal, C. Lassance, B. Piwowarski, and S. Clinchant. From distillation to hard negative
sampling: Making sparse neural ir models more effective. In Proceedings of the 45th Interna-
tional ACM SIGIR Conference on Research and Development in Information Retrieval, pages
2353-2359, 2022.

[6] T. Formal, C. Lassance, B. Piwowarski, and S. Clinchant. Towards effective and efficient sparse
neural information retrieval. ACM Trans. Inf. Syst., dec 2023. Just Accepted.

[7] T. Formal, B. Piwowarski, and S. Clinchant. SPLADE: Sparse Lexical and Expansion Model
for First Stage Ranking. In Proc. SIGIR, page 2288-2292, 2021.

[8] L. Gao and J. Callan. Unsupervised corpus aware language model pre-training for dense passage
retrieval. In S. Muresan, P. Nakov, and A. Villavicencio, editors, Proceedings of the 60th Annual
Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages
2843-2853, Dublin, Ireland, May 2022. Association for Computational Linguistics.

[9] L. Gao, X. Ma, J. Lin, and J. Callan. Tevatron: An efficient and flexible toolkit for dense
retrieval. arXiv preprint arXiv:2203.05765, 2022.

[10] S. Hofstätter, S. Althammer, M. Schröder, M. Sertkan, and A. Hanbury. Improving efficient
neural ranking models with cross-architecture knowledge distillation, 2021.

[11] C. Lassance and S. Clinchant. An efficiency study for splade models. In Proceedings of the 45th
International ACM SIGIR Conference on Research and Development in Information Retrieval,
pages 2220-2226, 2022.

[12] C. Lassance and S. Clinchant. The tale of two ms marco - and their unfair comparisons, 2023.

<!-- PageNumber="4" -->


<table>
<caption>図1: SPLADE-v3 と BM25 のメタ分析による比較。</caption>
<tr>
<th colspan="7">BM25 vs SPLADE-2023</th>
</tr>
<tr>
<th>Effect Size</th>
<th colspan="2"></th>
<th>Weight</th>
<th>Mean</th>
<th>CI 95%</th>
<th>nDCG*@10</th>
</tr>
<tr>
<td>M-DEV</td>
<td colspan="2"></td>
<td>2.4%</td>
<td>0.25</td>
<td>[0.23, 0.26]</td>
<td>0.223 + 0.469</td>
</tr>
<tr>
<td>M-TREC_2019</td>
<td colspan="2"></td>
<td>1.6%</td>
<td>0.26</td>
<td>[0.15, 0.37]</td>
<td>0.496 -+ 0.754</td>
</tr>
<tr>
<td>M-TREC_2020</td>
<td colspan="2"></td>
<td>2.0%</td>
<td>0.28</td>
<td>[0.20, 0.36]</td>
<td>0.480 -+ 0.758</td>
</tr>
<tr>
<td>M-TREC-Hard</td>
<td colspan="2"></td>
<td>1.9%</td>
<td>0.20</td>
<td>[0.12, 0.29]</td>
<td>0.565 - 0.769</td>
</tr>
<tr>
<td>M-TREC_2021</td>
<td colspan="2"></td>
<td>2.0%</td>
<td>0.27</td>
<td>[0.20, 0.35]</td>
<td>0.445 - 0.718</td>
</tr>
<tr>
<td>M-TREC_2022</td>
<td></td>
<td></td>
<td>2.1%</td>
<td>0.37</td>
<td>[0.30, 0.43]</td>
<td>0.281 - 0.650</td>
</tr>
<tr>
<td>M-V2_DEV</td>
<td colspan="2"></td>
<td>2.4%</td>
<td>0.13</td>
<td>[0.11, 0.14]</td>
<td>0.076 - 0.202</td>
</tr>
<tr>
<td>M-V2_DEV2</td>
<td colspan="2"></td>
<td>2.4%</td>
<td>0.13</td>
<td>[0.12, 0.14]</td>
<td>0.082 - 0.213</td>
</tr>
<tr>
<td>B-arguana</td>
<td colspan="2"></td>
<td>2.4%</td>
<td>0.17</td>
<td>[0.14, 0.19]</td>
<td>0.348 - 0.514</td>
</tr>
<tr>
<td>B-climate-fever</td>
<td colspan="2"></td>
<td>2.4%</td>
<td>0.04</td>
<td>[0.02, 0.06]</td>
<td>0.169 -+ 0.208</td>
</tr>
<tr>
<td>B-dbpedia</td>
<td colspan="2"></td>
<td>2.4%</td>
<td>0.17</td>
<td>[0.14, 0.20]</td>
<td>0.403 -+ 0.573</td>
</tr>
<tr>
<td>B-fever</td>
<td colspan="2"></td>
<td>2.4%</td>
<td>0.16</td>
<td>[0.15, 0.17]</td>
<td>0.622 - 0.784</td>
</tr>
<tr>
<td>B-fiqa</td>
<td colspan="2"></td>
<td>2.3%</td>
<td>0.13</td>
<td>[0.10, 0.17]</td>
<td>0.240 - 0.373</td>
</tr>
<tr>
<td>B-hotpotqa</td>
<td colspan="2"></td>
<td>2.5%</td>
<td>0.06</td>
<td>[0.06, 0.07]</td>
<td>0.625 - 0.690</td>
</tr>
<tr>
<td>B-nfcorpus</td>
<td colspan="2"></td>
<td>2.2%</td>
<td>0.03</td>
<td>[-0.02, 0.08]</td>
<td>0.328 - 0.358</td>
</tr>
<tr>
<td>B-nq</td>
<td></td>
<td></td>
<td>2.4%</td>
<td>0.28</td>
<td>[0.26, 0.30]</td>
<td>0.306 - 0.586</td>
</tr>
<tr>
<td>B-quora</td>
<td colspan="2"></td>
<td>2.5%</td>
<td>0.10</td>
<td>[0.09, 0.11]</td>
<td>0.709 - 0.813</td>
</tr>
<tr>
<td>B-scidocs</td>
<td colspan="2"></td>
<td>2.4%</td>
<td>0.01</td>
<td>[-0.01, 0.02]</td>
<td>0.152 + 0.158</td>
</tr>
<tr>
<td>B-scifact</td>
<td colspan="2"></td>
<td>2.1%</td>
<td>0.03</td>
<td>[-0.03, 0.09]</td>
<td>0.678 -+ 0.711</td>
</tr>
<tr>
<td>B-TREC_Covid</td>
<td colspan="2"></td>
<td>1.8%</td>
<td>0.13</td>
<td>[0.03, 0.22]</td>
<td>0.648 -+ 0.774</td>
</tr>
<tr>
<td>B-Touche</td>
<td colspan="2"></td>
<td>2.1%</td>
<td>-0.08</td>
<td>[-0.15, -0.01]</td>
<td>0.835 -+ 0.756</td>
</tr>
<tr>
<td>L-Lifestyle-S</td>
<td></td>
<td></td>
<td>2.3%</td>
<td>0.19</td>
<td>[0.16, 0.23]</td>
<td>0.434 - 0.629</td>
</tr>
<tr>
<td>L-Pooled-S</td>
<td colspan="2"></td>
<td>2.4%</td>
<td>0.21</td>
<td>[0.20, 0.23]</td>
<td>0.319 - 0.532</td>
</tr>
<tr>
<td>L-Recreation-S</td>
<td></td>
<td></td>
<td>2.4%</td>
<td>0.16</td>
<td>[0.13, 0.19]</td>
<td>0.389 - 0.549</td>
</tr>
<tr>
<td>L-Science-S</td>
<td colspan="2"></td>
<td>2.4%</td>
<td>0.17</td>
<td>[0.14, 0.21]</td>
<td>0.223 - 0.398</td>
</tr>
<tr>
<td>L-Technology-S</td>
<td></td>
<td></td>
<td>2.3%</td>
<td>0.22</td>
<td>[0.18, 0.25]</td>
<td>0.247 - 0.465</td>
</tr>
<tr>
<td>L-Writing-S</td>
<td></td>
<td></td>
<td>2.4%</td>
<td>0.21</td>
<td>[0.17, 0.24]</td>
<td>0.410 - 0.615</td>
</tr>
<tr>
<td>L-Lifestyle-F</td>
<td></td>
<td></td>
<td>2.4%</td>
<td>0.17</td>
<td>[0.15, 0.19]</td>
<td>0.311 + 0.478</td>
</tr>
<tr>
<td>L-Pooled-F</td>
<td></td>
<td></td>
<td>2.5%</td>
<td>0.13</td>
<td>[0.13, 0.14]</td>
<td>0.224 -+ 0.358</td>
</tr>
<tr>
<td>L-Recreation-F</td>
<td></td>
<td></td>
<td>2.4%</td>
<td>0.14</td>
<td>[0.12, 0.16]</td>
<td>0.334 -+ 0.474</td>
</tr>
<tr>
<td>L-Science-F</td>
<td colspan="2"></td>
<td>2.4%</td>
<td>0.05</td>
<td>[0.04, 0.06]</td>
<td>0.148 - 0.198</td>
</tr>
<tr>
<td>L-Technology-F</td>
<td></td>
<td></td>
<td>2.4%</td>
<td>0.09</td>
<td>[0.08, 0.11]</td>
<td>0.155 - 0.246</td>
</tr>
<tr>
<td>L-Writing-F</td>
<td></td>
<td></td>
<td>2.4%</td>
<td>0.14</td>
<td>[0.12, 0.16]</td>
<td>0.330 - 0.470</td>
</tr>
<tr>
<td>Antique</td>
<td></td>
<td></td>
<td>2.3%</td>
<td>0.19</td>
<td>[0.15, 0.22]</td>
<td>0.528 - 0.715</td>
</tr>
<tr>
<td>TREC-CAR-auto</td>
<td></td>
<td></td>
<td>2.4%</td>
<td>0.15</td>
<td>[0.13, 0.17]</td>
<td>0.195 - 0.347</td>
</tr>
<tr>
<td>TREC-CAR-manual</td>
<td colspan="2"></td>
<td>2.4%</td>
<td>0.14</td>
<td>[0.12, 0.17]</td>
<td>0.550 + 0.693</td>
</tr>
<tr>
<td>DPR-NQ</td>
<td></td>
<td></td>
<td>2.5%</td>
<td>0.20</td>
<td>[0.19, 0.21]</td>
<td>0.249 - 0.447</td>
</tr>
<tr>
<td>DPR-TriviaQA</td>
<td colspan="2"></td>
<td>2.5%</td>
<td>0.01</td>
<td>[-0.00, 0.02]</td>
<td>0.351 + 0.358</td>
</tr>
<tr>
<td>Mr. TyDi English</td>
<td></td>
<td></td>
<td>2.4%</td>
<td>0.26</td>
<td>[0.23, 0.29]</td>
<td>0.124 -+ 0.384</td>
</tr>
<tr>
<td>TREC-TB-2004</td>
<td></td>
<td></td>
<td>1.6%</td>
<td>0.00</td>
<td>[-0.11, 0.11]</td>
<td>0.363 -&gt; 0.365</td>
</tr>
<tr>
<td>TREC-TB-2005</td>
<td></td>
<td></td>
<td>1.7%</td>
<td>-0.05</td>
<td>[-0.15, 0.05]</td>
<td>0.512 -&gt; 0.466</td>
</tr>
<tr>
<td>TREC-TB-2006</td>
<td></td>
<td></td>
<td>1.7%</td>
<td>-0.03</td>
<td>[-0.13, 0.07]</td>
<td>0.484 - 0.453</td>
</tr>
<tr>
<td>TREC-MQ-2007</td>
<td></td>
<td></td>
<td>2.4%</td>
<td>-0.05</td>
<td>[-0.07, -0.03]</td>
<td>0.419 - 0.367</td>
</tr>
<tr>
<td>TREC-MQ-2008</td>
<td></td>
<td></td>
<td>2.4%</td>
<td>-0.16</td>
<td>[-0.19, -0.12]</td>
<td>0.467 - 0.311</td>
</tr>
<tr>
<td>Summary Effect (RE)</td>
<td colspan="2"></td>
<td></td>
<td>0.13</td>
<td>[0.11, 0.15]</td>
<td>0.375 +0.503</td>
</tr>
<tr>
<td></td>
<td colspan="2">0.0 0.2 0.4 Mean Difference</td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
</table>


<!-- PageNumber="5" -->

<table>
<caption>図2: SPLADE-v3 と SPLADE++SelfDistil のメタ分析による比較。</caption>
<tr>
<th colspan="6">SPLADE++ Self Distil vs SPLADE-2023</th>
</tr>
<tr>
<th>Effect Size</th>
<th></th>
<th>Weight</th>
<th>Mean</th>
<th>CI 95%</th>
<th>nDCG*@10</th>
</tr>
<tr>
<td>M-DEV</td>
<td></td>
<td>3.3%</td>
<td>0.02</td>
<td>[0.01, 0.04]</td>
<td>0.445 -+ 0.469</td>
</tr>
<tr>
<td>M-TREC_2019</td>
<td></td>
<td>0.6%</td>
<td>-0.01</td>
<td>[-0.10, 0.08]</td>
<td>0.761 -&gt; 0.754</td>
</tr>
<tr>
<td>M-TREC_2020</td>
<td></td>
<td>1.2%</td>
<td>0.02</td>
<td>[-0.04, 0.08]</td>
<td>0.737 -+ 0.758</td>
</tr>
<tr>
<td>M-TREC-Hard</td>
<td></td>
<td>0.8%</td>
<td>0.00</td>
<td>[-0.07, 0.08]</td>
<td>0.766 - 0.769</td>
</tr>
<tr>
<td>M-TREC_2021</td>
<td></td>
<td>0.9%</td>
<td>0.03</td>
<td>[-0.04, 0.10]</td>
<td>0.691 - 0.718</td>
</tr>
<tr>
<td>M-TREC_2022</td>
<td></td>
<td>1.0%</td>
<td>0.07</td>
<td>[0.01, 0.14]</td>
<td>0.579 - 0.650</td>
</tr>
<tr>
<td>M-V2_DEV</td>
<td></td>
<td>3.2%</td>
<td>0.02</td>
<td>[0.01, 0.03]</td>
<td>0.181 - 0.202</td>
</tr>
<tr>
<td>M-V2_DEV2</td>
<td></td>
<td>3.2%</td>
<td>0.02</td>
<td>[0.01, 0.04]</td>
<td>0.188 + 0.213</td>
</tr>
<tr>
<td>B-arguana</td>
<td></td>
<td>2.7%</td>
<td>-0.01</td>
<td>[-0.03, 0.02]</td>
<td>0.521 + 0.514</td>
</tr>
<tr>
<td>B-climate-fever</td>
<td></td>
<td>3.0%</td>
<td>-0.02</td>
<td>[-0.03, 0.00]</td>
<td>0.225 - 0.208</td>
</tr>
<tr>
<td>B-dbpedia</td>
<td></td>
<td>2.3%</td>
<td>0.01</td>
<td>[-0.02, 0.05]</td>
<td>0.559 -+ 0.573</td>
</tr>
<tr>
<td>B-fever</td>
<td></td>
<td>3.4%</td>
<td>-0.00</td>
<td>[-0.01, 0.01]</td>
<td>0.788 -+ 0.784</td>
</tr>
<tr>
<td>B-fiqa</td>
<td></td>
<td>1.9%</td>
<td>0.02</td>
<td>[-0.01, 0.06]</td>
<td>0.349 - 0.373</td>
</tr>
<tr>
<td>B-hotpotqa</td>
<td></td>
<td>3.5%</td>
<td>0.00</td>
<td>[-0.01, 0.01]</td>
<td>0.689 - 0.690</td>
</tr>
<tr>
<td>B-nfcorpus</td>
<td></td>
<td>1.5%</td>
<td>0.01</td>
<td>[-0.04, 0.06]</td>
<td>0.346 - 0.358</td>
</tr>
<tr>
<td>B-nq</td>
<td></td>
<td>3.0%</td>
<td>0.05</td>
<td>[0.03, 0.06]</td>
<td>0.540 -+ 0.586</td>
</tr>
<tr>
<td>B-quora</td>
<td></td>
<td>3.5%</td>
<td>-0.03</td>
<td>[-0.04, -0.03]</td>
<td>0.848 - 0.813</td>
</tr>
<tr>
<td>B-scidocs</td>
<td></td>
<td>3.0%</td>
<td>-0.00</td>
<td>[-0.02, 0.01]</td>
<td>0.162 + 0.158</td>
</tr>
<tr>
<td>B-scifact</td>
<td></td>
<td>1.1%</td>
<td>0.01</td>
<td>[-0.05, 0.07]</td>
<td>0.701 + 0.711</td>
</tr>
<tr>
<td>B-TREC_Covid</td>
<td></td>
<td>0.6%</td>
<td>0.01</td>
<td>[-0.07, 0.10]</td>
<td>0.761 - 0.774</td>
</tr>
<tr>
<td>B-Touche</td>
<td></td>
<td>0.8%</td>
<td>0.05</td>
<td>[-0.02, 0.13]</td>
<td>0.701 - 0.756</td>
</tr>
<tr>
<td>L-Lifestyle-S</td>
<td></td>
<td>2.0%</td>
<td>0.02</td>
<td>[-0.01, 0.06]</td>
<td>0.604 - 0.629</td>
</tr>
<tr>
<td>L-Pooled-S</td>
<td></td>
<td>3.2%</td>
<td>0.03</td>
<td>[0.01, 0.04]</td>
<td>0.504 - 0.532</td>
</tr>
<tr>
<td>L-Recreation-S</td>
<td></td>
<td>2.2%</td>
<td>0.03</td>
<td>[0.00, 0.06]</td>
<td>0.518 - 0.549</td>
</tr>
<tr>
<td>L-Science-S</td>
<td></td>
<td>2.1%</td>
<td>0.02</td>
<td>[-0.01, 0.05]</td>
<td>0.378 - 0.398</td>
</tr>
<tr>
<td>L-Technology-S</td>
<td></td>
<td>1.9%</td>
<td>0.04</td>
<td>[-0.00, 0.07]</td>
<td>0.430 -+ 0.465</td>
</tr>
<tr>
<td>L-Writing-S</td>
<td></td>
<td>2.3%</td>
<td>0.02</td>
<td>[-0.00, 0.05]</td>
<td>0.591 + 0.615</td>
</tr>
<tr>
<td>L-Lifestyle-F</td>
<td></td>
<td>2.9%</td>
<td>0.03</td>
<td>[0.02, 0.05]</td>
<td>0.444 -+ 0.478</td>
</tr>
<tr>
<td>L-Pooled-F</td>
<td></td>
<td>3.5%</td>
<td>0.02</td>
<td>[0.02, 0.03]</td>
<td>0.333 -+ 0.358</td>
</tr>
<tr>
<td>L-Recreation-F</td>
<td></td>
<td>2.8%</td>
<td>0.02</td>
<td>[-0.00, 0.04]</td>
<td>0.454 -+ 0.474</td>
</tr>
<tr>
<td>L-Science-F</td>
<td></td>
<td>3.2%</td>
<td>0.01</td>
<td>[-0.00, 0.02]</td>
<td>0.187 - 0.198</td>
</tr>
<tr>
<td>L-Technology-F</td>
<td></td>
<td>3.1%</td>
<td>0.02</td>
<td>[0.01, 0.04]</td>
<td>0.226 - 0.246</td>
</tr>
<tr>
<td>L-Writing-F</td>
<td></td>
<td>2.9%</td>
<td>0.03</td>
<td>[0.01, 0.05]</td>
<td>0.441 - 0.470</td>
</tr>
<tr>
<td>Antique</td>
<td></td>
<td>2.1%</td>
<td>0.06</td>
<td>[0.02, 0.09]</td>
<td>0.659 - 0.715</td>
</tr>
<tr>
<td>TREC-CAR-auto</td>
<td></td>
<td>2.9%</td>
<td>0.02</td>
<td>[0.00, 0.04]</td>
<td>0.325 -+ 0.347</td>
</tr>
<tr>
<td>TREC-CAR-manual</td>
<td></td>
<td>2.5%</td>
<td>0.02</td>
<td>[-0.00, 0.05]</td>
<td>0.671 + 0.693</td>
</tr>
<tr>
<td>DPR-NQ</td>
<td></td>
<td>3.4%</td>
<td>0.03</td>
<td>[0.02, 0.04]</td>
<td>0.418 -+ 0.447</td>
</tr>
<tr>
<td>DPR-TriviaQA</td>
<td></td>
<td>3.4%</td>
<td>0.00</td>
<td>[-0.01, 0.01]</td>
<td>0.357 - 0.358</td>
</tr>
<tr>
<td>Mr. TyDi English</td>
<td></td>
<td>1.9%</td>
<td>0.04</td>
<td>[0.00, 0.08]</td>
<td>0.343 ++ 0.384</td>
</tr>
<tr>
<td>TREC-TB-2004</td>
<td></td>
<td>0.6%</td>
<td>-0.00</td>
<td>[-0.09, 0.09]</td>
<td>0.365 - 0.365</td>
</tr>
<tr>
<td>TREC-TB-2005</td>
<td></td>
<td>0.6%</td>
<td>0.02</td>
<td>[-0.07, 0.11]</td>
<td>0.448 - 0.466</td>
</tr>
<tr>
<td>TREC-TB-2006</td>
<td></td>
<td>0.6%</td>
<td>0.01</td>
<td>[-0.08, 0.10]</td>
<td>0.445 - 0.453</td>
</tr>
<tr>
<td>TREC-MQ-2007</td>
<td></td>
<td>3.0%</td>
<td>0.02</td>
<td>[0.00, 0.04]</td>
<td>0.347 - 0.367</td>
</tr>
<tr>
<td>TREC-MQ-2008</td>
<td></td>
<td>2.7%</td>
<td>0.00</td>
<td>[-0.02, 0.03]</td>
<td>0.307 - 0.311</td>
</tr>
<tr>
<td>Summary Effect (RE) -0.05</td>
<td>0.00 0.05 0.10</td>
<td></td>
<td>0.02</td>
<td>[0.01, 0.02]</td>
<td>0.485 + 0.503</td>
</tr>
</table>


<!-- PageNumber="6" -->

<table>
<caption>図3: SPLADE-v3 と MiniLM (SPLADE-v3 が返した上位50件を再ランキング) のメタ分析による比較。</caption>
<tr>
<th></th>
<th colspan="4">SPLADE-2023 vs SPLADE-2023 + MINILM top50</th>
<th></th>
<th></th>
</tr>
<tr>
<th></th>
<th>Effect Size</th>
<th colspan="2">Weight</th>
<th>Mean</th>
<th>CI 95%</th>
<th>nDCG*@10</th>
</tr>
<tr>
<td>M-DEV</td>
<td></td>
<td colspan="2">2.9%</td>
<td>0.00</td>
<td>[-0.00, 0.01]</td>
<td>0.469 -&gt; 0.473</td>
</tr>
<tr>
<td>M-TREC_2019</td>
<td></td>
<td colspan="2">2.2%</td>
<td>0.01</td>
<td>[-0.01, 0.04]</td>
<td>0.754 -+ 0.768</td>
</tr>
<tr>
<td>M-TREC_2020</td>
<td></td>
<td colspan="2">2.2%</td>
<td>-0.01</td>
<td>[-0.03, 0.02]</td>
<td>0.758 - 0.750</td>
</tr>
<tr>
<td>M-TREC-Hard</td>
<td></td>
<td></td>
<td>0.6%</td>
<td>-0.13</td>
<td>[-0.21, -0.06]</td>
<td>0.769 -+ 0.637</td>
</tr>
<tr>
<td>M-TREC_2021</td>
<td></td>
<td colspan="2">2.1%</td>
<td>-0.01</td>
<td>[-0.04, 0.02]</td>
<td>0.718 -+ 0.708</td>
</tr>
<tr>
<td>M-TREC_2022</td>
<td></td>
<td colspan="2">1.9%</td>
<td>-0.02</td>
<td>[-0.04, 0.01]</td>
<td>0.650 -&gt; 0.635</td>
</tr>
<tr>
<td>M-V2_DEV</td>
<td></td>
<td colspan="2">2.9%</td>
<td>-0.01</td>
<td>[-0.01, 0.00]</td>
<td>0.202 - 0.197</td>
</tr>
<tr>
<td>M-V2_DEV2</td>
<td></td>
<td colspan="2">2.9%</td>
<td>-0.00</td>
<td>[-0.01, 0.00]</td>
<td>0.213 -+ 0.210</td>
</tr>
<tr>
<td>B-arguana</td>
<td></td>
<td></td>
<td>2.4%</td>
<td>-0.09</td>
<td>[-0.11, -0.08]</td>
<td>0.514 - 0.420</td>
</tr>
<tr>
<td>B-climate-fever</td>
<td></td>
<td colspan="2">2.8%</td>
<td>0.03</td>
<td>[0.02, 0.04]</td>
<td>0.208 -+ 0.238</td>
</tr>
<tr>
<td>B-dbpedia</td>
<td></td>
<td colspan="2">2.7%</td>
<td>-0.01</td>
<td>[-0.02, 0.00]</td>
<td>0.573 -+ 0.567</td>
</tr>
<tr>
<td>B-fever</td>
<td></td>
<td colspan="2">2.9%</td>
<td>0.03</td>
<td>[0.02, 0.03]</td>
<td>0.784 - 0.812</td>
</tr>
<tr>
<td>B-fiqa</td>
<td></td>
<td colspan="2">2.6%</td>
<td>-0.01</td>
<td>[-0.02, 0.01]</td>
<td>0.373 - 0.367</td>
</tr>
<tr>
<td>B-hotpotqa</td>
<td></td>
<td></td>
<td>2.9%</td>
<td>0.03</td>
<td>[0.03, 0.04]</td>
<td>0.690 -+ 0.723</td>
</tr>
<tr>
<td>B-nfcorpus</td>
<td></td>
<td colspan="2">2.8%</td>
<td>-0.01</td>
<td>[-0.02, -0.00]</td>
<td>0.358 -&gt; 0.347</td>
</tr>
<tr>
<td>B-nq</td>
<td></td>
<td colspan="2">2.8%</td>
<td>-0.01</td>
<td>[-0.01, 0.00]</td>
<td>0.586 -+ 0.579</td>
</tr>
<tr>
<td>B-quora</td>
<td></td>
<td colspan="2">2.9%</td>
<td>0.01</td>
<td>[0.01, 0.02]</td>
<td>0.813 -+ 0.826</td>
</tr>
<tr>
<td>B-scidocs</td>
<td></td>
<td colspan="2">2.9%</td>
<td>0.01</td>
<td>[0.00, 0.02]</td>
<td>0.158 -&gt; 0.168</td>
</tr>
<tr>
<td>B-scifact</td>
<td></td>
<td colspan="2">2.1%</td>
<td>-0.03</td>
<td>[-0.05, -0.00]</td>
<td>0.711 - 0.685</td>
</tr>
<tr>
<td>B-TREC_Covid</td>
<td></td>
<td colspan="2">1.4%</td>
<td>-0.02</td>
<td>[-0.06, 0.02]</td>
<td>0.774 - 0.755</td>
</tr>
<tr>
<td>B-Touche</td>
<td></td>
<td colspan="2">1.2%</td>
<td>-0.16</td>
<td>[-0.21, -0.11]</td>
<td>0.756 -&gt; 0.596</td>
</tr>
<tr>
<td>L-Lifestyle-S</td>
<td></td>
<td colspan="2">2.6%</td>
<td>-0.01</td>
<td>[-0.03, 0.00]</td>
<td>0.629 -+ 0.617</td>
</tr>
<tr>
<td>L-Pooled-S</td>
<td></td>
<td colspan="2">2.9%</td>
<td>-0.02</td>
<td>[-0.02, -0.01]</td>
<td>0.532 - 0.516</td>
</tr>
<tr>
<td>L-Recreation-S</td>
<td></td>
<td colspan="2">2.6%</td>
<td>-0.00</td>
<td>[-0.01, 0.01]</td>
<td>0.549 -+ 0.549</td>
</tr>
<tr>
<td>L-Science-S</td>
<td></td>
<td colspan="2">2.7%</td>
<td>-0.02</td>
<td>[-0.03, -0.01]</td>
<td>0.398 -+ 0.377</td>
</tr>
<tr>
<td>L-Technology-S</td>
<td></td>
<td colspan="2">2.6%</td>
<td>-0.02</td>
<td>[-0.04, -0.01]</td>
<td>0.465 -&gt; 0.444</td>
</tr>
<tr>
<td>L-Writing-S</td>
<td></td>
<td colspan="2">2.7%</td>
<td>-0.02</td>
<td>[-0.03, -0.01]</td>
<td>0.615 -&gt; 0.593</td>
</tr>
<tr>
<td>L-Lifestyle-F</td>
<td></td>
<td colspan="2">2.9%</td>
<td>-0.01</td>
<td>[-0.02, -0.00]</td>
<td>0.478 -&gt; 0.468</td>
</tr>
<tr>
<td>L-Pooled-F</td>
<td></td>
<td colspan="2">2.9%</td>
<td>-0.00</td>
<td>[-0.01, -0.00]</td>
<td>0.358 -&gt; 0.354</td>
</tr>
<tr>
<td>L-Recreation-F</td>
<td></td>
<td colspan="2">2.8%</td>
<td>0.00</td>
<td>[-0.01, 0.01]</td>
<td>0.474 -+ 0.475</td>
</tr>
<tr>
<td>L-Science-F</td>
<td></td>
<td colspan="2">2.9%</td>
<td>0.00</td>
<td>[-0.00, 0.01]</td>
<td>0.198 -+ 0.201</td>
</tr>
<tr>
<td>L-Technology-F</td>
<td></td>
<td colspan="2">2.9%</td>
<td>-0.01</td>
<td>[-0.02, -0.01]</td>
<td>0.246 -&gt; 0.233</td>
</tr>
<tr>
<td>L-Writing-F</td>
<td></td>
<td colspan="2">2.9%</td>
<td>-0.00</td>
<td>[-0.01, 0.01]</td>
<td>0.470 - 0.469</td>
</tr>
<tr>
<td>Antique</td>
<td></td>
<td colspan="2">2.6%</td>
<td>-0.06</td>
<td>[-0.08, -0.05]</td>
<td>0.715 -&gt; 0.650</td>
</tr>
<tr>
<td>TREC-CAR-auto</td>
<td></td>
<td colspan="2">2.8%</td>
<td>-0.01</td>
<td>[-0.02, -0.00]</td>
<td>0.347 -+ 0.338</td>
</tr>
<tr>
<td>TREC-CAR-manual</td>
<td></td>
<td colspan="2">2.8%</td>
<td>-0.06</td>
<td>[-0.07, -0.05]</td>
<td>0.693 -+ 0.637</td>
</tr>
<tr>
<td>DPR-NQ</td>
<td></td>
<td></td>
<td>2.9%</td>
<td>0.00</td>
<td>[-0.00, 0.01]</td>
<td>0.447 -&gt; 0.452</td>
</tr>
<tr>
<td>DPR-TriviaQA</td>
<td></td>
<td colspan="2">2.9%</td>
<td>0.02</td>
<td>[0.02, 0.03]</td>
<td>0.358 -+ 0.381</td>
</tr>
<tr>
<td>Mr. TyDi English</td>
<td></td>
<td></td>
<td>2.5%</td>
<td>-0.05</td>
<td>[-0.07, -0.04]</td>
<td>0.384 - 0.330</td>
</tr>
<tr>
<td>Summary Effect (RE)</td>
<td></td>
<td></td>
<td></td>
<td>-0.01</td>
<td>[-0.02, -0.00]</td>
<td>0.518 - 0.501</td>
</tr>
<tr>
<td colspan="2">-0.20 -0.15 -0.10 -0.05 Mean Difference</td>
<td colspan="2">0.00</td>
<td></td>
<td></td>
<td></td>
</tr>
</table>


<!-- PageNumber="7" -->

<table>
<caption>図4: SPLADE-v3 と DeBERTaV3 (SPLADE-v3 が返した上位50件を再ランキング) のメタ分析による比較。</caption>
<tr>
<th colspan="7">SPLADE-2023 vs SPLADE-2023 + DebertaV3 top50</th>
</tr>
<tr>
<th colspan="2">Effect Size</th>
<th></th>
<th>Weight</th>
<th>Mean</th>
<th>CI 95%</th>
<th>nDCG*@10</th>
</tr>
<tr>
<td>M-DEV</td>
<td></td>
<td></td>
<td>2.9%</td>
<td>0.01</td>
<td>[-0.01, 0.02]</td>
<td>0.469 - 0.475</td>
</tr>
<tr>
<td>M-TREC_2019</td>
<td></td>
<td></td>
<td>1.6%</td>
<td>0.03</td>
<td>[-0.05, 0.12]</td>
<td>0.754 + 0.786</td>
</tr>
<tr>
<td>M-TREC_2020</td>
<td></td>
<td></td>
<td>2.2%</td>
<td>0.00</td>
<td>[-0.05, 0.06]</td>
<td>0.758 - 0.762</td>
</tr>
<tr>
<td>M-TREC-Hard</td>
<td></td>
<td></td>
<td>1.7%</td>
<td>0.03</td>
<td>[-0.05, 0.11]</td>
<td>0.769 - 0.800</td>
</tr>
<tr>
<td>M-TREC_2021</td>
<td></td>
<td></td>
<td>1.9%</td>
<td>0.04</td>
<td>[-0.03, 0.11]</td>
<td>0.718 + 0.755</td>
</tr>
<tr>
<td>M-TREC_2022</td>
<td></td>
<td></td>
<td>1.9%</td>
<td>0.05</td>
<td>[-0.02, 0.12]</td>
<td>0.650 - 0.699</td>
</tr>
<tr>
<td>M-V2_DEV</td>
<td></td>
<td></td>
<td>2.9%</td>
<td>0.01</td>
<td>[-0.01, 0.02]</td>
<td>0.202 - 0.210</td>
</tr>
<tr>
<td>M-V2_DEV2</td>
<td></td>
<td></td>
<td>2.9%</td>
<td>0.01</td>
<td>[-0.01, 0.02]</td>
<td>0.213 + 0.220</td>
</tr>
<tr>
<td>B-arguana</td>
<td></td>
<td></td>
<td>2.7%</td>
<td>-0.22</td>
<td>[-0.25, -0.19]</td>
<td>0.514 - 0.294</td>
</tr>
<tr>
<td colspan="2">B-climate-fever</td>
<td></td>
<td>2.8%</td>
<td>0.05</td>
<td>[0.03, 0.07]</td>
<td>0.208 - 0.256</td>
</tr>
<tr>
<td colspan="2">B-dbpedia</td>
<td></td>
<td>2.6%</td>
<td>0.02</td>
<td>[-0.01, 0.05]</td>
<td>0.573 -+ 0.593</td>
</tr>
<tr>
<td colspan="2">B-fever</td>
<td></td>
<td>2.9%</td>
<td>0.08</td>
<td>[0.07, 0.09]</td>
<td>0.784 - 0.864</td>
</tr>
<tr>
<td colspan="2">B-fiqa</td>
<td></td>
<td>2.5%</td>
<td>0.11</td>
<td>[0.07, 0.15]</td>
<td>0.373 -+ 0.481</td>
</tr>
<tr>
<td>B-hotpotqa</td>
<td></td>
<td></td>
<td>2.9%</td>
<td>0.05</td>
<td>[0.04, 0.06]</td>
<td>0.690 -+ 0.742</td>
</tr>
<tr>
<td>B-nfcorpus</td>
<td></td>
<td></td>
<td>2.2%</td>
<td>0.02</td>
<td>[-0.03, 0.07]</td>
<td>0.358 - 0.376</td>
</tr>
<tr>
<td>B-nq</td>
<td></td>
<td></td>
<td>2.8%</td>
<td>0.07</td>
<td>[0.05, 0.09]</td>
<td>0.586 -+ 0.657</td>
</tr>
<tr>
<td>B-quora</td>
<td></td>
<td></td>
<td>2.9%</td>
<td>0.03</td>
<td>[0.02, 0.04]</td>
<td>0.813 -+ 0.843</td>
</tr>
<tr>
<td>B-scidocs</td>
<td></td>
<td></td>
<td>2.8%</td>
<td>0.03</td>
<td>[0.02, 0.05]</td>
<td>0.158 - 0.192</td>
</tr>
<tr>
<td>B-scifact</td>
<td></td>
<td></td>
<td>2.0%</td>
<td>0.04</td>
<td>[-0.02, 0.10]</td>
<td>0.711 + 0.750</td>
</tr>
<tr>
<td>B-TREC_Covid</td>
<td></td>
<td colspan="2">1.9%</td>
<td>0.11</td>
<td>[0.04, 0.17]</td>
<td>0.774 - 0.880</td>
</tr>
<tr>
<td>B-Touche</td>
<td></td>
<td></td>
<td>1.9%</td>
<td>0.00</td>
<td>[-0.07, 0.07]</td>
<td>0.756 - 0.759</td>
</tr>
<tr>
<td>L-Lifestyle-S</td>
<td></td>
<td></td>
<td>2.6%</td>
<td>0.09</td>
<td>[0.05, 0.12]</td>
<td>0.629 -+ 0.715</td>
</tr>
<tr>
<td>L-Pooled-S</td>
<td></td>
<td></td>
<td>2.9%</td>
<td>0.09</td>
<td>[0.08, 0.11]</td>
<td>0.532 - 0.626</td>
</tr>
<tr>
<td>L-Recreation-S</td>
<td></td>
<td></td>
<td>2.6%</td>
<td>0.11</td>
<td>[0.08, 0.14]</td>
<td>0.549 -+ 0.662</td>
</tr>
<tr>
<td>L-Science-S</td>
<td></td>
<td></td>
<td>2.5%</td>
<td>0.08</td>
<td>[0.04, 0.12]</td>
<td>0.398 -+ 0.473</td>
</tr>
<tr>
<td>L-Technology-S</td>
<td></td>
<td></td>
<td>2.5%</td>
<td>0.09</td>
<td>[0.06, 0.13]</td>
<td>0.465 - 0.560</td>
</tr>
<tr>
<td>L-Writing-S</td>
<td></td>
<td></td>
<td>2.7%</td>
<td>0.09</td>
<td>[0.06, 0.11]</td>
<td>0.615 - 0.702</td>
</tr>
<tr>
<td>L-Lifestyle-F</td>
<td></td>
<td></td>
<td>2.8%</td>
<td>0.13</td>
<td>[0.11, 0.15]</td>
<td>0.478 - 0.609</td>
</tr>
<tr>
<td>L-Pooled-F</td>
<td></td>
<td></td>
<td>2.9%</td>
<td>0.11</td>
<td>[0.10, 0.11]</td>
<td>0.358 - 0.463</td>
</tr>
<tr>
<td>L-Recreation-F</td>
<td></td>
<td></td>
<td>2.8%</td>
<td>0.13</td>
<td>[0.11, 0.16]</td>
<td>0.474 - 0.609</td>
</tr>
<tr>
<td>L-Science-F</td>
<td></td>
<td></td>
<td>2.8%</td>
<td>0.07</td>
<td>[0.06, 0.09]</td>
<td>0.198 - 0.270</td>
</tr>
<tr>
<td>L-Technology-F</td>
<td></td>
<td></td>
<td>2.8%</td>
<td>0.09</td>
<td>[0.07, 0.11]</td>
<td>0.246 - 0.337</td>
</tr>
<tr>
<td>L-Writing-F</td>
<td></td>
<td></td>
<td>2.8%</td>
<td>0.10</td>
<td>[0.08, 0.12]</td>
<td>0.470 - 0.566</td>
</tr>
<tr>
<td>Antique</td>
<td></td>
<td></td>
<td>2.6%</td>
<td>0.03</td>
<td>[-0.01, 0.06]</td>
<td>0.715 - 0.740</td>
</tr>
<tr>
<td>TREC-CAR-auto</td>
<td></td>
<td></td>
<td>2.8%</td>
<td>-0.03</td>
<td>[-0.05, -0.01]</td>
<td>0.347 - 0.320</td>
</tr>
<tr>
<td>TREC-CAR-manual</td>
<td></td>
<td></td>
<td>2.7%</td>
<td>-0.02</td>
<td>[-0.05, 0.00]</td>
<td>0.693 + 0.670</td>
</tr>
<tr>
<td>DPR-NQ</td>
<td></td>
<td></td>
<td>2.9%</td>
<td>0.06</td>
<td>[0.04, 0.07]</td>
<td>0.447 -+ 0.503</td>
</tr>
<tr>
<td colspan="2">DPR-TriviaQA</td>
<td></td>
<td>2.9%</td>
<td>0.03</td>
<td>[0.02, 0.04]</td>
<td>0.358 - 0.390</td>
</tr>
<tr>
<td>Mr. TyDi English</td>
<td></td>
<td></td>
<td>2.5%</td>
<td>0.08</td>
<td>[0.04, 0.12]</td>
<td>0.384 - 0.465</td>
</tr>
<tr>
<td>Summary Effect (RE)</td>
<td></td>
<td></td>
<td></td>
<td>0.05</td>
<td>[0.03, 0.06]</td>
<td>0.518 + 0.566</td>
</tr>
<tr>
<td colspan="4">-0.2 -0.1 0.0 0.1 Mean Difference</td>
<td></td>
<td></td>
<td></td>
</tr>
</table>


<!-- PageNumber="8" -->

[13] C. Lassance and S. Clinchant. The tale of two msmarco - and their unfair comparisons. In
Proceedings of the 46th International ACM SIGIR Conference on Research and Development in
Information Retrieval, SIGIR '23, page 2431-2435, New York, NY, USA, 2023. Association
for Computing Machinery.

[14] S .- C. Lin, J .- H. Yang, and J. Lin. Distilling dense representations for ranking using tightly-
coupled teachers, 2020.

[15] S. MacAvaney, A. Yates, S. Feldman, D. Downey, A. Cohan, and N. Goharian. Simplified data
wrangling with ir_datasets. In SIGIR, 2021.

[16] V. Sanh, L. Debut, J. Chaumond, and T. Wolf. Distilbert, a distilled version of bert: smaller,
faster, cheaper and lighter, 10 2019.

[17] K. Santhanam, O. Khattab, J. Saad-Falcon, C. Potts, and M. Zaharia. ColBERTv2: Effective and
efficient retrieval via lightweight late interaction. In M. Carpuat, M .- C. de Marneffe, and I. V.
Meza Ruiz, editors, Proceedings of the 2022 Conference of the North American Chapter of the
Association for Computational Linguistics: Human Language Technologies, pages 3715-3734,
Seattle, United States, July 2022. Association for Computational Linguistics.

[18] M. Sertkan, S. Althammer, and S. Hofstätter. Ranger: A toolkit for effect-size based multi-task
evaluation. arXiv preprint arXiv:2305.15048, 2023.

[19] M. Sertkan, S. Althammer, S. Hofstätter, P. Knees, and J. Neidhardt. Exploring effect-size-based
meta-analysis for multi-dataset evaluation. 2023.

[20] N. Thakur, N. Reimers, A. Rücklé, A. Srivastava, and I. Gurevych. Beir: A heterogenous bench-
mark for zero-shot evaluation of information retrieval models. arXiv preprint arXiv:2104.08663,
2021.

[21] H. Zeng, H. Zamani, and V. Vinay. Curriculum learning for dense retrieval distillation. In
Proceedings of the 45th International ACM SIGIR Conference on Research and Development in
Information Retrieval, pages 1979-1983, 2022.

