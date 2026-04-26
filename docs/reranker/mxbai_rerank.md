# Mixedbread mxbai-rerank 市場調査レポート

> 調査日: 2026年4月25日

---

## 基本情報

| 項目 | 内容 |
|------|------|
| プロダクト名 | mxbai-rerank-v2（mxbai-rerank-base-v2 / mxbai-rerank-large-v2） |
| 開発元 | Mixedbread AI（ドイツ拠点のAIスタートアップ） |
| 公式URL | https://www.mixedbread.com/ |
| ブログ発表 | https://www.mixedbread.com/blog/mxbai-rerank-v2 |
| リリース日 | 2025年3月13日（v2）、2024年2月29日（v1） |
| GitHub | https://github.com/mixedbread-ai/mxbai-rerank |
| ライセンス | Apache 2.0（完全オープンソース） |
| 価格（API） | リランキング付き検索：$7.50 / 1,000クエリ、Basicプラン（無料）：月100クエリ、Scaleプラン：月額$20、Enterpriseプラン：カスタム |
| デプロイ方式 | Hugging Face ダウンロード（無料）・Mixedbread Managed API・RunPod Serverless・セルフホスト |

### モデルファミリー

| モデル | パラメータ数 | 別名 | コンテキスト長 | レイテンシ（A100） |
|--------|-------------|------|--------------|-----------------|
| mxbai-rerank-base-v2 | 0.5B | ProRank-0.5B | 8K tokens（32K互換） | 0.67秒 |
| mxbai-rerank-large-v2 | 1.5B | ProRank-1.5B | 8K tokens（32K互換） | 0.89秒 |
| mxbai-rerank-large-v1 | （先代） | — | 〜 | 2.24秒 |

---

## 市場ポジション

### OSSリランカー市場での位置付け

mxbai-rerank-v2は、2025年3月のリリース時点で**OSSリランカー市場のSOTA（State of the Art）**として広く認知されている。`AnswerDotAI/rerankers`ライブラリには「現在のオープンソース最先端モデル」として組み込まれており、LlamaIndex・Haystack・HuggingFace Transformers等の主要エコシステムとの統合も完備している。

リランカー市場全体は以下のカテゴリに大別できる：

| カテゴリ | 代表モデル | mxbai-rerankの位置 |
|----------|-----------|------------------|
| クローズドソースAPI | Cohere Rerank 4 Pro、Voyage Rerank 2 | Apache 2.0で完全OSS代替 |
| OSS大型モデル | bge-reranker-v2-gemma（2.5B）、Qwen3-Reranker-8B | 小型で高速・高精度 |
| OSS軽量モデル | BGE-M3 reranker、FlashRank | 精度で上回る |
| 商用特化OSS | Contextual AI Reranker v2、Jina Reranker v3 | ベンチマーク競合関係 |

月間ダウンロード数はHugging Face上でmxbai-rerank-large-v2が**約350,430回/月**に達し（2025年時点）、OSS採用の広さを示している。

### 対Cohere / Voyage比較（市場ポジショニング）

- **vs. Cohere Rerank 3.5**（BEIR: 55.39）：base-v2（55.57）がわずかに上回り、large-v2（57.49）は明確に超える
- **vs. Voyage Rerank 2**（BEIR: 54.54）：base-v2・large-v2ともに上回る
- **コスト面**：Apache 2.0のOSSのため、セルフホスト時はライセンスコストゼロ。Cohere（商用API）に対してコスト優位

---

## 開発元のアピールポイント

Mixedbreadが公式に強調する差別化ポイントは以下の通り：

### 1. 強化学習（RL）による3段階訓練

従来のクロスエンコーダーとは異なり、mxbai-rerank-v2は**3段階のRL訓練**を採用している：

1. **GRPO（Guided Reinforcement Prompt Optimization）**：関連文書に「1」、非関連文書に「0」を出力するよう訓練し、スコアリングの根拠に基づく推論を実現
2. **コントラスト学習（Contrastive Learning）**：埋め込みモデルと同様のセマンティック理解を深化させ、意味的類似性をスコアに反映
3. **嗜好学習（Preference Learning）**：人間の判断に合わせた順序付けを最適化し、ユーザー期待とアラインメント

この訓練方法により「**バックボーンモデルが見えない思考を経由して関連性スコアを出力する**」点が最大の差別化ポイントとされている。

### 2. 前世代比での大幅な性能向上

v1からv2にかけてBEIRスコアが**8〜11ポイント向上**しており、特に多言語・コード検索タスクで飛躍的な改善を実現している。

### 3. 広いユースケースカバレッジ

- **100以上の言語**への対応
- **テキスト・コード・JSON・構造化データ**に対応
- **LLMツール呼び出し選択**（MCPエージェント用途）への対応
- **長文書リランキング**：8K tokens（32K互換）

### 4. 高効率・高速推論

- **bge-reranker-v2-gemma（2.5B）の8倍高速**（ベンチマーク値）で同等以上の精度
- **bge-reranker-v2-m3との比較**：4.5倍高速
- 大型モデル（2.5B）を大幅に下回るパラメータ数（1.5B）で競合する精度を達成

### 5. 完全なオープンソース

Apache 2.0ライセンスのため、商用利用・改変・再配布が完全に自由。セルフホストによるデータプライバシー確保も可能。

### 6. 開発元の誠実さ（信頼性アピール）

リリース前にデータリークを発見した際、モデルと全ベンチマークを即時撤回し再訓練を実施した経緯を公式に開示している。「正しい方法でやること」を優先した姿勢として業界内でポジティブに評価されている。

---

## 第三者評価：強み

### 1. OSSリランカーのSOTAとしての認知

2025年3月のリリース直後から、複数の技術メディア・研究者コミュニティが「最も強力なOSSリランカー」として言及している。`AnswerDotAI/rerankers`ライブラリへの正式採用はエコシステムからの信任を示す代表的指標である。

### 2. RAGパイプラインへの広い採用

LlamaIndex・Haystack・Infinityサーバー等との統合が早期に整備されており、実際の本番RAGシステムへの採用事例が多い。Hugging Faceでの月間ダウンロード数（約350K回）がこれを裏付けている。

### 3. 多言語対応の強さ

英語（BEIR）のみならず、中国語（C-Pack: 84.16、large-v2）・多言語（Mr.TyDi: 29.79）でも高スコアを記録しており、多言語RAGシステムへの適性が第三者ベンチマークで確認されている。

### 4. コード・技術文書検索への適性

コード検索タスク（32.05、large-v2）で優秀なスコアを示しており、技術系RAGシステムへの強さが評価されている。

### 5. 軽量モデルでの高精度実現

0.5B（base-v2）がCohere Rerank 3.5（55.39）を上回る55.57を達成しており、「小さくて強い」モデルとして効率性が評価されている。

### 6. シンプルな実装

sentence-transformers・mxbai-rerankパッケージを通じてわずか数行のコードで導入可能。既存検索パイプラインへのアドオンとして追加しやすいアーキテクチャ。

---

## 第三者評価：弱点・批判点

### 1. 超小型モデル（xsmall/v1系）のパフォーマンス問題

AIMultiple社の独立ベンチマーク（Amazonレビュー145,000件）では、**mxbai-rerank-xsmall（70Mパラメータ）がHit@1: 64.67%**と最下位を記録し「改善がノイズの範囲内」と評価されている。レポートは「小規模モデルでは十分な判断能力を持たない可能性がある」と警告しており、v2に限らずモデル選択に注意が必要とされる。

### 2. ベンチマークの自己申告性

mxbai-rerank-v2の主要ベンチマーク数値（BEIR 57.49等）は**開発元自身が公表したもの**であり、独立した第三者機関による完全な再現評価が不足している。学術論文（arxiv:2508.16757）での比較はv1系が主体であり、v2の独立検証は限定的である。

### 3. 新興競合による相対的地位の変化

2025年後半以降に登場したモデルとの比較：
- **Jina Reranker v3**（0.6B）：検索では61.85（BEIR近似）とmxbai-large-v2の61.44を上回ると報告（Jinaの自己発表値）
- **Contextual AI Reranker v2**（1B〜6B）：エンタープライズ向け実世界ベンチマークでmxbai-v2を上回ると主張
- **Zerank-2**：法律・医療・金融等の専門ドメインで高評価

リリース時の「SOTA」は2025年後半以降に複数の競合に追い抜かれる構造にあり、継続的な上位維持が課題である。

### 4. セルフホスト時のインフラ管理負担

Apache 2.0 OSSのため「セルフホスト無料」であるが、裏返すと**本番グレードのインフラ管理は自己責任**となる。Cohere等の商用APIと異なりSLA・サポート体制が標準では提供されない。

### 5. 長いコンテキストでの実際のパフォーマンス

8K（32K互換）のコンテキスト対応を謳うが、長文書での実際の精度低下については独立した評価データが乏しい。長文書リランキングは文書内の重要箇所特定に課題が残る可能性がある。

### 6. ドメイン特化の限界

汎用ベンチマーク（BEIR）では高スコアを示す一方、金融・法律・医療等の専門ドメインでの優位性は明確でない。BEIRのTouche（argumentative queries）ではmxbai-baseが34.32と相対的に低迷しており、論争的・曖昧なクエリへの対応は課題とされる。

### 7. 価格透明性の低さ

Managed APIの料金体系（$7.50/1,000クエリ）はリランキング込み検索クエリの価格であり、スタンドアロンのリランキングAPIの単体価格情報が公式サイトで確認しにくい。

---

## ベンチマーク結果

### 公式ベンチマーク（開発元発表・2025年3月）

| モデル | BEIR（Avg NDCG@10） | 多言語（Mr.TyDi） | 中国語（C-Pack） | コード検索 | レイテンシ（A100） |
|--------|---------------------|-----------------|----------------|----------|-----------------|
| **mxbai-rerank-large-v2** | **57.49** | 29.79 | 84.16 | 32.05 | 0.89秒 |
| **mxbai-rerank-base-v2** | **55.57** | 28.56 | 83.70 | 31.73 | 0.67秒 |
| mxbai-rerank-large-v1 | 49.32 | 21.88 | 72.53 | 30.72 | 2.24秒 |
| Cohere Rerank 3.5 | 55.39 | — | — | — | — |
| Voyage Rerank 2 | 54.54 | — | — | — | — |
| bge-reranker-v2-gemma | — | — | — | — | 8倍遅い（large-v2比） |

### 第三者論文での数値（arxiv:2508.16757、v1系中心）

BEIRの個別タスクでの評価（NDCG@10、v1系モデル）：

| タスク | mxbai-xsmall | mxbai-base | mxbai-large |
|--------|-------------|-----------|------------|
| TREC-DL19 | 68.95 | 72.49 | 71.53 |
| TREC-DL20 | 63.11 | 67.15 | 69.45 |
| COVID | 80.80 | 84.00 | 85.33 |
| NFCorpus | 34.44 | 35.64 | 37.08 |
| Touche | 39.44 | 34.32 | 36.90 |
| DBPedia | 42.50 | 42.50 | 44.51 |
| SciFact | 68.73 | 72.33 | 75.10 |
| Signal | 29.40 | 30.20 | 31.90 |
| News | 53.00 | 51.92 | 51.90 |
| Robust04 | 53.87 | 55.59 | 58.67 |

論文の知見：COVID・SciFact（科学・医療領域）で高スコア。Touche（論争的クエリ）は相対的に低迷。

### 独立ベンチマーク（AIMultiple社）

Amazonレビュー（145,000件）・300クエリによる商品検索タスクでのHit@1評価：

| モデル | Hit@1 | パラメータ | レイテンシ |
|--------|-------|-----------|---------|
| nemotron-rerank-1b | 83.00% | 1.2B | 243ms |
| gte-modernbert-base | 83.00% | 149M | 188ms |
| jina-reranker-v3 | 81.33% | 560M | 188ms |
| Qwen3-Reranker | 77.67% | 4B | 1,000ms+ |
| **mxbai-xsmall（v1）** | **64.67%** | 70M | 低 |

**注意**：本ベンチマークはmxbai-xsmall（v1系・最軽量版）のみを評価対象としており、v2のbase/largeは含まれていない。

---

## 競合比較

### OSSリランカー全体マップ（2025年時点）

| モデル | 開発元 | パラメータ | ライセンス | BEIR NDCG@10 | 特徴 |
|--------|-------|-----------|-----------|-------------|------|
| **mxbai-rerank-large-v2** | Mixedbread | 1.5B | Apache 2.0 | 57.49 | RL訓練、多言語、コード対応 |
| **mxbai-rerank-base-v2** | Mixedbread | 0.5B | Apache 2.0 | 55.57 | 軽量高精度 |
| bge-reranker-v2-gemma | BAAI | 2.5B | Apache 2.0 | 〜56台 | Gemmaベース、高精度 |
| bge-reranker-v2-m3 | BAAI | 568M | Apache 2.0 | 〜54台 | 多言語強み |
| Jina Reranker v3 | Jina AI | 0.6B | CC BY-NC 4.0 | 〜61台（Jina発表値） | Listwise、低レイテンシ |
| Contextual AI Reranker v2 | Contextual AI | 1B/2B/6B | Apache 2.0 | 競合水準 | 命令フォロー、実世界強 |
| Qwen3-Reranker-0.6B | Alibaba | 0.6B | Apache 2.0 | 〜60台（自社発表） | LLMベース、多言語 |
| Qwen3-Reranker-8B | Alibaba | 8B | Apache 2.0 | 〜64台（自社発表） | LLM最大 |
| Zerank-2 | ZeroEntropy | 非公開 | 非商用 | 高（自社発表） | ドメイン特化、命令対応 |

### vs. Cohere Rerank（商用APIとの比較）

| 比較軸 | mxbai-rerank-large-v2 | Cohere Rerank 4 Pro |
|--------|----------------------|-------------------|
| ライセンス | Apache 2.0（OSS） | 商用API |
| BEIR NDCG@10 | 57.49 | 〜55〜57台（推定） |
| セルフホスト | 可能 | 不可 |
| データプライバシー | 完全制御可 | API経由 |
| SLA/サポート | なし（Enterpriseは別途） | あり |
| 価格 | セルフホスト無料 | クエリ課金 |

### vs. BGE-Reranker-v2-M3（OSS軽量モデルとの比較）

| 比較軸 | mxbai-rerank-base-v2 | BGE-Reranker-v2-M3 |
|--------|----------------------|-------------------|
| パラメータ | 0.5B | 568M |
| BEIR NDCG@10 | 55.57 | 〜54台 |
| レイテンシ | 0.67秒 | やや遅い |
| 多言語 | 100言語+ | 100言語+ |
| 訓練方法 | RL（3段階） | 従来型 |

### vs. Jina Reranker v3（新興OSS競合）

| 比較軸 | mxbai-rerank-large-v2 | Jina Reranker v3 |
|--------|----------------------|-----------------|
| パラメータ | 1.5B | 0.6B |
| ライセンス | Apache 2.0 | CC BY-NC 4.0（非商用） |
| BEIR（各社発表値） | 57.49 | 〜61台（Jina値） |
| アーキテクチャ | Cross-encoder（Qwen2.5ベース） | Listwise（Qwen3ベース） |
| コンテキスト | 8K（32K互換） | 131K |
| レイテンシ | 0.89秒 | 〈200ms（自社値） |
| 商用利用 | 完全自由 | 非商用ライセンス（要注意） |

**重要な留意点**：Jina Reranker v3はCC BY-NC 4.0ライセンスのため商用利用不可。mxbai-rerank-v2はApache 2.0で商用利用完全自由という点で差別化される。

### 総合ポジショニング評価

```
精度（高）
  ^
  |  Zerank-2          Qwen3-8B
  |          Jina-v3
  |  Contextual-v2
  |       mxbai-large-v2  ← Apache 2.0 OSSとして最高水準
  |  mxbai-base-v2
  |       Cohere 3.5 / Voyage 2
  |  BGE-v2-M3
  |
  +-----------------------------------> サイズ効率（小さい→右）
```

mxbai-rerank-v2 largeは「**Apache 2.0 OSSリランカーとしての精度トップ層**」に位置し、商用利用可能なOSSという観点では最も有力な選択肢の一つ。ただし2025年後半以降、Contextual AI v2やQwen3-Rerankerシリーズが競合に台頭している。

---

## 参考リンク

### 公式リソース
- [Mixedbread 公式サイト](https://www.mixedbread.com/)
- [mxbai-rerank-v2 発表ブログ](https://www.mixedbread.com/blog/mxbai-rerank-v2)
- [mxbai-rerank-large-v2 HuggingFace](https://huggingface.co/mixedbread-ai/mxbai-rerank-large-v2)
- [mxbai-rerank-base-v2 HuggingFace](https://huggingface.co/mixedbread-ai/mxbai-rerank-base-v2)
- [GitHub リポジトリ](https://github.com/mixedbread-ai/mxbai-rerank)
- [Mixedbread 料金ページ](https://www.mixedbread.com/pricing)

### 第三者評価・ベンチマーク
- [How Good are LLM-based Rerankers? (arxiv:2508.16757)](https://arxiv.org/html/2508.16757v1)
- [Reranker Benchmark: Top 8 Models Compared（AIMultiple）](https://aimultiple.com/rerankers)
- [Top 7 Rerankers for RAG（Analytics Vidhya）](https://www.analyticsvidhya.com/blog/2025/06/top-rerankers-for-rag/)
- [Best Rerankers for RAG Leaderboard（Agentset）](https://agentset.ai/rerankers)

### 競合比較関連
- [Jina Reranker v3 論文（arxiv:2509.25085）](https://arxiv.org/pdf/2509.25085)
- [Contextual AI Reranker v2 発表](https://contextual.ai/blog/rerank-v2)
- [Cohere vs BGE Reranker 比較（Agentset）](https://agentset.ai/rerankers/compare/cohere-rerank-4-fast-vs-baaibge-reranker-v2-m3)

### エコシステム統合
- [LlamaIndex mixedbread Rerank Cookbook](https://docs.llamaindex.ai/en/stable/examples/cookbooks/mixedbread_reranker/)
- [Haystack mixedbread AI 統合](https://haystack.deepset.ai/integrations/mixedbread-ai)
- [Together AI mxbai-rerank-large-v2](https://www.together.ai/models/mxbai-rerank-large-v2)
- [RunPod mxbai-rerank-large-v2](https://www.runpod.io/models/mixedbread-ai-mxbai-rerank-large-v2)
