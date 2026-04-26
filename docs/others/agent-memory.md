# 2026年のSearch AIはAgent Memoryである

**著者:** Han Xiao (VP of AI, Elastic / 元 Jina AI 創業者兼CEO)
**発表:** 2026年4月
**原資料:** スライド全31ページ (`screenshots/0.png`〜`30.png`) からの文字起こしを統合

---

## 目次

1. [Search AIの進化](#1-search-aiの進化)
2. [Agent Memoryとは何か](#2-agent-memoryとは何か)
3. [Memory設計パターン](#3-memory設計パターン)
4. [ベンチマーク](#4-ベンチマーク)
5. [結論](#5-結論)
6. [参考文献](#6-参考文献)

---

## 1. Search AIの進化

### 1.1 検索AIの系譜

検索AIは以下のように進化してきた:

```
Keyword Search (1960s〜) → Embedding Search (2010-22) → Hybrid Search (2020-23)
  → RAG (2023-24) → Deep Research (2025) → Agent Memory (2026)
```

### 1.2 2025年の業界トレンド

- **Decoder-onlyモデル**が主流 (Qwen3、NV-Embed)
- **小型モデル**が大型モデルを凌駕: <500Mパラメータ
- **長文コンテキスト**は32K–128Kが標準。ColPaliによるビジュアル検索が登場
- **Matryoshka次元適応**、バイナリ量子化で32倍の圧縮

### 1.3 Jina AIの3本柱

- **Embeddings**: v3 → v4 (マルチモーダル) → v5
- **Reranker**: v3 (131K context) + m0 (マルチモーダル)
- **Reader**: r.jina.ai (HTML→MD/JSON 変換)
- オープンウェイト、マルチモーダル、多言語対応
- llama.cpp / ONNX / vLLM / MLX で動作

### 1.4 エージェントの時代

エージェントはチャットから「長時間自律的に動作するワーク」へと進化している。METRのデータによれば、フロンティアモデルのタスク・ホライズン (一定の成功率を達成できるタスク長) は**7か月で2倍**になっており、2026年初頭には複数日にわたるタスクをこなせるようになっている。

しかし、どれほど能力が向上しても、**セッションが終わるとすべてを失う**という根本問題がある。

> 出典: METR, *Task-Completion Time Horizons of Frontier AI Models*, 2026.3

### 1.5 なぜMemoryが重要なのか

```
自律タスクのホライズンが7か月で倍増 (METR)
  ⇒ AGI (複数日エージェント)
  ⇒ Persistent Memory はもはやオプションではない
```

Memoryの**Representation (構造)** は次の4操作 (CRUD) で語られる:

- **C**reate — 何を保存するか
- **R**ead — どう取り出すか
- **U**pdate — どうマージするか
- **D**elete — いつ忘れるか

---

## 2. Agent Memoryとは何か

### 2.1 生物学的Memoryからの類推

脳の3つのMemoryサブシステムは、Agent Memoryに直接対応する:

| 脳領域 | 機能 | エージェント側のアナロジー | 時間スケール |
|---|---|---|---|
| 海馬 (Hippocampus) | エピソード記憶: ワンショット書き込み・時間的インデックス・感情的重み付け | Vector Database | ms〜時間 |
| 大脳新皮質 (Neocortex) | 意味記憶: 緩やかな統合、統計的抽出、汎化 | Knowledge Graph | 日〜年 (睡眠リプレイ) |
| 前頭前皮質 (Prefrontal Cortex) | ワーキングメモリ: 能動的維持、注意ゲーティング、急速減衰 | Context Window | 秒 |

### 2.2 サブシステムマッピング

完全なAgent Memoryシステムは3サブシステムすべてをカバーする必要がある。実用上は、エピソード記憶と意味記憶は別々に構築され、ワーキングメモリはコンテキストウィンドウに収まる範囲で管理される。

|  | Episodic (海馬) | Semantic (新皮質) | Working (前頭前皮質) |
|---|---|---|---|
| 生物学的アルゴリズム | Sparse Coding + Temporal Binding | Hebbian 緩やか統合 | Attractor Dynamics |
| 書き込み速度 | ワンショット | 緩慢 (interleaved replay) | 即時 (attention gating) |
| 保持期間 | 時間〜日 | 永続 | 秒 |
| 想起 | 手がかり依存・時間的 | 意味的連想 | 能動的維持 |
| エージェント側 | Vector DB | Knowledge Graph | Context Window |
| 中核操作 | `store()` + `search()` | エンティティ抽出 + グラフ構築 | プロンプト注入 + 要約 |
| Jinaの役割 | Embedding + Reranker + Reader | – | – |

### 2.3 「忘却問題」

> Karpathy: 「あらゆるLLMのパーソナライゼーションに共通する課題は、2か月前のちょっとした質問が永続的に深い興味として扱われ、何度も再浮上することだ」

本当の問題は**覚えること**ではなく、**何を忘れるか**を知ることである。

#### なぜ起きるか

- 現状のAgent Memoryは **append-only**、減衰がない
- 検索の重みは時間や関連性ドリフトを無視する
- 生物学に反する: 海馬の記憶には時間依存の忘却がある

#### Ebbinghausの忘却曲線

$$R = e^{-t/S}$$

復習されない記憶は指数関数的に減衰し、繰り返しアクセスされると安定性 *S* が高まる。**現在のAIシステムは多くがそもそも減衰を持たない**。

---

## 3. Memory設計パターン

### 3.1 製品ランドスケープ

Vector + Graph のハイブリッド構成が支配的 (10製品中5つが採用)。Pure Vector や Pure SQL では時間的推論やマルチホップクエリを扱えない。ByteDanceは**ファイルシステム・パラダイム**で参戦している。

| 製品 | 企業 / 創業者 | Stars | 資金 | アーキテクチャ | バックエンド | LongMemEval |
|---|---|---|---|---|---|---|
| Mem0 | Deshraj Yadav (YC) | 50K | $24M Series A | Vector + Graph | 20+ backends + Neo4j | 49% |
| Graphiti/Zep | Zep AI | 24K | – | Temporal KG | Neo4j | 71.2% |
| Letta/MemGPT | UC Berkeley | 22K | $10M | LLM-as-OS | SQLite/PG | – |
| OpenViking | ByteDance/Volcengine | 19K | 内部 | Context DB | Volcengine | – |
| Supermemory | Dhravya Shah (19歳) | 17K | $2.6M Seed | Atomic facts + relations | Cloudflare KV | 85.2% |
| Cognee | Cognee AI | 13K | $7.5M | ECL + Memify | LanceDB + Kuzu | – |
| Memori | GibsonAI (Bobur U.) | 12K | – | Pure SQL | PG/SQLite | – |
| Nowledge | Nowledge Labs | 108 | – | Local Personal KG | Local + MCP | – |
| Hindsight | – | 6.4K | – | 4-net + 4-way retrieval | Graph + Vector + BM25 | **91.4%** |
| HydraDB | HydraDB Inc | Closed | $6.5M | Git-style append KG | Custom graph + vector | 90.8% |
| MemOS | MemTensor (SJTU/IAAR) | 7.9K | – | Memory OS | Qdrant + Neo4j | 75.8% |
| mem9 | PingCAP (Ed Huang) | 751 | – | Stateless plugin | TiDB | – |

**プラットフォーム組み込み:**

| 製品 | 企業 | アーキテクチャ | バックエンド |
|---|---|---|---|
| ChatGPT | OpenAI | ユーザ事実 + 履歴検索 | 非公開 |
| Claude.ai | Anthropic | Project Knowledge Base | 非公開 |
| Claude Code | Anthropic | CLAUDE.md + MEMORY.md | ファイルシステム |
| Codex | OpenAI | ファイルシステム + サンドボックス | ファイルシステム |

### 3.2 製品ポジショニングマップ

軸: **Active Mgmt ↔ Passive Store** (縦) / **Flat Storage ↔ Structured Graph** (横)

- **LLM-Native** (左上): ChatGPT, Claude.ai, Letta/MemGPT, Mem0
- **Graph-Based** (右上): Hindsight, Zep/Graphiti, MemOS, Supermemory, HydraDB
- **Storage-Centric** (左下): Memori, Claude Code, mem9, Codex
- **右下〜中央**: Cognee, OpenViking, Nowledge

### 3.3 3つの流派

共通基盤 (Embedding / Retrieval / CRUD) はコモディティ化しており、差別化要因は**グラフ設計**と**ライフサイクル管理**にある。

- **Graph-Based**: LLMが事実をKnowledge Graphに抽出。検索は Vector + グラフ走査
- **LLM-Native**: モデル自身がメモリを管理し、何を保持・忘却・統合するか決める
- **Storage-Centric**: CRUDだけのフラット格納。構造も推論もない

### 3.4 業界コンセンサス

| 技術 | 採用製品 | 評価 |
|---|---|---|
| Vector意味検索 | Mem0, Supermemory, Cognee, HydraDB, Zep, MemOS | **強い合意** |
| LLM事実/エンティティ抽出 | Mem0, Zep, Supermemory, Cognee, HydraDB, Hindsight, OpenViking, MemOS | **強い合意** |
| Graph + Vector ハイブリッド | Mem0, Zep, Supermemory, Cognee, HydraDB, Hindsight, MemOS | **強い合意** |
| メモリのアトム化 | Mem0, Supermemory, Cognee, HydraDB | **強い合意** |
| 知識コンフリクト解消 | Mem0, Zep, Supermemory, HydraDB, Hindsight | **強い合意** |
| 時間的認識 (bi-temporal) | Zep, Supermemory, HydraDB, Hindsight | 中〜強 |
| BM25 + Dense ハイブリッド | Zep, HydraDB | 中 |
| メモリライフサイクル管理 (OSパラダイム) | MemOS, Letta | 萌芽 |
| LLM自己管理メモリ | Letta のみ | 学術的、本番リスク高 |
| Pure SQL (Vector/Graphなし) | Memori のみ | 反主流 |
| Git-style append-only グラフ | HydraDB のみ | 真のイノベーション |
| 生物学的減衰 | HydraDB, Supermemory | 実験的 |
| デプロイ後グラフ最適化 | Cognee のみ | 有望、データなし |
| ファイルシステム型コンテキスト管理 | OpenViking のみ | 新パラダイム、未検証 |

### 3.5 主流アーキテクチャパターン

```
Chat → LLM抽出 → {Vector DB, KG, Temporal} → Hybrid Retrieval
       → {Conflict解消, Decay} → Context
```

Jina Embeddings + Reranker は Vector DB と Hybrid Retrieval の段で活躍する。

### 3.6 製品別の詳細

#### Mem0 (50K stars / Deshraj Yadav / YC / $24M Series A)
- Vector + Graph ハイブリッド: 事実をVector DBとNeo4jへ
- 20+ Vector バックエンド対応 (Elasticsearch含む)
- 3層構造: user / session / agent
- LOCOMO: OpenAI Memory比 +26% 精度、−91% レイテンシ
- **+** 最も広いエコシステム、ESを既にサポート / **−** OSS版 LongMemEval-s ≈49%

#### Graphiti / Zep (24K stars / 114 citations)
- Neo4j上の時間的Knowledge Graph
- Bi-temporal edges: `t_valid` + `t_invalid`
- 3経路検索: Semantic + BM25 + Graph traversal
- クエリ時LLM不要、P95 300ms
- **+** 時間推論が真の堀、DMR 94.8% / **−** Neo4j依存

#### Letta / MemGPT (22K stars / UC Berkeley / $10M)
- LLM-as-OS: ツール呼び出しでメモリを自己管理
- 4階層: core → recall → archival → vector DB
- **+** 最も独自性のあるパラダイム / **−** ハルシネーション連鎖リスク

#### Supermemory (17K stars / Dhravya Shah, 19歳 / $2.6M)
- 3種類の関係を持つアトミック事実メモリ
- 生物学的減衰 (intelligent forgetting)
- 2層検索: memory + raw chunks
- **+** LongMemEval-s 85.2% (#2)、<400ms / **−** 論文なし、コアは非公開

#### MemOS (7.9K stars / MemTensor·IAAR-Shanghai / Apache-2.0)
- OSスタイル3層設計 (interface / operations / infrastructure)
- **MemCube**: 明示的(text) / 活性(KV-cache) / パラメトリック(LoRA) を統一
- **MemScheduler**: 優先度・減衰・型選択を非同期スケジュール
- **MemLifecycle**: create → activate → merge → archive → expire
- **MemGovernance**: アクセス制御 + バージョンチェイン + 監査ログ
- バックエンド: Qdrant + Neo4j (+ Redis Streams)
- **+** 36著者の最も包括的な論文、型変換が独自 / **−** LongMemEval 75.8% は控えめ、依存重い

#### Cognee (13K stars / $7.5M)
ECLパイプライン + Memify (デプロイ後グラフ最適化)。DBアグノースティック。

#### Memori (12K stars / Harish Mukhami)
Pure SQL、コスト52–82%減、意味検索なし。

#### Nowledge (108 stars)
ローカルファースト個人KG、クロスAIツール、極初期段階。

#### HydraDB ($6.5M / 非公開)
Git-style append-only KG、スライディングウィンドウ、3層リランキング。LongMemEval-s SOTA 90.8%。

#### mem9 (751 stars / Apache-2.0)
ステートレスプラグイン + Go中央サーバ、TiDBバックエンド。

#### OpenViking (19K stars / ByteDance)
Context DB、ファイルシステム・パラダイム、L0/L1/L2 3層オンデマンドロード、再帰的ディレクトリ検索。

### 3.7 アーキテクチャ採用比較

主要コンポーネント (LLM抽出 / Vector / Graph / Temporal / Hybrid Retrieval / Conflict解消 / Decay) の採用状況の概観:

- フル装備に近い: **Supermemory, HydraDB**
- 6/7 採用: **Zep/Graphiti, Hindsight**
- 5/7 採用: **Mem0, MemOS**
- 単機能寄り: Letta, OpenViking, Memori, mem9, Nowledge
- プラットフォーム製品 (ChatGPT/Claude.ai/Claude Code/Codex) は積極的なメモリ層を持たないか、ChatGPTのみが Hybrid Retrieval + Conflict + Decay 相当を持つ

---

## 4. ベンチマーク

### 4.1 主要ベンチマーク

- **LongMemEval** (Wu et al., 2024): 抽出・マルチセッション推論・知識更新・時間推論・安全拒否の500問。簡易版 LongMemEval-s あり
- **EverMemBench** (2026.2): マルチパーティ協調の初ベンチマーク、1M+トークン。オラクル検索でもmulti-hopは26%、時間推論にはバージョン意味論が必要
- **MABench** (Hu et al., ICLR 2026): 精密検索、テスト時学習、長文理解、コンフリクト解消。EventQA + 事実統合
- **MemBench** (ACL 2025): 事実 vs 内省的メモリ、参加者 vs 観察者ロール。内省メモリは事実抽出より遥かに困難
- **MemoryArena** (2026.2): メモリ-エージェント-環境ループ
- **MemoryBench** (Tsinghua, 2025.10): ユーザフィードバック付き継続学習ベンチ、11データセット。**手続き記憶を活かせる既存システムは無し**
- **LOCOMO** (Snap Research): 300+ターンの超長対話10本。Mem0 は +26% を報告
- **Letta Leaderboard**: ファイルベース 74.0% vs Mem0 68.5%

### 4.2 ベンチマークから得られた知見

#### LongMemEvalから

- 長文コンテキストLLMが生履歴を読む構成は精度が30〜60%低下
- ChatGPTは重要情報を上書き、Cozeは間接情報を取り逃がす
- **マルチセッション推論** が最弱領域 (Hindsight 91.4% SOTAでもサブスコアは低い)
- MemOS: LoCoMo 75.80, LongMemEval +40.43% vs OpenAI、35%トークン削減
- ターン粒度 > セッション粒度
- 事実拡張インデックス: Recall +9.4%、QA +5.4%

#### MABenchから

- マルチホップ事実統合が最難関: ベスト ≈7%、MIMIRが39%
- 知識コンフリクト解消は全体的に弱い

#### 横断的合意

- **単一事実の抽出は容易、クロスセッション推論は困難**
- **時間的認識** がキー差別化要因
- 知識の更新・コンフリクト解消は依然オープン課題

### 4.3 主要論文

2026年の文献は4点に収束する: (1) ステートレスなRAGでは不十分、メモリには**状態管理**が必要; (2) **グラフ**が好まれる組織化手法; (3) 忘却/減衰は未解決; (4) 次はマルチモーダル/マルチエージェントメモリ。

| 論文 | arXiv | 中核貢献 |
|---|---|---|
| Memory in the Age of AI Agents | 2512.13564 | 47名による調査。3次元分類 (form/function/dynamics) |
| Memory for Autonomous LLM Agents | 2603.07670 | write-manage-read ループ。5機構ファミリー |
| AriadneMem | 2603.03290 | 二段階分離: オフライン構築 + オンライン推論。Multi-Hop F1 +15.2%、497トークン |
| CMA (Continuum Memory) | 2601.09913 | 連続体メモリアーキテクチャを定義 |
| Graph-based Agent Memory | 2602.05665 | グラフ視点の包括的サーベイ |
| HydraDB / Cortex | – | Git-style versioned temporal graph + 3層リランキング。LongMemEval-s 90.8% |
| MemOS | 2507.03724 | Memory OS: MemCubeで3型統一。LoCoMo 75.8%、LongMemEval +40.43% vs OpenAI |
| Hindsight | – | 4ネット分離 + 4経路並列検索 + cross-encoderリランキング。LongMemEval SOTA 91.4% |

---

## 5. 結論

### 5.1 Jinaの位置づけ

Embedding + Reranking + Reading は、あらゆるメモリ層の下にある**標準の検索インフラ**である。Elasticsearchは Storage + Search 層でハイブリッド検索を担う。**メモリ層そのものは作らない**。

```
┌───────────────────────────────────────────┐
│ Agent Frameworks (OpenClaw, Letta, ...)   │
├───────────────────────────────────────────┤
│ Memory Logic (extraction, lifecycle,      │
│ conflict)                                 │
├───────────────────────────────────────────┤
│ Storage + Search (ES, vector/graph DBs)   │  ┐
├───────────────────────────────────────────┤  ├─ Jina + ES
│ Jina Embeddings + Reranker + Reader       │  ┘
└───────────────────────────────────────────┘
```

### 5.2 カバレッジ分析

**カバーしている領域:**

| 機能 | 実装 |
|---|---|
| Vector意味検索 | Jina Embeddings v5 (677M) |
| BM25キーワード検索 | ES コア機能 |
| Dense + Sparse ハイブリッド | ES native RRF |
| リランキング | Jina Reranker v3 (131K context) |
| Web/ドキュメント理解 | ReaderLM-v2 (512K context) |
| マルチモーダル埋め込み | Jina v4 (text + image + PDF) |
| メタデータ / マルチテナント | ES index/alias |

**カバーしない領域:**

| 機能 | 帰属層 |
|---|---|
| Knowledge Graph 走査 | Neo4j/Kuzu |
| Bi-temporal バージョン管理 | データモデル設計 |
| メモリライフサイクル (decay) | アプリケーションロジック |
| LLM 事実抽出 | メモリロジック層 |

### 5.3 ホットテイク

1. **エージェントメモリのおかげでレコメンダシステムが復活する** — エージェントメモリの本質はパーソナライゼーション (好み・パターン・過去決定の記憶) であり、レコメンダはこれを20年やってきた。Douyin/Taobao/Spotifyのようなレコメンドに強い企業は内在的優位を持つ。RecSysコミュニティは大復活するだろう。

2. **忘却 (Unlearning) は記憶よりも難しく、より重要** — 現状のあらゆるシステムはappend-only。マシン・アンラーニングは未解決。「TikTokフィードが汚染されたから新しいアカウントを作る」のように、一度汚染されると忘れられないので回復不能。ノイズが書き込まれた瞬間に、検索は永続的に毒される。

3. **ファイルベース・アプローチは諦めであり、最終形ではない** — Claude CodeのCLAUDE.mdは Vector も Graph も LLM抽出も使わず、フラットファイルと手動キュレーションのみ。Embedding/RAG/Deep Research の波の後に来た「LLMに生のまま全部食わせる」への退却。動くが天井が低い。

---

## 6. 参考文献

### 6.1 サーベイ論文

- Hu et al. "Memory in the Age of AI Agents." arXiv:2512.13564, 2025.12
- Du. "Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers." arXiv:2603.07670, 2026.3
- Yang et al. "Graph-based Agent Memory: Taxonomy, Techniques, and Applications." arXiv:2602.05665, 2026.2
- Logan. "Continuum Memory Architectures for Long-Horizon LLM Agents." arXiv:2601.09913, 2026.1

### 6.2 システム論文

- Zhu et al. "AriadneMem." arXiv:2603.03290, 2026.2
- Mem0: arXiv:2504.19413 (https://mem0.ai)
- Graphiti/Zep: arXiv:2501.13956 (https://zep.ai)
- MemGPT/Letta: arXiv:2310.08560 (https://letta.com)
- HydraDB/Cortex: https://research.hydradb.com/cortex.pdf
- MemOS: arXiv:2507.03724 (https://github.com/MemTensor/MemOS)

### 6.3 神経科学的基盤

- McClelland, McNaughton & O'Reilly. "Why there are complementary learning systems." *Psychological Review*, 102(3), 419-457, 1995
- Wixted et al. *PNAS*, 111, 9621-9626, 2014
- Gastaldi et al. *Nat Sci Rep*, 2025
- Wimmer et al. *Nat Neurosci*, 17, 2014
- Barbosa et al. *J Neurosci*, 2020

### 6.4 製品・ツール

- Supermemory (https://supermemory.ai)
- Cognee (https://cognee.ai)
- Memori / Gibson AI (https://github.com/memOai/memori)
- Nowledge (https://nowledge-labs.ai)
- mem9 (https://github.com/mem9-ai/mem9)
- OpenViking (https://github.com/volcengine/OpenViking)

### 6.5 ベンチマーク

- LongMemEval (Wu et al., 2024)
- MABench (Hu et al., ICLR 2026, https://github.com/HUST-AI-HYZ/MemoryAgentBench)
- MemoryArena: arXiv:2602.16313, 2026.2
- LOCOMO: https://snap-research.github.io/locomo

### 6.6 その他引用

- Karpathy, X post (2026.3.25): LLMパーソナライゼーションの問題提起
- @TaNGSoFT, X post (2026.3.23): 生物学的メモリの3サブシステム
- @parcadei, X post (2026.3.25): MIMIR が multi-hop で 39%、5.57× SOTA

---

**著者連絡先:** Han Xiao
X: x.com/hxiao | GitHub: github.com/hanxiao | LinkedIn: linkedin.com/in/hxiao87 | Blog: hanxiao.io
