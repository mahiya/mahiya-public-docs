# voyage-4-nano アーキテクチャ解析レポート

**Hugging Face リポジトリ**: voyageai/voyage-4-nano
**URL**: https://huggingface.co/voyageai/voyage-4-nano
**解析対象シャード**: model.safetensors (単一ファイル)
**参照論文**: 論文未公開 — Voyage AI 公式ブログ記事 "The Voyage 4 model family: shared embedding space with MoE architecture" (2026-01-15) および Model Card を参照
**解析日**: 2026-04-17

## サマリ
- **アーキテクチャ系統**: Qwen3 系 decoder-only Transformer を双方向 attention に改修したテキスト埋め込みモデル（カスタム `Qwen3BidirectionalModel`）
- **総パラメータ数**: 346,451,968（約 346M）— 埋め込み層 155.6M (44.9%) + Transformer 層 188.8M (54.5%) + 射影ヘッド 2.1M (0.6%)
- **特徴的な要素**: GQA (2:1), SwiGLU MLP, QK-Norm, 双方向 attention (非因果的), mean pooling + L2 正規化, 線形射影による埋め込み次元拡張 (1024→2048), Matryoshka Representation Learning (MRL), 量子化対応訓練, Voyage 4 シリーズ共有埋め込み空間

## 1. メタ情報 / ファイル

本モデルは単一の safetensors ファイルに全重みが格納されている。metadata は空辞書であり、HF 標準保存の典型パターン。BF16 で 0.645 GB と軽量で、理論値（346M × 2 bytes = 0.645 GB）と完全に一致する。カスタムモデリングコード `modeling_qwen3_bidirectional.py` が付随しており、`trust_remote_code=True` が必要。

| 項目 | 値 | 備考 |
|--|--|--|
| safetensors metadata | 空辞書 `{}` | HF 標準保存 |
| シャード構成 | 単一ファイル, 0.645 GB | index.json なし |
| ダウンロード済みシャード | `model.safetensors` (0.645 GB) | 全テンソル解析済み |
| 付随ファイル | config.json, tokenizer.json, tokenizer_config.json, config_sentence_transformers.json, modules.json, sentence_bert_config.json, vocab.json, modeling_qwen3_bidirectional.py | カスタムコード付き |

## 2. モデル識別

config.json の `architectures` は `Qwen3ForCausalLM` だが、`auto_map` で `Qwen3BidirectionalModel` にリダイレクトされる。この差異は意図的で、Qwen3 の標準 transformers 実装をベースに、カスタムコード (`modeling_qwen3_bidirectional.py`) で因果的 attention マスクを双方向マスクに差し替えている。Voyage AI は Qwen チーム (Alibaba) の OSS 貢献を Acknowledgments で明記しており、Qwen3 の 0.6B クラスのバックボーンをベースに埋め込み特化で再訓練したものと推定される。

| 項目 | 値 | 根拠 |
|--|--|--|
| `architectures` | `["Qwen3ForCausalLM"]` | config.json |
| `model_type` | `qwen3` | config.json |
| キー prefix の系統 | `model.layers.*.self_attn.q_proj` / `model.layers.*.mlp.gate_proj` → Qwen3/LLaMA 系 | safetensors キー |
| `auto_map` (custom code) | あり — `AutoModel` → `modeling_qwen3_bidirectional.Qwen3BidirectionalModel` | config.json |

## 3. 全体構造

12 層の Transformer で、hidden_size=1024。Qwen3 公式の 0.6B モデル（28 層, hidden_size=1024）と hidden_size は同一だが層数が大幅に削減（28→12）されている。Model Card では "180M [Non-embedding] + 160M [Embedding]" と記載されているが、実測では非埋め込みパラメータは約 190.9M であり、約 10M の差異がある（ブログの概数と推定）。`lm_head.weight` は存在せず、代わりに `linear.weight` (2048, 1024) で hidden_size=1024 から埋め込み次元 2048 へ線形射影している。`tie_word_embeddings=true` だが lm_head 自体が不要なため、実質的には意味をなさない。

| 項目 | 値 | 根拠 |
|--|--|--|
| 構成 | decoder-only（双方向 attention に改修） | キー prefix (`model.layers.*`) + カスタムコード |
| `num_hidden_layers` | 12 | `model.layers.{0-11}.*` の最大インデックス + 1 |
| `hidden_size` | 1,024 | `model.embed_tokens.weight.shape[1]` = 1024 |
| `vocab_size` | 151,936 | `model.embed_tokens.weight.shape[0]` = 151936 |
| 最終正規化 | RMSNorm, shape (1024,) | `model.norm.weight` — bias なし |
| `tie_word_embeddings` | True（config.json）— ただし lm_head 不在のため実質無関係 | config.json, `lm_head.weight` キー不在 |

## 4. Attention サブレイヤー

GQA を採用し、Q ヘッド数 16 に対して KV ヘッド数 8 の 2:1 比率である。これは Qwen3-0.6B と同じ GQA 構成で、KV キャッシュを半減する。`head_dim=128` は Qwen3 標準。最大の特徴は、カスタムコードで `is_causal=False` に設定し、`bidirectional_mask_function` により因果マスクを双方向マスクに差し替えている点である。これにより BERT のような全トークン間の双方向 attention を実現しつつ、Qwen3 の効率的な GQA・QK-Norm・Flash Attention 2 互換性をそのまま利用できる。NV-Embed (arXiv:2405.17428) などで示されたように、decoder-only LLM を双方向化することで埋め込み品質が向上するアプローチと同じ方針。

| 項目 | 値 | 根拠 |
|--|--|--|
| Attention 種別 | GQA (2:1) — 双方向 (非因果的) | `q_proj.shape[0]`=2048 / head_dim=128 = 16 heads, `k_proj.shape[0]`=1024 / 128 = 8 heads |
| `num_attention_heads` | 16 | config.json, `q_proj.weight` shape (2048, 1024) |
| `num_key_value_heads` | 8 | config.json, `k_proj.weight` shape (1024, 1024) |
| `head_dim` | 128 | config.json `head_dim=128` |
| QK-Norm | あり | `model.layers.*.self_attn.q_norm.weight` (128,), `k_norm.weight` (128,) 全 12 層に存在 |
| バイアス項 | なし | `attention_bias=false`, `*_proj.bias` キー不在 |
| MLA パラメータ | 該当なし | MLA 関連キー不在 |
| 出力射影 `o_proj` | shape (1024, 2048) | `model.layers.*.self_attn.o_proj.weight` |
| 双方向 attention | あり — `use_bidirectional_attention=true` | config.json + `modeling_qwen3_bidirectional.py` で `is_causal=False` |

## 5. 位置埋め込み

RoPE を使用し、base frequency `θ=1,000,000` は Qwen3 標準の長コンテキスト対応設定。`max_position_embeddings=40960` だが Model Card では 32,000 トークンのコンテキスト長と記載されており、実運用では 32K が推奨上限と思われる（40960 は内部マージンの可能性）。Sliding Window は無効化されている（`sliding_window=null`, `use_sliding_window=false`）。双方向 attention モデルでは位置情報の扱いが重要で、RoPE は相対位置を効率的にエンコードするため双方向コンテキストでも有効に機能する。

| 項目 | 値 | 根拠 |
|--|--|--|
| 位置埋め込み方式 | RoPE | Qwen3 系標準, config.json `rope_theta` |
| `rope_theta` | 1,000,000 | config.json |
| `rope_scaling` | null（なし） | config.json |
| `partial_rotary_factor` | 未設定 | config.json に記載なし |
| `max_position_embeddings` | 40,960 | config.json（Model Card では 32,000 コンテキスト長と記載） |
| Sliding Window | `sliding_window=null`, `use_sliding_window=false` — 無効 | config.json |

## 6. MLP / FFN サブレイヤー

SwiGLU（`silu` + gate 機構）を採用し、`gate_proj` + `up_proj` + `down_proj` の 3 層構成。拡張比は 3072/1024 = 3.0 で、Qwen3-0.6B（intermediate_size=3072）と同一。MoE は本モデルには採用されていないが、Voyage 4 ブログによれば `voyage-4-large` では MoE を採用して「初のプロダクショングレード MoE 埋め込みモデル」を実現しており、voyage-4-nano は dense 版の小型バリアントとして位置づけられている。

| 項目 | 値 | 根拠 |
|--|--|--|
| MLP タイプ | SwiGLU（gate + up + down の 3 層構成） | `gate_proj` + `up_proj` + `down_proj` キー存在 |
| `hidden_act` | `silu` | config.json |
| `intermediate_size` | 3,072 (拡張比 3072/1024 = 3.0) | `gate_proj.weight.shape[0]` = 3072 |
| MoE | なし | `experts.*` キー不在 |
| `num_experts` | 該当なし | — |
| `num_experts_per_tok` | 該当なし | — |
| `moe_intermediate_size` | 該当なし | — |
| Shared experts | なし | — |
| Dense/MoE 混在 | 全層 dense | — |

## 7. 正規化層

Qwen3 標準の Pre-Norm 構成で、各層に `input_layernorm` と `post_attention_layernorm` の 2 枚。Gemma 系のサンドイッチ正規化（4 枚/層）は採用していない。`rms_norm_eps=1e-06` は Qwen3 の標準値。

| 項目 | 値 | 根拠 |
|--|--|--|
| 正規化タイプ | RMSNorm | norm キーに `.bias` なし、config.json `rms_norm_eps` 存在 |
| `rms_norm_eps` | 1e-06 | config.json |
| 層内正規化数 | 2 枚/層: `input_layernorm` + `post_attention_layernorm` | safetensors キー一覧 — 標準 Pre-Norm |

## 8. 数値精度 / 量子化

全 135 テンソルが BF16 で統一されている。ただし本モデルは「量子化対応訓練 (Quantization-Aware Training)」を経ており、推論時に INT8/UINT8/Binary への量子化を最小限の品質劣化で適用可能。この QAT は重みの dtype ではなく出力埋め込みの後処理として適用されるため、safetensors 上は通常の BF16 のまま。sentence-transformers の `precision` 引数で `'int8'`, `'uint8'`, `'binary'`, `'ubinary'` を指定可能。

| 項目 | 値 | 根拠 |
|--|--|--|
| dtype 分布 | 全 135 テンソルが BF16 | safetensors inspect 結果 |
| 量子化スキーム | 未量子化（重み自体は BF16）— ただし QAT により出力の INT8/Binary 量子化対応 | `qweight`/`scales` キー不在, Model Card |
| 混合精度 | なし — 全テンソル BF16 統一 | dtype 集計 |

## 9. パラメータ数 / メモリ

Model Card の "180M + 160M = 340M" と実測 346M の差異は約 6M で、ブログの概数表記と推定される。Qwen3-0.6B（28 層, 587M パラメータ）から層数を 28→12 に大幅削減し、`linear.weight` による射影ヘッド（2.1M）を追加した構成。埋め込み層は vocab_size=151,936 × hidden_size=1,024 = 155.6M で全体の 44.9% を占める。KV キャッシュは GQA 2:1 の恩恵があるが、seq=32K で約 1.47 GB と本体の重みサイズ（0.645 GB）を大幅に超える。

| 部位 | パラメータ数 | 計算根拠 |
|--|--|--|
| 埋め込み (`model.embed_tokens`) | 155,582,464 (44.9%) | 151,936 × 1,024 |
| Attention (全 12 層) | 75,500,544 (21.8%) | (2,097,152 + 1,048,576 + 1,048,576 + 2,097,152 + 128 + 128) × 12 = 6,291,712 × 12 |
| MLP / FFN (全 12 層) | 113,246,208 (32.7%) | (3,145,728 × 3) × 12 = 9,437,184 × 12 |
| 正規化 (全 12 層 + final) | 25,600 (0.01%) | (1,024 × 2) × 12 + 1,024 |
| 射影ヘッド (`linear`) | 2,097,152 (0.6%) | 2,048 × 1,024 |
| **合計** | **346,451,968** | 全テンソル numel の合計 |
| 理論ファイルサイズ (BF16) | 0.645 GB | 346,451,968 × 2 bytes |
| 実ファイルサイズ | 0.645 GB | 実測値 |
| 整合性 | 完全一致 | 量子化なし、BF16 統一 |
| KV キャッシュ (seq=32,000) | 約 1.47 GB | 2 × 12 × 8 × 128 × 32,000 × 2 bytes = 1,572,864,000 bytes |

## 10. タスクヘッド / アダプタ

`lm_head` は存在せず、代わりに `linear.weight` (2048, 1024) による線形射影が追加されている。この層は hidden_size=1024 から埋め込み次元 2048 へアッププロジェクションを行う。Matryoshka Representation Learning (MRL) に対応しており、出力の先頭 256/512/1024/2048 次元を truncate して使用可能。mean pooling + L2 正規化で固定長テキスト埋め込みを生成する。instruction-following 型で、クエリには `"Represent the query for retrieving supporting documents: "` を、ドキュメントには `"Represent the document for retrieval: "` をプロンプトとして付与する。

| 項目 | 値 | 根拠 |
|--|--|--|
| ヘッド種別 | `linear` (2048, 1024) — hidden_size→埋め込み次元への射影 | safetensors キー `linear.weight` |
| プーリング | mean pooling + L2 正規化 | Model Card, `modeling_qwen3_bidirectional.py` のコード例 |
| 埋め込み次元 | 2,048（MRL で 1024/512/256 にも対応） | `linear.weight.shape[0]` = 2048, `config.num_labels=2048` |
| LoRA / アダプタ | なし | `lora_A`, `lora_B`, `adapter.*` キー不在 |

## 11. マルチモーダル構成

テキスト単独のユニモーダルモデルである。`vision_model.*`, `vision_tower.*`, `audio_*`, `mm_projector.*` 等のマルチモーダル関連キーは完全に不在。Voyage AI は `voyage-multimodal-3` で画像対応を提供しているが、Voyage 4 シリーズはテキスト埋め込み専用。

| 項目 | 値 | 根拠 |
|--|--|--|
| サブネット | なし — テキスト単独 | マルチモーダル関連キー prefix 不在 |
| ビジョンエンコーダ | 該当なし | — |
| 接続層 | 該当なし | — |
| 投影次元 | 該当なし | — |

## 12. 所見

**アーキテクチャ系統の特定根拠**: キー命名規則 (`model.layers.*.self_attn.q_proj`, `model.layers.*.mlp.gate_proj`)、config.json の `model_type: qwen3` / `architectures: ["Qwen3ForCausalLM"]`、QK-Norm の存在、SwiGLU MLP、および Qwen3 標準の 2 枚 Pre-Norm 構成から、Qwen3 バックボーンであることが確実。`auto_map` で `Qwen3BidirectionalModel` にリダイレクトし、因果マスクを双方向マスクに差し替えるカスタムコードが付随する。

**同世代モデルとの比較で目立つ点**:
- **双方向 attention + decoder-only**: BERT のような encoder モデルではなく、Qwen3 の decoder-only アーキテクチャを双方向化するアプローチ。NV-Embed や GritLM と同じ方針で、事前学習済み LLM の表現力を埋め込みに活用する。カスタムコードはわずか約 60 行で、`is_causal=False` と `or_mask_function` の差し替えのみで実現しており、実装の簡潔さが際立つ。
- **hidden_size→埋め込み次元の線形射影**: hidden_size=1024 から 2048 次元へアッププロジェクションする `linear.weight` は特異な設計。通常の埋め込みモデルは hidden_size をそのまま埋め込み次元とするか、ダウンプロジェクションするが、本モデルは逆方向に拡張する。これは Voyage 4 シリーズの共有埋め込み空間を実現するためで、`voyage-4-large` (MoE) から `voyage-4-nano` まで同一の 2048 次元空間を共有し、モデル間で埋め込みの互換性を保証する。
- **Matryoshka + QAT の組み合わせ**: 2048/1024/512/256 次元の MRL と INT8/Binary の量子化対応訓練を併用し、下流のベクトル DB コストを柔軟に調整可能。Voyage 4 ブログによれば、この組み合わせにより「品質損失を最小化しつつベクトル DB コストを大幅削減」できる。
- **Qwen3-0.6B からの層数削減**: 28 層 → 12 層と大幅に圧縮しつつ hidden_size=1024 は維持。これにより非埋め込みパラメータ約 190M、ファイルサイズ 0.645 GB と軽量ながら、既存の `voyage-3.5-lite` を上回る性能を実現（Voyage 4 ブログ）。

**解析時に未確認だった項目**:
- Voyage 4 シリーズの専用論文は 2026-04-17 時点で未公開。ブログ記事と Model Card の情報を基に記述した。
- `voyage-4-large` の MoE 構成の詳細は非公開（別のブログ記事 "Breaking the Dense Ceiling" に一部記載あり）。
- 共有埋め込み空間の訓練手法（どのように異なるサイズのモデル間で互換性を確保したか）は未公開。
- Qwen3-0.6B ベースの事前学習チェックポイントから fine-tune したのか、ゼロから訓練したのかは不明。
