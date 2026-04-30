# jina-embeddings-v5-text-nano モデル情報レポート

**論文**: jina-embeddings-v5-text: Task-Targeted Embedding Distillation (arXiv:2602.15547, 2026-02)
**著者/所属**: Mohammad Kalim Akram, Saba Sturua, Nastia Havriushenko, Quentin Herreros, Michael Günther, Maximilian Werk, Han Xiao(いずれも Jina AI GmbH, ベルリン)
**URL**: https://arxiv.org/abs/2602.15547
**モデルカード**: https://huggingface.co/jinaai/jina-embeddings-v5-text-nano

---

## モデルについて

### 開発組織
- **値**: Jina AI GmbH(ドイツ・ベルリン)
- **背景**: `jina-embeddings` シリーズの最新世代 v5。v3(Jina AI 独自の 572M XLM-RoBERTa 系バックボーン)、v4(Qwen2.5-VL ベースのマルチモーダル大型モデル)に続き、v5 で再び「小型・高効率」路線へ回帰し、同時に「タスク特化蒸留」という新しい学習レシピを提示している。

### 公開年月
- **値**: arXiv 初版は 2026-02-17。Hugging Face モデルウェイト公開は 2026-02-18。
- **背景**: 2026 年初頭の同サイズ帯(<500M)競合である Google の `embeddinggemma-300m`(2025 末)、Qwen3-Embedding-0.6B(2025 末)、`snowflake-arctic-embed-l-v2`、`KaLM-mini-v2.5` などに対し、より小さいパラメータで上回ることを狙ったリリース。

### 使用したベースモデル
- **値**: EuroBERT-210M(~212M パラメータ)
- **モデルの特徴**: EuroBERT は欧州中心の 15 言語(英・仏・独・西・中・伊・露・波・葡・日・越・蘭・阿・土・印)に対応した encoder-only の多言語 BERT 系。RoPE を使用し、長文適応性を重視した最新の bidirectional encoder。
- **採用の背景**: 同シリーズの小型兄弟機 `jina-embeddings-v5-text-small` は 119 言語対応の Qwen3-0.6B(decoder-only)を採用するが、nano は decoder 系ではなく encoder 系を選んでいる。これは (1) パラメータあたりの表現密度で encoder の方が効率的、(2) embedding 専用途ではデコーダのオートレグレッシブ能力は不要、(3) ヨーロッパ地域市場を意識した多言語カバレッジ、という三点が背景。

### モデルアーキテクチャ
- **位置埋め込み方式**: RoPE(Rotary Position Embedding)。学習時 theta=250K、推論時はより大きな theta へ切り替えて長文外挿性能を補強。
- **Transformer ブロック数**: EuroBERT-210M 準拠(正確な層数は論文中明記なし、EuroBERT-210M の標準構成が踏襲)。
- **LoRA アダプタの有無**: あり。4 タスク(非対称検索 / STS / クラスタリング / 分類)ごとに独立した LoRA アダプタ(rank=32, alpha=32)を搭載。nano ではアダプタ総計 4×6.7M ≒ 26.8M 追加(small は 4×20.2M)。推論時は該当タスクのアダプタのみがアクティブになり、残りは凍結。
- **背景**: ベースバックボーンを凍結したまま各タスクに特化した変換を後付けする「タスクアダプタ」方式は v3 から継承。共有バックボーンの知識を保ちつつタスクごとの最適化を両立する。

### モデルのパラメータ数
- **値**: ベース 212M + アダプタ合計 約 26.8M = 合計 **約 239M**。公式モデルカードは「239M」と表記。
- **背景**: 500M 未満の公開モデルとして最小クラス。教師モデル Qwen3-Embedding-4B の約 17 分の 1 に蒸留されている。

### 最大コンテキスト長
- **値**: 論文では 32,000 トークンをサポートと主張。モデルカードの `max_seq_length` は 8192 トークン(RoPE の theta 調整による外挿で実用上 32k まで拡張可能)。
- **背景**: 学習時のコンテキスト窓と推論時の外挿窓を分けた二段階構成。長文専用の追加学習段階で 1,000–4,096 トークンの長文データを用い、RoPE theta 切替で 32k まで安定化させている。

### 出力ベクトルの次元数
- **値**: 768 次元(フル)。Matryoshka 表現学習により 32 / 64 / 128 / 256 / 512 / 768 次元へ truncation 可能。
- **背景**: Qwen3 ベースの small は 1024 次元、nano は EuroBERT 由来の 768 次元。`truncate_dim` 引数で任意サイズに切り詰めても性能が劣化しにくいよう MRL で学習。

### 学習したタスク
- 非対称検索(query ↔ document の非対称コサイン類似度)
- Semantic Text Similarity(STS, 対称類似度の段階評価)
- クラスタリング
- 分類
- Text Matching(モデルカード上はこれを STS 系アダプタとして公開)

### Instruction Tuning への対応
- **対応**: 限定的にあり。ただし教師モデル Qwen3-Embedding-4B のような複雑なタスク記述は使わず、非対称検索は `Query:` / `Document:` プレフィックス、それ以外は `Document:` 単一プレフィックスという**最小指示**のみ。タスク指定は `task=` 引数(retrieval / text-matching / classification / clustering)で LoRA アダプタを切り替える方式。
- 論文のアブレーションでは、豊富な指示を使わないこの方式が分類タスクで不利になる一方、検索/STS では十分な精度を達成できることが示されている。

### マトリョーシカ表現学習(MRL)の対応
- **対応**: あり。32, 64, 128, 256, 512, 768 の各次元で truncation してもスコア劣化を最小化する学習を適用。
- バイナリ量子化に対する頑健性も、後述の GOR 正則化とセットで確保。

### 多言語対応かどうか
- **対応言語数**: 15 言語(EuroBERT バックボーン由来)。英語、フランス語、ドイツ語、スペイン語、中国語、イタリア語、ロシア語、ポーランド語、ポルトガル語、日本語、ベトナム語、オランダ語、アラビア語、トルコ語、ヒンディー語。
- **背景**: 同シリーズ small(Qwen3-0.6B, 119 言語)と比較すると言語カバレッジは狭いが、欧州中心の主要言語では高い性能を示す。MMTEB でのスコア(65.5)が実質的にこのサブセットで測定されたもの。

---

## モデルの訓練方法

### 損失関数
- **InfoNCE(検索用)**: temperature-scaled cosine similarity を用いた対照学習。in-batch negatives に加えて mined hard negatives を合流。
- **CoSENT Ranking Loss(STS 用)**: listwise に予測類似度とゴールド順序を整列させる。段階ラベル(graded similarity)を生かすため。スコア付きデータがないときは対照学習版に切替。
- **Embedding-based Distillation**: 線形射影 ψ で学生埋め込みを教師側空間に写像し、教師埋め込みとのコサイン距離を最小化。**論文の中核的な主張**として、score-based distillation(類似度行列の MSE)よりも embedding-based の方が最終検索性能で勝ると結論づけている。
- **Score-based Distillation**: 比較対象として評価されたが採用せず(性能が伸び悩む)。
- **Relational Knowledge Distillation**: 分類アダプタの feature collapse を防ぐための追加正則化。
- **背景**: 「対照学習だけ」「蒸留だけ」ではなく、両者をタスクごとに最適な比率で組み合わせる点が v5 の新規性。

### 正則化
- **Global Orthogonal Regularizer(GOR)**: 埋め込みがベクトル空間に一様に散らばるように促進。バイナリ量子化に対する頑健性の源。
- **Matryoshka Loss**: 各 truncation 次元で再計算した対照損失を集約。
- **Relational KD**: 分類アダプタで、教師側のサンプル間関係を学生側でも保つ。
- **Model Weight Averaging**: チェックポイント平均によるアンサンブル的な汎化。

### プーリング戦略
- **Last-token pooling**(end-of-sequence トークンの埋め込みを使用)。
- **背景**: EuroBERT は encoder-only だが、本論文では EOS トークン位置の隠れ状態を最終表現として採用している(Qwen3 系の decoder と表現方法を揃えるため、という設計意図と推察される)。

### 訓練パイプライン
- **Stage 1 — 汎用埋め込み蒸留**: 教師 Qwen3-Embedding-4B からの埋め込み蒸留で、300+ データセット・30+ 言語からの多様なテキストに対し学生を学習。続いて長文特化の追加学習段階で 1,000–4,096 トークン文書に対応。
- **Stage 2 — タスク特化アダプタ学習**: ベース重みを凍結し、4 つの LoRA アダプタを各タスク固有の損失で学習。
  - Retrieval: InfoNCE + 埋め込み蒸留 + GOR
  - STS: CoSENT ranking(あるいは対照損失にフォールバック)
  - Clustering: クラスタリング用教師指示での特化蒸留
  - Classification: 双方向対照損失 + Relational KD

### 訓練に適用した方式
- **値**: バッチサイズ 8×512(8 デバイス × 512 サンプル)、長文データでは動的調整。
- **記載なし**: FlashAttention、DeepSpeed、FSDP、bf16 等の具体的な最適化スタックは論文中で明示されていない(本論文は学習レシピに焦点を置き、エンジニアリング詳細は省略)。

### 訓練データの構成と品質
- **規模**: 300 を超えるデータセット、30+ 言語。
- **種類**: (1) (query, positive, hard-negatives) のトリプレット検索データ、(2) STS12/SICK と機械翻訳版、(3) 分類データセットをトリプレット化したもの、(4) 対訳/パラフレーズ、(5) 長文専用の 1,000–4,096 トークン収集コーパス。
- **合成データ**: LLM 生成クエリと自然な長文(書籍チャプター等)をペアリングした long-context 合成データを使用。ノイズの多い密な長文下での検索耐性を狙った設計。

### ハードネガティブマイニングの手法
- **値**: InfoNCE 内で in-batch negatives に加え、事前にマイニングした意味的に近いが不正解の文書(mined hard negatives)を注入。
- **マイニング元モデル**: 論文上は明示されないが、文脈から教師 Qwen3-Embedding-4B または jina-embeddings-v3/v4 の系列モデルを用いた ANN ベースマイニングと考えられる。
- **段階**: Stage 2 の Retrieval アダプタ学習時に特に重要。

---

## モデルの評価

### ベンチマークスコア

**MTEB English v2(平均)**
- jina-embeddings-v5-text-nano (239M): **71.0**(Classification 89.7 / Retrieval 58.8 / STS 88.3)
- KaLM-mini-v2.5 (494M): 71.3
- embeddinggemma-300m (308M): 69.7
- jina-embeddings-v3 (572M): 65.7

**MMTEB(多言語, 平均)**
- jina-embeddings-v5-text-nano (239M): **65.5**(Retrieval 81.9 / STS 63.3)
- embeddinggemma-300m: 61.1
- KaLM-mini-v2.5: 60.1
- jina-embeddings-v3: 58.4

**BEIR / LongEmbed**
- BEIR: 64.08(embeddinggemma 63.75, KaLM 56.51 を上回る)
- LongEmbed: **63.65**(embeddinggemma 55.29, KaLM 43.35 を大きく引き離す)

**相対的な強み**
- 500M 未満のモデル群で検索・再ランキングの最高性能。
- 特に長文検索(LongEmbed)で +8〜20 ポイント差、MRL による truncation 後でもスコア劣化が小さい点が差別化要因。
- 一方、Classification では KaLM-mini-v2.5(90.5)や embeddinggemma(87.6)に対し僅差で劣る局面もあり、最小指示方式のトレードオフが出ている。

---

## 論文

### 今回の発表の目新しいポイント
1. **タスク特化蒸留(Task-Targeted Embedding Distillation)**: 検索/STS/クラスタリング/分類ごとに蒸留と対照学習の組合せを変え、タスク固有に最適化する学習レシピを提案。
2. **Embedding-based distillation > Score-based distillation**: 埋め込みそのものを蒸留対象にする方が、類似度行列の蒸留よりも最終検索性能で勝ることを実証。
3. **超小型で SOTA クラス**: 239M で MTEB-v2 英語 71.0 / MMTEB 65.5 を達成し、2–3 倍サイズのモデルを多くの指標で上回る。
4. **Truncation & 量子化耐性**: MRL + GOR の組合せで、次元切詰やバイナリ量子化後もスコアが大きく落ちない実装。
5. **長文対応の二段構え**: 学習時の短い RoPE theta と推論時の大きな theta で 32k トークン外挿を実用化。

### 先行研究(Related Work)の要約
- **汎用蒸留系**: DistilBERT / MiniLM / TinyBERT は言語モデル一般の蒸留で、埋め込み品質の直接最適化は行っていない。EmbedDistill や Jasper/Stella はより埋め込みに近いが、タスク別の細かい調整は提供していなかった。本論文はこれらを「タスク非依存で蒸留」する系譜として整理し、タスクごとに損失を切り替える点で差別化。
- **同規模の対照学習系**: multilingual-e5-large-instruct、snowflake-arctic-embed-l-v2、BGE-M3 は大規模な対照学習で高い多言語性能を示すが、サイズが 500M 超か、あるいは長文対応に弱い。本論文は 239M で同等以上を達成。
- **teacher-student 同ファミリ**: Qwen3-Embedding-0.6B/4B は強力な教師として採用され、本論文の学生モデルはそれを大きく下回らない位置まで縮約される。
- **前世代自モデル**: jina-embeddings-v3 (572M) と v4 (マルチモーダル大型) と比較し、v5-nano は半分以下のサイズで英語・多言語ともに上回る。
- **クロージングの差分**: 既存小型モデルが「対照学習 + 軽い蒸留」で済ませていたのに対し、本論文は「タスクごとに蒸留形態と損失を切り替える」フレームワークで精度を押し上げた点が中心的な貢献。

---

## まとめ表

| 項目 | 値 |
|--|--|
| 開発組織 | Jina AI GmbH(ベルリン) |
| 公開年月 | 2026-02(arXiv v1: 2026-02-17, HF 公開: 2026-02-18) |
| 使用したベースモデル | EuroBERT-210M(encoder-only, 15 言語) |
| 位置埋め込み方式 | RoPE(学習時 theta=250K / 推論時大きめ theta で 32k 外挿) |
| Transformer ブロック数 | EuroBERT-210M 準拠(論文中に明示なし) |
| LoRA アダプタの有無 | あり(4 タスク × rank 32 / alpha 32、nano で約 26.8M 追加) |
| モデルのパラメータ数 | ベース 212M + アダプタ 約 26.8M = 約 239M |
| 最大コンテキスト長 | 論文 32,000 tok / モデルカード 8,192 tok(RoPE 外挿で 32k 主張) |
| 出力ベクトルの次元数 | 768(MRL で 32/64/128/256/512/768 に可変) |
| 学習したタスク | 非対称検索 / STS(text-matching) / クラスタリング / 分類 |
| Instruction Tuning 対応 | 最小限(`Query:` / `Document:` プレフィックス + task 引数でアダプタ切替) |
| MRL 対応 | あり(truncation + バイナリ量子化耐性) |
| 多言語対応 | 15 言語(英・仏・独・西・中・伊・露・波・葡・日・越・蘭・阿・土・印) |
| 損失関数 | InfoNCE / CoSENT / Embedding-based Distillation / Relational KD |
| プーリング戦略 | Last-token pooling(EOS トークン位置) |
| 訓練パイプライン | Stage1: 汎用埋め込み蒸留 → Stage2: 4 タスク別 LoRA アダプタ学習 |
| ハードネガティブマイニング | mined hard negatives + in-batch negatives(Retrieval アダプタ学習時) |
| 正則化 | Global Orthogonal Regularizer, Matryoshka loss, Relational KD, weight averaging |
| 主要ベンチマーク | MTEB-v2 英語 71.0 / MMTEB 65.5 / BEIR 64.08 / LongEmbed 63.65(<0.5B でトップクラス) |
| ライセンス | CC BY-NC 4.0(商用利用は Jina AI セールス問合せ) |
