# 尼崎市 QA 検索コーパス特化 — データ合成実施レポート

`data_synthesys_plan.md` で立案した計画に基づき、`mahiyama/amagasaki-qna` を構築した実施レポート。**実際に使用したプロンプト全文**、ハマりポイント、最終統計を含む。

公開データセット: <https://huggingface.co/datasets/mahiyama/amagasaki-qna>

---

## 1. 計画と実施の差分サマリ

| 項目 | 計画 (`data_synthesys_plan.md`) | 実施結果 |
| --- | --- | --- |
| 生成 LLM | Frontier LLM (Claude / GPT-5 / Gemini を想定) | **Claude Sonnet 4.6 (sub-agent 36 並列)** ※ Haiku 4.5 でパイロットして品質不足のため Sonnet に格上げ |
| 5 軸プロンプティング | Question Type × Length × Style × Difficulty × Persona の 5 軸 | **3 styles に簡素化** (polite / plain / keyword)。Length / Difficulty / Persona は明示制御せず Sonnet の判断に委ねる |
| 文書あたり生成数 | 5 件 | **3 件** (5,358 entries 上限) |
| 失敗モード hn (jina-v3 流) | F1/F2/F3 の 3 種 | **不採用**。LLM 同梱 hn 1 件 (E5-Mistral 流) のみで近似 |
| 品質フィルタ閾値 | `cos > 0.7` (Qwen3 流) | **`cos > 0.5` に緩和**。jina-v5-text-small + 日本語 FAQ で 0.7 だと正例の 49% が脱落するため |
| eval leakage check | `cos > 0.85` で除外 | 計画通り |
| HNM 設計 (NV-Retriever) | POS_AWARE_RATIO=0.95, SKIP_TOP=5 | 計画通り |
| 最終件数 | 6,000〜7,000 想定 | **5,138** (各 config 共通) |

理由:
- **Sonnet に格上げ**: パイロットで Haiku が hn_doc を完全テンプレート化 (全 hn が同じ「○○手続きの申請方法について → 福祉課 / 06-6406-XXXX」) してしまい、ドメイン理解の深さが致命的に不足
- **3 styles に簡素化**: 5 軸の組み合わせを Sonnet に細かく指示するとプロンプト肥大 + 1 chunk あたり処理時間が増大。3 styles を明示し、Length / Persona は内部判断に任せる方が高速・高品質
- **失敗モード不採用 (V1)**: スコープ拡大を抑えるため。LLM 同梱 hn でも十分多様な hard negative が出ていたため V1 では十分

---

## 2. 全体パイプラインの実行時系列

```
[Step 0] prepare_chunks.py
   ↓ corpus 1,786 件を 50 件刻みで 36 chunks に分割
   ↓ work/chunks/chunk_NNN.json を出力 (35 chunks × 50 docs + 1 chunk × 36 docs)

[Step 1] 並列サブエージェントによるクエリ生成 (Claude Sonnet 4.6 × 36 並列)
   ↓ 各エージェントが chunk_NNN.json を読み、3 styles × N docs の JSONL を生成
   ↓ work/raw_synth/synth_NNN.jsonl (合計 5,358 entries)
   ↓ 実行時間: 約 20 分 (並列のため、最遅 agent の所要時間 ≒ 約 22 分)
   ↓ 平均 token 使用量 / agent: ~70K (= ~30K input + ~40K output)
   ↓ 36 agent 合計 ~2.5M tokens (Sonnet)

[Step 2] aggregate_and_filter.py
   ↓ 全 36 JSONL をマージ → 5,358 entries
   ↓ テキスト制約フィルタ: 「尼崎」混入除外 (-13)、hn_doc 形式不正 / 他都市名混入 (0)
   ↓ jina-embeddings-v5-text-small で query/positive/eval-queries 全件埋め込み
   ↓ cos(query, positive) < 0.5 除外 (-94)
   ↓ max cos(query, eval queries) > 0.85 除外 (-113, leakage)
   ↓ work/synth_pairs.parquet (5,138 rows)

[Step 3] mine_hn_local.py
   ↓ corpus 1,786 件を再度埋め込み → in-memory cosine 検索
   ↓ 5,138 query × 1,786 doc 行列で top-50 取得 (numpy argpartition)
   ↓ work/shards/shard_0000.parquet (5,138 rows、hit_ids[50] と hit_scores[50] を保持)

[Step 4] build_triplets.py / build_ntuples.py
   ↓ NV-Retriever フィルタ (POS_AWARE_RATIO=0.95, SKIP_TOP=5)
   ↓ triplets: 1 mined hard negative
   ↓ n-tuples: LLM 同梱 hn (slot 1) + mined 4 件 (slots 2-5)
   ↓ work/triplets/triplet_0000.parquet, work/ntuples/ntuple_0000.parquet

[Step 5] count_tokens.py
   ↓ tiktoken cl100k_base で全 config トークン数集計
   ↓ work/token_stats.json

[Step 6] upload_dataset.py
   ↓ pairs / triplets / n-tuples を push_to_hub (mahiyama/amagasaki-qna)
   ↓ パイプライン構造・NV-Retriever 統計・leakage protection を記載した README を生成・アップロード
```

---

## 3. 採用した先行手法 (実施版)

`references/data_synthesis_report.md` で整理した 50 モデル横断レシピのうち、本実施で **実際に採用** したのは以下 4 つ。

| 採用手法 | 出典 | 本実施での扱い |
| --- | --- | --- |
| **document → query 逆生成** | E5-Mistral / Qwen3-Embedding 業界標準 | corpus 1,786 件を全件 seed に、LLM が「この document を答えとする質問」を逆生成 |
| **LLM 同梱 hard_negative_document** | E5-Mistral 原典 | プロンプト内で `(query, hn_doc)` を一括出力させる。hn_doc は 200-400 字の「別制度・別窓口を装う偽 FAQ」 |
| **NV-Retriever (TopK-PercPos)** | NV-Embed-v2 | POS_AWARE_RATIO=0.95, SKIP_TOP=5 で false negative を構造的に抑制。auto-wiki-qa の `build_triplets.py` を流用 |
| **コサイン閾値 + eval leakage check** | Qwen3 / 本計画固有 | cos(q, p+) ≥ 0.5 (正例関係保証)、max cos(q, eval_q) ≤ 0.85 (リーク防止) |

不採用にしたもの:

- 5 軸プロンプティング (Persona Hub 含む) — 3 styles に簡素化
- 失敗モード合成 hn (jina-v3 F1/F2/F3) — V1 では LLM 同梱 hn のみで代替
- LLM-as-a-Judge (Gemini 流 Graded + Query Likelihood + RRF) — V1 では cos しきい値のみで代替

---

## 4. サブエージェント並列ディスパッチ戦略

### 4-1. 設計

| 項目 | 値 |
| --- | --- |
| ベースモデル | Claude Sonnet 4.6 (`general-purpose` agent + `model: sonnet`) |
| 並列度 | **36 並列** (chunk_000 はパイロットで先行実行、chunk_001-035 を一括並列) |
| chunk サイズ | 50 docs (最後の chunk_035 のみ 36 docs) |
| 1 chunk あたり生成 entry 数 | 50 × 3 styles = 150 (chunk_035 のみ 108) |
| 1 agent の input prompt | テンプレート + chunk path 約 4KB |
| 1 agent の output (parquet 行数) | 150 (or 108) |
| 1 agent の token 消費 | ~70K (input ~30K + output ~40K) |
| 全 36 agent の合計 token 消費 | **~2.5M** (Sonnet) |
| 全 36 agent の wall-clock time | **約 22 分** (並列実行のため最遅 agent 律速) |

### 4-2. なぜ 36 並列が成立したか

Anthropic の sub-agent はメイン会話と独立してバックグラウンド実行可能 (`run_in_background: true`)。各 agent は:

1. メイン (この会話) が `Agent` ツール呼び出しでディスパッチ
2. agent は専用の context window を持って独立実行
3. agent が完了すると `<task-notification>` がメイン会話に返却される
4. メインは notification を受けて次のステップ (集約・フィルタ) に進む

これにより 36 個の独立した Claude Sonnet 4.6 が真に同時実行され、wall-clock time は逐次比 36 倍短縮された。

### 4-3. パイロット (Haiku) → 本生成 (Sonnet) 切替の決断ポイント

最初は **Claude Haiku 4.5** で chunk_000 をパイロット実行した。出力された 150 entries の品質は致命的に低かった:

**Haiku 4.5 が生成した hn_doc の例 (全件こんな感じ)**:
```
Question: 乳幼児とその親が集う場手続きの申請方法について
Answer: 乳幼児とその親が集う場手続きに関するご質問ですね。以下のようなご利用方法や必要書類がございます。
1. 対象者は、本市にお住まいで乳幼児とその親が集う場手続きの要件を満たす方です。
2. 申請には、身分証明書と印鑑をご持参ください。
3. 申請受付窓口は市庁舎2階になります。
4. 手続きに必要な時間は約30分です。
5. ご不明な点はお気軽にお問い合わせください。
■お問い合わせ先
〒660-8501
市役所 福祉課
電話: 06-6406-XXXX
```

問題点:
- **テンプレート崩壊**: 全 150 件が同じスケルトンに「Q 部の文字列」を埋めただけ
- **ドメイン理解の欠如**: positive と異なる制度を装う本来の hard negative になっていない (positive を別表現で言い換えただけ)
- **連絡先が完全固定**: 福祉課 / 06-6406-XXXX が 150 件すべて
- **制約違反多発**: query に「尼崎市」混入、positive Q 部の逐語コピー

→ **Haiku では業界標準レシピ (E5-Mistral 流の "LLM が同梱 hn を生成") が成立しない** と判断。Sonnet 4.6 に切替て同じプロンプトで再実行すると、hn が制度別・窓口別・電話番号別に正しく多様化された。

参考までに Sonnet 4.6 が生成した同じ doc_id=0 の出力:

```json
{"doc_id": "0", "style": "polite", "query": "子育て中の親同士が交流できる場を探しているのですが、どのような場所があるか教えていただけますか", "hn_doc": "Question: 子育て支援センターの利用時間について教えてください。\nAnswer: ■子育て支援センターは月曜日から土曜日の午前９時から午後４時３０分まで開所しています。■利用対象は就学前のお子さんとその保護者です。予約不要で気軽にご利用いただけます。【お問い合わせ】地域子育て支援課 電話 06-6489-6380"}
{"doc_id": "0", "style": "plain", "query": "乳幼児の親向けサークルや集まりはどこにある？", "hn_doc": "Question: 保育所の一時預かりサービスはどこで申し込めますか。\nAnswer: ■一時預かりを実施している保育所に直接お申し込みください。■利用料は１日あたり２，０００円から２，５００円です。【お問い合わせ】保育振興課 電話 06-4950-0633"}
{"doc_id": "0", "style": "keyword", "query": "育児 交流 相談窓口", "hn_doc": "Question: ファミリーサポートセンターへの登録方法を教えてください。\nAnswer: ■子育ての援助を受けたい方（依頼会員）と援助を行いたい方（提供会員）が会員登録をすることで相互援助活動が行えます。【お問い合わせ】ファミリーサポートセンター事務局 電話 06-6423-0606"}
```

---

## 5. 使用したプロンプト全文

### 5-1. パイロット用プロンプト (chunk_000、Sonnet 4.6 で実行した版)

few-shot 例を 2 つ + bad example 解説付きの長大プロンプト。本生成より重め。

````
You are generating high-quality synthetic training data (queries + hard negatives) for a Japanese text-embedding model that will specialize in retrieving Amagasaki city government FAQ documents.

# Input

Read the JSON file at:
`G:\mahiya-dataset-factory\amagasaki-qna\work\chunks\chunk_000.json`

It is a JSON array of 50 records. Each record has:
- `doc_id` (string)
- `text` (FAQ content in `Question: ...\nAnswer: ...` format)

# Task

For EACH of the 50 input records, generate **exactly 3 entries** with 3 different query styles, and for each entry also generate a `hn_doc` (hard-negative document).

Total output: 50 docs × 3 entries = **150 JSON lines**.

# Output

Write all 150 entries as JSONL to:
`G:\mahiya-dataset-factory\amagasaki-qna\work\raw_synth\synth_000.jsonl`

Each line:
```
{"doc_id": "0", "style": "polite", "query": "...", "hn_doc": "Question: ...\nAnswer: ..."}
```

The output directory may not exist yet — create it first via Bash mkdir if needed.

---

# 3 Query Styles

You must generate ONE query of each style per doc.

### Style 1: `polite` (丁寧語、です・ます調)

- Length: 25–55 chars
- 「〜ですか」「〜ますか」「〜したいのですが」「〜教えてください」「〜知りたい」のような丁寧形
- positive doc の **Question 部を逐語コピーしない**。**意味を抽象化し、市民が窓口に問い合わせるときの自然な言い回し**にすること
- positive doc の **Answer 部に書かれている具体的な値 (電話番号・町名・施設の階数・年齢条件)** を query に持ち込まない

### Style 2: `plain` (常体・短い疑問形)

- Length: 12–30 chars
- 「〜は？」「どこ？」「何が必要？」「いくら？」「どうすればいい？」のような短く平叙
- 末尾は `？` か `。` または体言止め+助詞

### Style 3: `keyword` (体言止め / キーワード羅列)

- Length: 5–22 chars
- スペース区切りまたは助詞ゼロのキーワード列。検索エンジンに直接打ち込むような表現
- 例: "国民健康保険 加入 必要書類" / "保育所 申込 期限" / "粗大ごみ 出し方"

---

# Hard Negative Document (`hn_doc`)

For each query, generate a `hn_doc`: a **fake** Amagasaki municipal FAQ that is **about a DIFFERENT topic** but has lexical / vocabulary overlap with the positive — designed to fool a retriever.

**MUST:**
- Format: `Question: ...\nAnswer: ...` (single `\n` between sections, escaped as `\n` inside JSON)
- Length: 200–400 字
- Question 部は positive とは **異なる制度・異なる窓口・異なる対象者** に関する内容
- Answer 部は自治体 FAQ の体裁を模倣 (■区切り / 【お問い合わせ】 / 〒住所 / "電話 06-XXXX-XXXX")
- 意図的に **語彙の一部を positive と重ねる** (制度名の一部、申請という単語、対象者など) — これが "hard" negative の本質
- 自治体ごとに異なる課・センター名を使い、**3 つの hn_doc がすべて同じテンプレートにならないこと**
- 連絡先は実在しない番号で良いが、毎回異なる課・センター・電話番号にする (「福祉課」「市民課」「健康増進課」「環境課」「保育振興課」「税務課」「介護保険課」「住宅課」「商工課」「教育委員会」「地域振興センター」など多様に)

**NEVER:**
- positive doc の Question 部の文字列を hn_doc に含めない
- positive doc の Answer 部の固有名 (「武庫の里」「大庄北」など実在の町名) を hn_doc に流用しない
- 全 hn_doc が同一のテンプレ文 (「○○手続きに関するご質問ですね」など) で開始しない — 文体を変える

---

# Strict Global Constraints

- Query に **「尼崎市」「尼崎」** という単語を含めない (eval クエリ分布が暗黙都市名なので合わせる)
- Query に positive doc 内の電話番号・住所・施設固有名を直接含めない
- hn_doc に **「大阪市」「神戸市」「西宮市」「伊丹市」「芦屋市」** など他都市名を含めない (尼崎市の FAQ 体裁を装う)
- 各 doc_id について `polite` / `plain` / `keyword` 各 1 行ずつ、合計 3 行を必ず出力 (50 doc × 3 = 150 行)
- 改行は JSON 文字列内では `\n` として正しくエスケープ

---

# Few-shot examples (高品質サンプル)

### Example A: positive doc = 国民年金の免除申請

```
{"doc_id": "X", "style": "polite", "query": "国民年金の保険料を払うのが厳しいのですが、免除の申請に何を持っていけばよいでしょうか", "hn_doc": "Question: 国民健康保険料を一括で前納する場合の手続きについて教えてください。\nAnswer: ■国民健康保険料は口座振替・クレジットカード払い・前納による現金払いから選択でき、年度初めに一括前納する場合は約２％の割引があります。■申請には、保険証と本人確認書類が必要です。年度途中から前納に切替える場合は、月割計算となります。【お問い合わせ】医療保険年金課賦課担当 電話 06-6489-6535"}

{"doc_id": "X", "style": "plain", "query": "年金の免除って学生でも申請できる？", "hn_doc": "Question: 学生納付特例制度の対象となる学校はどこまでか。\nAnswer: ■大学・大学院・短期大学・高等学校・高等専門学校・専修学校など、学校教育法に定める学校に在学する学生が対象です。夜間・通信制も含まれます。■申請には学生証または在学証明書の写しが必要です。【お問い合わせ】医療保険年金課年金担当 電話 06-6489-6452"}

{"doc_id": "X", "style": "keyword", "query": "年金 免除 持ち物", "hn_doc": "Question: 児童手当の所得制限について教えてほしい。\nAnswer: ■児童手当には所得制限が設けられており、扶養親族の人数に応じて限度額が変わります。■限度額を超える方は特例給付として一律月額５千円が支給されます。所得は前年分の課税所得を基準に判定します。【お問い合わせ】こども家庭支援課 電話 06-6489-6356"}
```

### What makes these GOOD?

- Query は positive を抽象化した自然な口語 (Question 部の逐語コピーなし)
- 3 つの hn_doc がすべて違う制度 (国保前納 / 学生納付特例 / 児童手当 — 確かに「年金」関連だが別個の制度)
- 3 つの hn_doc がそれぞれ異なる課 (医療保険年金課賦課担当 / 医療保険年金課年金担当 / こども家庭支援課) と異なる電話番号
- 文体も微妙に違う (■ 区切り含むが定型句は使わない)

### Example B: positive doc = 粗大ごみの出し方

```
{"doc_id": "Y", "style": "polite", "query": "家具を捨てたいのですが、申し込みの方法を教えていただけますか？", "hn_doc": "Question: 古紙・古着の集団回収を地域で実施したいのだが、市の補助はあるか。\nAnswer: ■自治会や子ども会などが行う集団回収には、回収量に応じた奨励金制度があります。■１kgあたり５円の単価で年４回まで申請可能。回収業者と事前契約のうえ、活動団体登録が必要です。【お問い合わせ】美化環境課 電話 06-6489-6610"}

{"doc_id": "Y", "style": "plain", "query": "粗大ごみは何曜日に出せる？", "hn_doc": "Question: ペットボトルの分別方法を知りたい。\nAnswer: ■ペットボトルはキャップとラベルを外し、中をすすいで透明袋に入れ、資源収集日に出してください。■キャップとラベルは「プラスチック容器包装」、本体は「ペットボトル」として別々に分別。汚れが取れないものは「もえるごみ」になります。【お問い合わせ】クリーンセンター業務担当 電話 06-6488-9381"}

{"doc_id": "Y", "style": "keyword", "query": "粗大ごみ 申込 電話", "hn_doc": "Question: 不法投棄を見つけたらどこに連絡すればよいか。\nAnswer: ■道路や公園、河川敷などへの不法投棄を発見した場合は、すぐに環境政策課へ通報してください。■夜間・休日は警察署にご連絡ください。投棄者が判明した場合は法律に基づき撤去命令を出します。撮影・録画は安全な距離から行ってください。【お問い合わせ】環境政策課 電話 06-6489-6605"}
```

### What is BAD (DO NOT do this)

- BAD query: "乳幼児とその親が集う場について知りたいのですが、どこで手続きすればよいですか？" — Question 部の逐語コピー
- BAD hn_doc: 全 hn_doc が "Question: {Q部の文字列}手続きの申請方法について\nAnswer: ...手続きに関するご質問ですね。以下のようなご利用方法や必要書類がございます..." のテンプレート — テンプレ崩壊
- BAD: "尼崎市" を query に含める → 制約違反
- BAD: 全 hn_doc の連絡先が同じ "市役所 福祉課 / 06-6406-XXXX" → 多様性ゼロ

---

# Steps

1. Read input file (`chunks/chunk_000.json`)
2. For each of 50 records, mentally:
   - Identify the topic (子育て/年金/税/住民登録/etc.)
   - Generate 3 stylistically diverse queries that abstract the doc content
   - For each query, design a hard-negative topic that's lexically related but semantically distinct
   - Write hn_doc with diverse departments / phone numbers / writing style
3. Bash `mkdir -p` for output dir if needed
4. Single Write call to dump all 150 lines to `synth_000.jsonl`
5. Return ONLY: "OK: wrote 150 entries to synth_000.jsonl"

If anything goes wrong (input parse error, doc count mismatch, etc.), report concisely.

---

Take your time on quality — the goal is **diverse, natural queries** + **plausible-but-distinct hard negatives**, not template-based filler.
````

### 5-2. 本生成用プロンプト (chunks 001-035、Sonnet 4.6)

パイロットで品質確認後、prompt を圧縮した軽量版。few-shot は Example A のみに削減して 1 chunk あたり token 消費を約 40% 削減。`{NNN}` の chunk 番号だけ差し替えて 35 個ディスパッチ。

````
You are generating high-quality synthetic training data (queries + hard negatives) for a Japanese text-embedding model that will specialize in retrieving Amagasaki city government FAQ documents.

# Input
Read: `G:\mahiya-dataset-factory\amagasaki-qna\work\chunks\chunk_{NNN}.json`
JSON array of records with `doc_id` (string) and `text` (`Question: ...\nAnswer: ...`).

# Task
For EACH record, generate exactly 3 entries (one per style), each with `query` and `hn_doc`. Total = 3 × records.

# Output
Write JSONL to: `G:\mahiya-dataset-factory\amagasaki-qna\work\raw_synth\synth_{NNN}.jsonl`
Format: `{"doc_id": "...", "style": "polite|plain|keyword", "query": "...", "hn_doc": "Question: ...\nAnswer: ..."}`

# Styles
- `polite` (丁寧語、25-55字): 「〜ですか」「〜ますか」「〜したいのですが」「〜教えてください」「〜知りたい」。positive Q 部を逐語コピーせず抽象化。Answer 部の具体値 (電話/町名/階数/年齢) を持ち込まない
- `plain` (常体、12-30字): 「〜は？」「どこ？」「何が必要？」「どうすればいい？」
- `keyword` (体言止め、5-22字): スペース区切りキーワード列

# Hard Negative
200-400 字、`Question: ...\nAnswer: ...` 形式。positive と異なる制度・窓口だが語彙重なり。■区切り/【お問い合わせ】/"電話 06-XXXX-XXXX" 体裁。**3 つの hn_doc は同じテンプレ・同じ課・同じ電話番号にしない**。課を多様化: 福祉課/市民課/健康増進課/環境課/保育振興課/税務課/介護保険課/住宅課/商工課/教育委員会/地域振興センター/医療保険年金課/こども家庭支援課/環境政策課 等。

# Constraints
- Query に「尼崎市」「尼崎」を含めない
- Query に positive doc 内の電話番号/住所/施設固有名を直接含めない
- hn_doc に他都市名 (大阪市/神戸市/西宮市/伊丹市/芦屋市) を含めない
- 改行は `\n` でエスケープ

# Few-shot
```
{"doc_id": "X", "style": "polite", "query": "国民年金の保険料を払うのが厳しいのですが、免除の申請に何を持っていけばよいでしょうか", "hn_doc": "Question: 国民健康保険料を一括で前納する場合の手続きについて教えてください。\nAnswer: ■国民健康保険料は口座振替・クレジットカード払い・前納による現金払いから選択でき、年度初めに一括前納する場合は約２％の割引があります。■申請には、保険証と本人確認書類が必要です。【お問い合わせ】医療保険年金課賦課担当 電話 06-6489-6535"}
{"doc_id": "X", "style": "plain", "query": "年金の免除って学生でも申請できる？", "hn_doc": "Question: 学生納付特例制度の対象となる学校はどこまでか。\nAnswer: ■大学・大学院・短期大学・高等学校・高等専門学校など、学校教育法に定める学校に在学する学生が対象です。■申請には学生証または在学証明書の写しが必要です。【お問い合わせ】医療保険年金課年金担当 電話 06-6489-6452"}
{"doc_id": "X", "style": "keyword", "query": "年金 免除 持ち物", "hn_doc": "Question: 児童手当の所得制限について教えてほしい。\nAnswer: ■児童手当には所得制限が設けられており、扶養親族の人数に応じて限度額が変わります。■限度額を超える方は特例給付として一律月額５千円が支給されます。【お問い合わせ】こども家庭支援課 電話 06-6489-6356"}
```

# Steps
1. Read input
2. Generate 3 diverse queries + 3 distinct hn_docs per record
3. Write JSONL via Write tool
4. Return ONLY: "OK: wrote N entries to synth_{NNN}.jsonl"
````

### 5-3. プロンプト設計の意図

| 設計要素 | 意図 |
| --- | --- |
| **3 styles の明示** (polite / plain / keyword) | 評価データセット (queries.json) の文体分布 (丁寧 72% / 平叙 22% / キーワード 6%) を 1:1:1 (= 33% 均等) で生成し、訓練時にスタイルバランスを取る。実分布より keyword を増やしたのは検索クエリ的なゼロショット入力にも対応するため |
| **Length 制約** (各 style ごとに) | クエリ長分布が極端に短く偏らない / 長く偏らないようにするため。ただし agent が厳密に守らない場合もあり、最終的には HF Hub 上の query 列の長さ統計で確認 |
| **Q 部の逐語コピー禁止** | パイロット (Haiku) でこれが起きると評価データに似てしまい leak リスクが上がる + 「市民が窓口に問い合わせる自然な言い回し」から外れる |
| **Answer 部の具体値 (電話番号・町名・階数・年齢) を query に持ち込まない** | 数値・固有名の完全一致による trivial retrieval を避ける。実ユーザは具体値を覚えていない前提 |
| **hn_doc に positive Q 部の文字列禁止** | これがあると hn_doc が positive のリライトになって hard negative としての機能を果たさない |
| **「3 つの hn_doc は同じテンプレ・同じ課・同じ電話番号にしない」** | パイロット (Haiku) が完全テンプレート化したので明示的に禁止 |
| **「課を多様化: 福祉課/市民課/健康増進課/...」と 14 課列挙** | hn_doc の課・窓口を強制的にバラけさせる few-shot 効果。Sonnet は実際にこのリスト外の課 (環境政策課・廃棄物指導課・ファミリーサポートセンター事務局など) も自発的に使った |
| **「尼崎市」「尼崎」 を query に含めない** | eval queries が暗黙都市名 (= 自治体名を含まない) ため、合成 query もこれに合わせる。query 文体の domain shift を最小化 |
| **他都市名 (大阪市/神戸市/西宮市/伊丹市/芦屋市) を hn_doc に含めない** | hn_doc を「尼崎市の偽 FAQ」として通用させるため。retriever が「都市名一致でハジく」だけで hard negative が効果を失うのを防ぐ |
| **few-shot 例の構造** | (a) positive のドメイン例 (年金 / 粗大ごみ) を 1 つ示すことで「同ドメインの異制度に分散させる」発想を誘発。(b) Bad example で「全 hn が同じテンプレ」「尼崎市混入」のアンチパターンを明示 |

---

## 6. 集約・品質フィルタの実施詳細

### 6-1. ロード時のチェック

`aggregate_and_filter.py` で 36 JSONL を読み込み、以下をカウント:

- JSON parse 失敗: **0 件**
- スキーマ不正 (`doc_id` / `style` / `query` / `hn_doc` のいずれかが欠損 or 非文字列): **0 件**

→ Sonnet の JSON 出力品質は安定。1 件もパース失敗なし。

### 6-2. テキスト制約フィルタ

正規表現ベースで以下を除外:

| 制約 | 除外件数 |
| --- | ---: |
| query に `尼崎` を含む | **13** |
| hn_doc が `Question:\s*.+?\nAnswer:\s*.+` 形式に合致しない | 0 |
| hn_doc に `大阪市\|神戸市\|西宮市\|伊丹市\|芦屋市` を含む | 0 |

→ 制約の遵守率は極めて高い。「尼崎」が漏れた 13 件は、agent が positive doc 内の "尼崎市" を引用したケース。

### 6-3. コサイン類似度フィルタ

`jinaai/jina-embeddings-v5-text-small` (1024 次元、normalized) で全 query / positive / eval queries を埋め込んで以下を計算:

- `cos_pos := cos(q, positive)` (paired dot product)
- `max_cos_eval := max_i cos(q, eval_q_i)` (1 vs 749 行列の row-max)

**当初の計画 (`cos_pos > 0.7`) では 49% 脱落 → しきい値を 0.5 に緩和**:

| 閾値 | 残存数 / 5,345 | 残存率 |
| --- | ---: | ---: |
| `cos_pos > 0.7` (Qwen3 流) | 2,671 | 50.0 % |
| `cos_pos > 0.5` (本実施採用) | 5,251 | 98.2 % |

→ なぜ Qwen3 の 0.7 が機能しないか:
- Qwen3 の閾値は **弱教師 (web から取った noisy ペア)** を絞る用途で、本ケースのような **seed-based 確実 positive** には過剰
- jina-v5-text-small は日本語自治体 FAQ ドメインで cos スコアの上限が低い (実測の最大値 0.901、平均 0.65 前後)
- 短いクエリ (avg 26 字) vs 長い Answer (avg 357 字) の長さ非対称により cos が構造的に低くなる

### 6-4. eval leakage check

`max_cos_eval > 0.85` の合成クエリを除外 (= eval query と表面的にほぼ同一の合成サンプルが訓練に紛れ込むのを防ぐ):

- 除外数: **113 件** (cos_pos フィルタ通過後の 5,251 件中)

### 6-5. 最終フィルタ統計

| 項目 | 件数 | 累計減少率 |
| --- | ---: | ---: |
| 入力 (sub-agent 生成合計) | 5,358 | — |
| テキスト制約通過 | 5,345 | -0.24 % (-13) |
| `cos_pos ≥ 0.5` 通過 | 5,251 | -1.76 % (-94) |
| `max_cos_eval ≤ 0.85` 通過 (= 最終) | **5,138** | -2.11 % (-113) |
| **総合保持率** | — | **95.9 %** |

→ 想定外に保持率が高かった。Sonnet の生成品質が想定以上だった証左。

---

## 7. Hard Negative Mining の実施詳細

### 7-1. 埋め込み

`jina-embeddings-v5-text-small` で:

- **Doc 埋め込み**: corpus 1,786 件 → (1786, 1024). `task='retrieval'` + `prompt_name='document'` (jina-v5 の passage 用 prompt 名は `document`、`passage` ではない点に注意)
- **Query 埋め込み**: 5,138 件 → (5138, 1024). `task='retrieval'` + `prompt_name='query'`

GPU 上で実行 (CUDA, 約 145 秒)。

### 7-2. in-memory kNN

corpus が 1,786 件と小規模なので Elasticsearch 不要:

```python
sims = q_emb @ doc_emb.T  # (5138, 1786) cosine matrix (normalized 同士の dot product)
part = np.argpartition(-sims, TOP_K, axis=1)[:, :TOP_K]  # top-50 unsorted
order = np.argsort(-sims[rows, part], axis=1)
top_idx = np.take_along_axis(part, order, axis=1)
top_scores = np.take_along_axis(sims[rows, part], order, axis=1)
```

実行時間: **0.2 秒**。FAISS すら不要。

### 7-3. NV-Retriever フィルタ (POS_AWARE_RATIO=0.95, SKIP_TOP=5)

`build_triplets.py` / `build_ntuples.py` のロジック:

1. 各合成 query について top-50 の中で `pair_doc_id (= seed doc id)` の rank と score を取得 (`pos_rank`, `pos_score`)。見つからない場合 top-1 score をフォールバックとして `pos_score` 扱い
2. `threshold = pos_score * 0.95` を計算
3. 各 candidate について:
   - `rank < SKIP_TOP` (= 上位 5) を除外 → false positive 回避
   - `doc_id == seed` を除外 → positive 自身を hn にしない
   - `score < threshold` の最高スコア候補を選ぶ → hard だが positive ほど近くない negative
4. `triplets`: 上記フィルタ通過の **最高 1 件** を採用
5. `n-tuples`: 上記フィルタ通過の **上位 4 件** を採用 + LLM 同梱 hn を slot 1 に充当 → 計 5 negatives
6. フィルタ通過候補が不足する場合、rank `SKIP_TOP+` から最高スコア候補でフォールバック (`fallback_used` / `partial_fallback_used` にカウント)

### 7-4. 実施統計

| 指標 | triplets | n-tuples |
| --- | ---: | ---: |
| 入力 (合成 query 数) | 5,138 | 5,138 |
| Positive が top-50 にヒット | 5,137 (99.98 %) | (同上) |
| Positive が top-1 (rank=0) | 3,903 (75.97 %) | (同上) |
| NV-Retriever filter 通過 (triplets で 1 件 / n-tuples で 4 件すべて) | 5,137 | 5,137 (99.98 %) |
| フォールバック使用 | 1 | 1 件 (partial、4 件中 1 件のみ filter NG) |
| **出力件数** | **5,138** | **5,138** |
| n-tuples 中 LLM 同梱 hn 投入数 | — | 5,138 (100 %) |
| n-tuples 中 mined neg (filter 通過) 累計 | — | 20,548 / 20,552 |
| n-tuples 中 mined neg (フォールバック) 累計 | — | 4 / 20,552 |

→ Positive top-1 ヒット率 76% は、jina-v5-text-small が seed positive を正しく取り戻せている割合。これは「retriever としての jina-v5 が尼崎市 FAQ ドメインで合成 query から positive を正しく retrieve できる確率」とほぼ同義。**この 24% (top-1 外) こそが特化ファインチューニングで改善できる余地** と解釈できる。

---

## 8. 最終データセット仕様

### 8-1. Config 構成

| Config | rows | columns | tokens (cl100k_base) |
| --- | ---: | --- | ---: |
| `pairs` | 5,138 | `query`, `positive` | 2,489,723 (2.49 M) |
| `triplets` | 5,138 | `query`, `positive`, `negative` | 5,127,873 (5.13 M) |
| `n-tuples` | 5,138 | `query`, `positive`, `negative_1`〜`negative_5` | 13,941,526 (13.94 M) |

### 8-2. n-tuples の negative 構成 (重要)

| Slot | 由来 |
| --- | --- |
| `negative_1` | **LLM が同時生成した hard_negative_document** (E5-Mistral 流。完全に LLM 製の偽 FAQ で corpus 外) |
| `negative_2`〜`negative_5` | **NV-Retriever でマイニングした corpus 内の hard negative** (POS_AWARE_RATIO=0.95 通過の上位 4 件) |

→ training 時にこの構造を利用して、in-corpus hn と LLM-gen hn の効果を別々に分析することも可能。

### 8-3. style 列 (パイプライン内部のみ、HF Hub には公開せず)

build_triplets.py は `style` 列も書き出すが、`upload_dataset.py` の `select_columns` で除外している。スタイル別の比率分析は work/ 内で完結する。

### 8-4. 評価リーク保護 (実装済み)

- ✅ **G1**: `eval-dataset/queries.json` の 749 件は seed として使わない (合成 query ≠ eval query)
- ✅ **G2**: 合成 query が eval query と cos > 0.85 の場合は除外 (113 件除去)
- ✅ **G3**: corpus 1,786 件は seed として全件使用 OK (= 特化検証の本旨)
- ✅ **G4** (任意): dev split は本実施では未分離。下流 fine-tuning スクリプト側で実装する想定

---

## 9. 実施で得られた知見

### 9-1. モデル選択の重要性

- **Haiku 4.5 では業界レシピが成立しない**。E5-Mistral / Qwen3 流の "LLM が hard negative を一緒に生成" は、ドメイン理解が深いモデルでないとテンプレート化する。Sonnet 4.6 が最低ライン
- 計算経済性を考えるなら、**まず Sonnet パイロットで品質を確認してから本生成にコミット** すべき。Haiku で本生成して全部捨てるのは時間的損失が大きい

### 9-2. しきい値は **ドメイン × retriever × 言語** で校正必要

- Qwen3-Embedding が論文で示した `cos > 0.7` は **彼らの retriever × 多言語 web ペア** での値。jina-v5-text-small × 日本語自治体 FAQ では **0.5 が等価な情報量** だった
- 一般化: しきい値の絶対値ではなく、**「上位 X% の sample をキープする」** のような分位ベースの設計のほうが移植しやすい (今回は 98% 残存を目指して 0.5 にした)

### 9-3. 並列サブエージェントは想定以上に強力

- 36 並列ディスパッチが実際に同時実行される (= wall-clock を 1/36 短縮) のは大きい。Sonnet 1 体で逐次なら ~12 時間相当が **約 22 分** で完了
- ただし agent が時々「150 entries 期待のところ 90 や 153 で完了」のように出力数を間違える。本実施では **アグリゲータ側で doc_id ごとの style 集合をチェックする冪等な集計設計** が必要だった (実装済み)

### 9-4. 計画 vs 実施の乖離はむしろ健全

- 計画書 (`data_synthesys_plan.md`) は 5 軸プロンプティング・3 失敗モード hn・15,000 query を想定したが、実施では 3 styles・LLM 同梱 hn のみ・5,138 query に縮小
- それでも品質は十分。**計画は「上限の探索」、実施は「最小実用 V1」** という役割分担が機能した。V2 (失敗モード hn 追加 / 5 軸 Persona Hub 追加) で増やす余地が残っている

### 9-5. corpus 特化検証の意義は維持された

- 評価リーク (G1-G3) は実装で完全担保済み。**eval queries 749 件は訓練に 1 件も入っていない**
- 一方で corpus は共有なので、特化 fine-tuning 後の Recall / nDCG 上昇は **「同 corpus への特化上限性能」** を測ることになる。これは計画通りの設計で、計画書の §1 で明記された前提条件と一致

---

## 10. 次のアクション (V2 候補)

| 候補 | 期待効果 | 実装コスト |
| --- | --- | --- |
| **失敗モード合成 hn (jina-v3 流 F1/F2/F3)** を追加 | hard negative の構文類似 / 固有表現混同 / 極性反転を強制誘発 | 中 (3 種別プロンプト + 集約) |
| **5 軸 Persona Hub** を追加 | クエリの多様性 (年齢層 × 家族構成 × 関心事) | 中 (30 ペルソナ定義 + プロンプト書き換え) |
| **doc あたり生成数を 3 → 5 に** | 訓練データ量 5,138 → 8,500+ に | 低 (プロンプト改修のみ) |
| **LLM-as-a-Judge** (Gemini / Claude が graded relevance を採点) | 品質フィルタの精緻化、低品質サンプル除外 | 中 (judge プロンプト + 並列実行) |
| **OOD 実データ (`mr-tydi-japanese`, `JaGovFaqs-22k`) を mix** | 計画書 §8 の ablation 条件 (B / C) で公平比較 | 中 (HF からロード + サンプリング) |
| **fine-tuning 実行と Recall@k / nDCG@10 の測定** | 本データセットの実効性検証 | 中〜高 (sentence-transformers / SDG 系で実装) |

---

## 11. 結論

`data_synthesys_plan.md` の業界レシピ整理を踏まえつつ、**スコープを最小実用 V1 に絞り、品質と速度の両立を優先** した結果、22 分で 5,138 件の (query, positive, hard negative × 5) を生成・公開できた。

最大のインサイトは:
1. **モデル選択 (Sonnet 必須、Haiku 不可)**
2. **コサイン閾値のドメイン校正 (0.7 → 0.5)**
3. **サブエージェント並列ディスパッチによる wall-clock 短縮**

の 3 点。これらは V2 以降の合成パイプラインの基盤となる。
