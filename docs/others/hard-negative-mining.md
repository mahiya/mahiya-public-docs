# Hard Negative Mining 手法 — 全モデル横断サマリ

`target_models.json` に列挙された 50 モデルについて、訓練時に使用された Hard Negative Mining (HNM) 手法を個別 Markdown に記録した上で、本ファイルでは横断的な主流潮流を整理する。

> **補足**: 個別モデルの詳細は `hard_negative_mining/{model_name}.md` を参照。商用 API モデル (OpenAI / Cohere / Voyage / Seed1.6 / text-multilingual-embedding-002) は技術詳細が非公開のため、推測・前身モデルからの類推に留まる。

---

## 0. 集計対象 (50 モデル)

| カテゴリ | モデル数 | 代表 |
|---|---|---|
| Microsoft Harrier-OSS | 3 | harrier-oss-v1-{27b, 0.6b, 270m} |
| Qwen3 Embedding | 3 | Qwen3-Embedding-{8B, 4B, 0.6B} |
| F2LLM-v2 | 6 | F2LLM-v2-{14B, 8B, 4B, 1.7B, 0.6B, 330M} |
| Alibaba GTE | 4 | gte-Qwen2-{7B, 1.5B}-instruct, gte-Qwen1.5-7B-instruct, gte-multilingual-base |
| KaLM | 3 | KaLM-Embedding-Gemma3-12B-2511, KaLM-embedding-multilingual-mini-{v1, instruct-v1} |
| Jina | 3 | jina-embeddings-v3, jina-embeddings-v5-text-{small, nano} |
| NVIDIA | 3 | NV-Embed-{v1, v2}, llama-embed-nemotron-8b |
| Salesforce / GritLM | 4 | GritLM-{7B, 8x7B}, SFR-Embedding-{Mistral, 2_R} |
| E5 / BGE | 5 | e5-mistral-7b-instruct, multilingual-e5-large(-instruct), bge-m3, bge-m3-custom-fr |
| Google | 3 | gemini-embedding-001, embeddinggemma-300m, text-multilingual-embedding-002 |
| 商用 API | 4 | text-embedding-3-large, Cohere-embed-multilingual-{v3.0, light-v3.0}, voyage-3.5 |
| その他 | 9 | Octen-Embedding-8B, Seed1.6-embedding-1215, Linq-Embed-Mistral, BOOM_4B_v1, stella_en_1.5B_v5, jasper_en_vision_language_v1, Solon-embeddings-large-0.1, bilingual-embedding-{large, base} |

---

## 1. マイニング手法 (どの retriever で hard negative を採取するか)

### 1.1 Dense retriever ベースの top-k マイニング (圧倒的主流: 約 35/50 モデル)

**事前学習済みの強い埋め込みモデルで top-k 検索 → 上位帯から hard negative を選択** するパターンが、ほぼ業界標準として確立している。

| モデル | retriever / teacher embedder |
|---|---|
| SFR-Embedding-Mistral | **BGE-base** |
| SFR-Embedding-2_R | 自前 SFR-Embedding-Mistral / E5-Mistral (self-distillation 強化) |
| Linq-Embed-Mistral | **mE5-base** |
| NV-Embed-v2 | **E5-mistral-7b-instruct** |
| llama-embed-nemotron-8b | **e5-mistral-7b-instruct + Qwen3-Embedding-8B** (2 teacher 併用) |
| F2LLM-v2 シリーズ | **Qwen3-Embedding-8B** (v1 では 0.6B、v2 で増強) |
| KaLM 系 | "previously trained model" (自己ブートストラップ) |
| jina-embeddings-v3 | **BGE-large + BM25** ハイブリッド |
| jina-embeddings-v5 | Qwen3-Embedding-4B (教師蒸留経由) |
| multilingual-e5-large | mE5base (top-100 マイニング) |
| e5-mistral-7b-instruct | mE5base + GPT-4 生成 negatives |
| bge-m3 | ANCE 法による自前 ANN マイニング |

### 1.2 LLM スコアリング型 (新潮流: 約 5/50 モデル)

LLM 自身で hard negative を採点・選別する設計が 2024-2025 年から登場し、計算量と引き換えに精度を高める動きがある。

- **gemini-embedding-001**: Gemini-init embedder で top-k 取得 → **Gemini LLM で graded classification + query likelihood の 2 種プロンプト採点 → RRF 統合 → 最下位の k 番目 neighbor を hard negative に採用** (一次論文 §4.2)
- **harrier-oss-v1 系**: GPT-5 で生成した 2B ペア事前学習 + LLM ベース re-ranker をデータクリーナ兼 teacher に
- **e5-mistral-7b-instruct**: GPT-4 がプロンプト内で `hard_negative_document` を**直接生成**(LLM 生成型 hard negative の先駆け)

### 1.3 BM25 / Sparse 系 (限定的)

- **jina-embeddings-v3** のみが Dense (BGE-large) と BM25 の**ハイブリッド**を明確に採用。
- 単体 BM25 のみで hard negative を採取するモデルは現代の本対象群には**ほぼ存在しない** (BM25 は NQ / MS-MARCO のオリジナルラベル経路でのみ間接利用)。

### 1.4 In-batch negatives のみ (Stage 1 / 弱教師段階の標準)

ほぼ全モデルが**弱教師(対照)事前学習段階では in-batch negatives のみ**で大規模バッチ (16,384 級) で学習 → Stage 2 SFT で hard negative を導入する 2 段階レシピを採る。

- E5 / mE5 / GTE / Qwen3 / F2LLM / Linq / NV-Embed すべてこのパターン。
- **Stage 1 で hard negative を使わない**のはコスト・false negative リスク回避の経済的判断と、Stage 1 のデータ規模 (10 億〜数十億ペア) が hard mining 計算量に見合わないことが理由。

### 1.5 Multi-teacher distillation 自動 triplet 構築 (NovaSearch 系)

- **stella_en_1.5B_v5 / jasper_en_vision_language_v1**: NV-Embed-v2 / SFR / BGE-en-icl など複数の teacher の cosine similarity に基づき**バッチ内で triplet を自動生成**。明示的 ANN pre-mining なしで false negative も暗黙除外される設計。

### 1.6 古典的 Augmented SBERT (Cross-Encoder 教師)

- **bilingual-embedding-large / base** (Lajavaness): Thakur 2021 の Augmented SBERT pair sampling を採用し、**Cross-Encoder で silver negative を生成**する旧来型レシピ。retriever-based mining とは系譜が異なる。

---

## 2. False Negative 除去 (今や HNM の核心)

「Hard Negative とラベル付けたが実は意味的に正例だった」サンプルを除外することが、2024 年以降の HNM の最大の差別化ポイント。

### 2.1 Positive-aware score margin filtering (新主流: NVIDIA / Alibaba / Qwen 共通)

スコアが正例に近すぎる候補を**閾値でマスク**するアプローチ。

| モデル | 具体ルール |
|---|---|
| **NV-Embed-v2** | **TopK-PercPos: `neg_score < pos_score × 0.95`** (95% margin) |
| **llama-embed-nemotron-8b** | NV-Retriever の TopK-PercPos 95% 閾値を多言語拡張 |
| **Qwen3-Embedding 系** | 損失内で `s_ij > s(q_i, d+_i) + 0.1` のサンプルをマスク |
| **F2LLM-v2 系** | `score < 0.8` かつ`正例スコアの 95% 未満`の候補のみ採用 |
| **Octen-Embedding-8B** | 動的 false negative フィルタ (詳細は半公開) |

NV-Retriever 論文 (arXiv:2407.15831) のアブレーションでは**Naive Top-K (NDCG@10 0.5407) → TopK-PercPos (0.5856)** と +4.5pt 改善されており、**現時点で最も効果が立証された除去手法**。

### 2.2 Top-k 範囲指定 (rank 30+ サンプリング: SFR レシピ)

top-1〜top-29 は false positive 率が高いため意図的に除外し、rank 30〜100 帯から hard negative を採る。

| モデル | サンプリング範囲 |
|---|---|
| **SFR-Embedding-Mistral** | rank 30〜100 |
| **SFR-Embedding-2_R** | rank 30〜100 (継承) |
| **Linq-Embed-Mistral** | rank 30〜100 (継承) |
| **F2LLM-v2** | top-100 検索 → top-5 除外 → 上位 24 件 |

### 2.3 Ranking Consistency Filtering

正例ペアが retriever の top-k に入らないサンプルそのものを**訓練データから削除**する手法。データ品質の方を担保する設計思想。

- **KaLM v1**: 正例が top-50 に入らないペアを除外 (k=50)
- **Linq-Embed-Mistral**: 双方向の ranking consistency でデータ全体をフィルタ

### 2.4 同一文書 / タプル ID マスク

In-batch negatives 内の偶発的な false positive (他クエリの正例) を除去:

- **Qwen3-Embedding**: same document detection で `m_ij` マスク
- **jina-embeddings-v3**: タプル固有 ID プレフィックス (Gecko 流)
- **e5-mistral**: GPT-4 プロンプトでクエリ ID をテンプレート化

### 2.5 Cross-encoder reranking フィルタ (限定的)

意外なことに、本対象の主要モデルでは**訓練時 Cross-encoder reranking 経由の HNM 除去は主流ではない**。

- **gte-multilingual-base** の Reranker fine-tune (1 pos + 6 hard + 4 random) で部分採用
- 多くのモデルは「reranking は評価時のみ」「KD の teacher として cross-encoder を使う」(multilingual-e5-large の KL 蒸留 α=0.2 など) に留めている

---

## 3. Hard Negative 数 (per query)

| 数 | 採用モデル |
|---|---|
| **1** | e5-mistral-7b-instruct, Linq-Embed-Mistral (合成データ品質向上で十分) |
| **4** | NV-Embed-v2, llama-embed-nemotron-8b (Stage 2) |
| **6+4 (hard+random)** | gte-multilingual-base reranker fine-tune |
| **7** | **SFR-Embedding-Mistral**, **SFR-Embedding-2_R**, multilingual-e5-large, KaLM v1, jina-v5-nano (Classification) |
| **8** | gte-multilingual-base TRM fine-tune |
| **24 (top 上位)** | F2LLM-v2 |

**集約**: Linq の事例 (1 個で十分) を除き、**4〜8 個** が定番レンジ。最も多いのは **7 (SFR レシピ)** で、E5 系の長らく続く慣習。

合成データの質が高いほど hard negative 数を**減らせる** (Linq, e5-mistral) という Diminishing returns の知見が 2024-2025 年に蓄積されている。

---

## 4. Teacher / Distillation の利用

### 4.1 Self-knowledge distillation

- **bge-m3**: Dense + Sparse + Multi-vector の統合スコアを内部 teacher にする (外部 cross-encoder 不要)
- **F2LLM-v2 系**: 大型モデルが小型モデルの teacher (1.7B ← 4B, 0.6B ← 1.7B, 330M ← 0.6B)
- **harrier-oss 系**: 27B が 0.6B / 270m の teacher

### 4.2 外部 teacher 蒸留

- **EmbeddingGemma**: Gemini Embedding を teacher として **embedding matching distillation を hard negative passage にも適用**
- **multilingual-e5-large**: cross-encoder からの **KL 蒸留 (α=0.2)** を Stage 2 で適用
- **stella v5 / jasper**: NV-Embed-v2, SFR, BGE-en-icl の **multi-teacher**

### 4.3 損失関数面での hard negative 重み付け (新工夫)

- **EmbeddingGemma**: **Hardness-weighted NCE loss** (`w_i = exp(α · sg(sim(q, p-)))`, α=5.0) — hard なサンプルほど損失寄与を増幅
- **KaLM-Gemma3-12B-2511**: **Online Hard-Negative Mixing** (Beta(2,2) 重みで 2 ハードネガを線形混合) + **Focal-Style Reweighting** (γ=0.5)
- **Qwen3-Embedding**: query-query / document-document / query-document の 3 系統を全て in-batch negatives 化

---

## 5. 合成データ × Hard Negative

合成データ生成 (LLM-driven SDG) と hard negative mining の融合が 2024-2026 年の主要潮流。

| モデル | 合成 LLM | HN との関係 |
|---|---|---|
| e5-mistral-7b-instruct | GPT-4 | プロンプトで `hard_negative_document` を直接生成 |
| Qwen3-Embedding | Qwen3-32B | 約 150M 合成ペア (Stage 1 主体) |
| Linq-Embed-Mistral | LLM 多種 | 合成 query 品質向上で per-query HN 数 7→1 に削減 |
| llama-embed-nemotron-8b | gpt-oss-20b/120b, Mixtral-8x22B, Llama-3.3-70B, Llama-4-Scout/Maverick (6 モデル) | 合成 8.4M + 公開 7.7M = 16.1M ペア |
| jina-embeddings-v3 | LLM 構文類似生成 | 検索失敗モード F1〜F4 に基づく合成 HN 補強 |
| KaLM v1 | Qwen2-72B-Instruct + Persona Hub | 55 万件合成 |
| harrier-oss | GPT-5 | 2B ペア (事前学習) |

---

## 6. 主流手法の総括 (=「2026 年現在の標準レシピ」)

50 モデルの公開情報を横断した結果、**現代の SOTA 埋め込みモデルが採用する Hard Negative Mining の標準レシピ**は以下に集約できる:

```
1. 2 段階訓練を採る:
   - Stage 1 (弱教師): in-batch negatives のみ、巨大バッチ (8K-16K)、HN なし
   - Stage 2 (SFT)  : hard negative + in-batch negatives 併用

2. Hard negative の採取は Dense retriever ベース top-k マイニング:
   - retriever は当代最強の oss embedder (BGE / mE5 / Qwen3-Embedding) または
     自モデルの前世代 (self-bootstrapping)
   - top-100 候補から rank 30 以上をサンプリング、または閾値で filter

3. False negative 除去は positive-aware score margin filtering:
   - NV-Retriever の TopK-PercPos (neg_score < pos_score × 0.95) が事実上の標準
   - Qwen3 の +0.1 マージン式 / F2LLM の score<0.8 二重条件などバリエーションあり

4. Hard negative 数は 4〜8 個 / query (中央値 7):
   - 合成データ品質が高ければ 1 個でも可 (Linq, e5-mistral)

5. 損失内で同一文書 / 同一タプルの偶発的 false positive をマスク

6. 合成データを LLM (GPT-4 / Qwen3-32B / Llama-4 / Gemini) で生成し、
   生成プロンプト内で hard negative document も同時に出力させる手法が普及

7. Cross-encoder reranking は訓練時の HNM 除去より、
   KD の teacher 信号として使われる方が多い

8. 蒸留 (Self / Multi-teacher) と組み合わせて hard negative の困難度を
   ソフトラベル経由で伝達する設計が増加 (EmbeddingGemma, BGE-M3, Stella, F2LLM)
```

### 主流手法の "事実上の標準テンプレート"

```
[マイニング]      Dense retriever top-100 検索
[除外]            top-5 (or top-29) を捨てる
[除去]            neg_score < pos_score × 0.95 (positive-aware filter)
[サンプル数]      4〜8 個 / query (デフォルトは 7)
[補完]            in-batch negatives (cross-batch, cross-device)
[マスク]          same-doc / same-tuple-id false negative
[損失]            InfoNCE (温度 τ ≈ 0.02) ± KD term
[合成データ]      LLM で query / hard_negative_doc を共生成
```

---

## 7. 異端・特殊事例の整理

主流から外れる興味深い事例:

| モデル | 特殊性 |
|---|---|
| **gemini-embedding-001** | Gemini LLM 自身でgraded classification + query likelihood を採点 (LLM-based mining の最先端) |
| **bge-m3** | 外部 teacher を使わず Dense + Sparse + Multi-vector の自己統合 score を teacher 化 |
| **EmbeddingGemma** | Hardness-weighted NCE loss + embedding matching distillation を HN passage に適用 |
| **GritLM** | 自身で再マイニングせず E5 公開データ + MEDI2 の既存 HN を流用、同データセット由来サンプルでバッチ統一 |
| **stella v5 / jasper** | 明示的 ANN pre-mining なし、multi-teacher cosine 類似で batch 内 triplet 自動構築 |
| **bilingual-embedding-large/base** | 古典的 Augmented SBERT (Cross-Encoder 教師) 系譜、retriever-based mining ではない |
| **Linq-Embed-Mistral** | 合成データの質向上により per-query HN 数を 1 まで削減 (diminishing returns の実証) |
| **harrier-oss / Cohere / OpenAI / Voyage / Seed1.6** | 商用クローズド、公式情報極めて限定的 |

---

## 8. 商用クローズドモデルの開示状況

| モデル | 公開度 |
|---|---|
| OpenAI text-embedding-3-large | ✗ 公式情報ゼロ。前身 cpt-text 論文 (arXiv:2201.10005) のみ参照可能 |
| Cohere embed-multilingual-v3.0 / light | ✗ "3 段階訓練" "compression-aware training" の言及のみ |
| Voyage 3.5 | △ "distillation from voyage-3-large" + "Voyage AI rerankers 利用" 公式言及あり |
| Seed1.6-embedding-1215 (ByteDance) | ✗ "difficulty-stratified negative mining" 言及のみ |
| Google text-multilingual-embedding-002 | ✗ Vertex AI ドキュメントに訓練手法記述なし。Gecko Embedding (Lee et al. 2024) ベースと推定 |

---

## 参考: 個別レポート一覧

50 モデル分の Hard Negative Mining 詳細は同フォルダ内の各 Markdown を参照:

- `harrier-oss-v1-{27b, 0.6b, 270m}.md`
- `Qwen3-Embedding-{8B, 4B, 0.6B}.md`
- `F2LLM-v2-{14B, 8B, 4B, 1.7B, 0.6B, 330M}.md`
- `gte-Qwen{2-7B, 2-1.5B, 1.5-7B}-instruct.md`, `gte-multilingual-base.md`
- `KaLM-Embedding-Gemma3-12B-2511.md`, `KaLM-embedding-multilingual-mini-{v1, instruct-v1}.md`
- `jina-embeddings-{v3, v5-text-small, v5-text-nano}.md`
- `NV-Embed-{v1, v2}.md`, `llama-embed-nemotron-8b.md`
- `GritLM-{7B, 8x7B}.md`, `SFR-Embedding-{Mistral, 2_R}.md`
- `e5-mistral-7b-instruct.md`, `multilingual-e5-large{,-instruct}.md`, `bge-m3{,-custom-fr}.md`
- `gemini-embedding-001.md`, `embeddinggemma-300m.md`, `text-multilingual-embedding-002.md`
- `text-embedding-3-large.md`, `Cohere-embed-multilingual-{v3.0, light-v3.0}.md`, `voyage-3.5.md`
- `Octen-Embedding-8B.md`, `Seed1.6-embedding-1215.md`, `Linq-Embed-Mistral.md`, `BOOM_4B_v1.md`
- `stella_en_1.5B_v5.md`, `jasper_en_vision_language_v1.md`, `Solon-embeddings-large-0.1.md`
- `bilingual-embedding-{large, base}.md`
