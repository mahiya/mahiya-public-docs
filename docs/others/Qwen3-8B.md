# Qwen3-8B アーキテクチャ解析レポート

**Hugging Face リポジトリ**: Qwen/Qwen3-8B
**URL**: https://huggingface.co/Qwen/Qwen3-8B
**解析対象シャード**: `model-00001-of-00005.safetensors` (3.996 GB), `model-00005-of-00005.safetensors` (1.245 GB)
**解析日**: 2026-04-16

## サマリ
- **アーキテクチャ系統**: LLaMA 系 decoder-only Transformer (Qwen3 世代・dense)
- **総パラメータ数**: **8,190,735,360 ≒ 8.19 B**(埋め込み 622M + 36層本体 6.95B + 最終 norm 4K + `lm_head` 622M)
- **特徴的な要素**: GQA (32 Q / 8 KV, g=4), QK-Norm (per-head RMSNorm), SwiGLU (拡張比 3.0×), RMSNorm, RoPE (θ=1,000,000, 40,960 コンテキスト), **attention bias なし**・**`lm_head` untied**

## 1. メタ情報 / ファイル
safetensors のメタデータは `{"format": "pt"}` のみで、独自の量子化情報やカスタム属性は一切埋め込まれていない。BF16 のまま 5 シャードに分割され、総容量 16.38 GB は「総パラメータ数 × 2 byte」と 0 バイト単位で一致する。先頭(embed + 層 0–7)と末尾(lm_head)の 2 シャードだけで全キー命名規約とテンソル形状を確定できる構成になっており、index.json による完全な整合性チェックが可能。

| 項目 | 値 | 備考 |
|--|--|--|
| safetensors metadata | `{"format": "pt"}` | 標準の PyTorch 保存メタのみ |
| シャード構成 | 5 分割, 総 16,381,470,720 bytes (≈ 16.38 GB) | `model.safetensors.index.json` より |
| ダウンロード済みシャード | `model-00001-of-00005.safetensors` (3,996,250,744 B), `model-00005-of-00005.safetensors` (1,244,659,840 B) | 先頭(embed + layers 0–7)と末尾(lm_head)で全構造を確定 |
| 付随ファイル | `config.json`, `tokenizer_config.json`, `generation_config.json`, `model.safetensors.index.json` | 取得済み |

## 2. モデル識別
`architectures: ["Qwen3ForCausalLM"]` と `model_type: qwen3` により transformers 本体実装(>=4.51)で直接ロード可能で、`trust_remote_code=True` を要求するカスタムコード(`auto_map`)は一切含まれない。キー命名は `model.embed_tokens` / `model.layers.<i>.self_attn.{q,k,v,o}_proj` / `mlp.{gate,up,down}_proj` という LLaMA 系 HF 実装の標準様式に完全準拠しており、既存 LLaMA 系ツールチェーン(vLLM, TGI, llama.cpp 等)との互換性が高い。

| 項目 | 値 | 根拠 |
|--|--|--|
| `architectures` | `["Qwen3ForCausalLM"]` | config.json |
| `model_type` | `qwen3` | config.json |
| キー prefix の系統 | `model.embed_tokens.weight` / `model.layers.<i>.self_attn.{q,k,v,o}_proj` / `model.layers.<i>.mlp.{gate,up,down}_proj` → **LLaMA 系 HF 実装** | safetensors キー |
| `auto_map` (custom code) | なし(`Qwen3ForCausalLM` は `transformers>=4.51` 本体実装) | config.json |

## 3. 全体構造
decoder-only 36 層 × hidden 4096 で、同規模の LLaMA-3 8B(32 層)よりやや深く設計されている。語彙サイズ 151,936 は多言語・コード対応を意識した大規模語彙で、`tie_word_embeddings=false` により入力埋め込みと出力 `lm_head` が独立重みを持つ(両者で計 1.24 B パラメータを消費)。最終 RMSNorm 重みはシャード 4 末尾に格納され、bias 項は存在しない。

| 項目 | 値 | 根拠 |
|--|--|--|
| 構成 | **decoder-only** | `model.layers.*` のみで encoder/cross-attn キーなし |
| `num_hidden_layers` | **36** | `model.safetensors.index.json` の `layers.N.*` 最大インデックス 35, +1 = 36(config と一致) |
| `hidden_size` | **4096** | `model.embed_tokens.weight.shape = (151936, 4096)` |
| `vocab_size` | **151,936** | 同上、第 1 次元 |
| 最終正規化 | RMSNorm, `shape=(4096,)` (推定・シャード 4 に格納) | `model.norm.weight` が index.json の shard 4 末尾にあり、`.bias` キーなし |
| `tie_word_embeddings` | **False**(untied) | `lm_head.weight` がシャード 5 に独立して存在。config も `false` |

## 4. Attention サブレイヤー
**32 Query ヘッド / 8 KV ヘッドの GQA(比 4:1)** を採用しており、KV キャッシュを MHA 比で 1/4 に圧縮できる長文推論向け構成。Qwen3 世代の最大の設計変更は **QK-Norm の導入** と **attention bias の撤廃** で、Q/K を head_dim 方向(128次元)に RMSNorm で正規化することで長コンテキスト時の attention logit 爆発を抑制する。MLA(DeepSeek-V2/V3 系の latent 圧縮)は採用されておらず、標準的な q/k/v/o_proj 構成を維持。

| 項目 | 値 | 根拠 |
|--|--|--|
| Attention 種別 | **GQA** (group=4) | `q_proj` 出力 4096 vs `k_proj`/`v_proj` 出力 1024、比 4:1 |
| `num_attention_heads` | **32** | `q_proj.shape[0] / head_dim = 4096 / 128` |
| `num_key_value_heads` | **8** | `k_proj.shape[0] / head_dim = 1024 / 128` |
| `head_dim` | **128** | config.head_dim(`hidden_size / H = 4096/32 = 128` と整合) |
| QK-Norm | **あり**(per-head_dim RMSNorm) | `self_attn.q_norm.weight.shape=(128,)` / `self_attn.k_norm.weight.shape=(128,)` |
| バイアス項 | **なし** | `self_attn.*_proj.bias` キーは一切存在しない(config `attention_bias: false` と一致) |
| MLA パラメータ | 該当なし | `q_a_proj` / `kv_a_proj_with_mqa` 等のキー不在 |
| 出力射影 `o_proj` | `shape=(4096, 4096)`, BF16 | `self_attn.o_proj.weight` |

**Qwen3 世代の特徴点**: Qwen2 系で存在していた `q_proj.bias` / `k_proj.bias` / `v_proj.bias` が消え、代わりに **QK-Norm**(q, k をヘッド次元方向に RMSNorm)が導入された。`q_norm`/`k_norm` の shape が `(128,)` = `head_dim` であることから、全ヘッド共通重みではなく head_dim 方向の per-channel scale として適用される(各ヘッドに同一重みがブロードキャスト)。

## 5. 位置埋め込み
RoPE の `θ=1,000,000`(LLaMA-2 の 10,000 の 100 倍)により **40,960 トークン**のネイティブコンテキスト長を確保している。`rope_scaling=null` なので YaRN / NTK 等の外挿スケーリングは事前適用されておらず、長文運用時は推論側で動的に設定する必要がある。Sliding Window Attention は全層で無効化(`use_sliding_window: false`)されており、全 36 層がフルアテンションで動作する。

| 項目 | 値 | 根拠 |
|--|--|--|
| 位置埋め込み方式 | **RoPE**(Rotary Position Embeddings) | 絶対/相対の学習重みキーなし、q/k に独立位置パラメータなし |
| `rope_theta` | **1,000,000** | config.json |
| `rope_scaling` | `null`(スケーリングなし) | config.json |
| `partial_rotary_factor` | 未設定(全 head_dim に RoPE 適用) | config.json |
| `max_position_embeddings` | **40,960** | config.json |
| Sliding Window | `sliding_window: null`, `use_sliding_window: false`, `max_window_layers: 36` | config.json(全層フルアテンション) |

## 6. MLP / FFN サブレイヤー
SwiGLU(gate/up/down の 3 射影)で `intermediate_size=12,288`、**拡張比 3.0×** と近年モデルとしては控えめな設定(LLaMA-3 8B は 3.5×、Qwen2-7B は 5.4×)。これにより FFN パラメータを 5.44 B に抑え、その分を深さ(36 層)と語彙(152K)に振り分けた配分バランス。MoE 関連キー(`experts.*`, `gate.weight`, `shared_experts.*` 等)は一切存在せず、完全な dense モデル(同世代には別途 `Qwen3-*-MoE` が存在)。

| 項目 | 値 | 根拠 |
|--|--|--|
| MLP タイプ | **SwiGLU** | `mlp.gate_proj` + `mlp.up_proj` + `mlp.down_proj` が全 36 層に存在 |
| `hidden_act` | **silu** | config.json (SwiGLU の非線形) |
| `intermediate_size` | **12,288**(拡張比 **3.0×**) | `gate_proj.shape = (12288, 4096)` → 12288/4096 = 3.0 |
| MoE | **なし** | `experts.*` / `gate.weight` / `shared_experts.*` キーはいずれも不在 |
| `num_experts` | 該当なし | — |
| `num_experts_per_tok` | 該当なし | — |
| `moe_intermediate_size` | 該当なし | — |
| Shared experts | 該当なし | — |
| Dense/MoE 混在 | dense のみ | 全層同一構造 |

## 7. 正規化層
全て **RMSNorm**(bias なし)で、`rms_norm_eps=1e-6` と近年標準値。1 層あたり **4 個**の RMSNorm(Pre-Norm 2 個 + QK-Norm 2 個)を持つのが Qwen3 の特徴で、Qwen2 の 2 個から倍増している。QK-Norm の追加コストは head_dim=128 の重み 2 本(256 パラメータ/層)と微小だが、attention の数値安定性を大幅に改善する。

| 項目 | 値 | 根拠 |
|--|--|--|
| 正規化タイプ | **RMSNorm** | 全 `*layernorm.weight` / `*_norm.weight` キーに対応する `.bias` が存在しない |
| `rms_norm_eps` | **1e-06** | config.json |
| 層内正規化数 | **Pre-Norm × 2 + QK-Norm × 2**(= 1 層あたり 4 個の RMSNorm) | `input_layernorm`, `post_attention_layernorm`, `self_attn.q_norm`, `self_attn.k_norm` |

## 8. 数値精度 / 量子化
**全 82 テンソルが BF16 単一精度**で保存されており、FP8 / INT8 / INT4 などの量子化は一切適用されていない(`quantization_config` なし、`qweight`/`scales`/`qzeros`/`g_idx` キー不在)。理論ファイルサイズ(総 numel × 2 byte)と実ファイルサイズが完全一致することから、量子化派生モデル(AWQ/GPTQ/GGUF)はこのベースウェイトから別途生成されたものと判断できる。ファインチューニングや蒸留のベースとして使いやすい素の状態。

| 項目 | 値 | 根拠 |
|--|--|--|
| dtype 分布 | **全テンソル BF16** | shard 1 (81 keys) + shard 5 (1 key) の全 82 テンソルが `BF16`。index 合計サイズ 16.38 GB ≒ 総 numel × 2 byte と完全一致 |
| 量子化スキーム | **未量子化**(bfloat16 のまま保存) | `qweight` / `scales` / `qzeros` / `g_idx` キーなし、config に `quantization_config` なし |
| 混合精度 | なし(単一 dtype) | dtype 集計結果 |

## 9. パラメータ数 / メモリ
総 **8.19 B** のうち本体(attention + MLP)が 6.95 B(約 85%)、埋め込み+lm_head が 1.24 B(約 15%)という配分で、語彙サイズが大きいため埋め込み系の比率が LLaMA-3 8B(約 8%)より高い。重みだけで BF16 時 16.38 GB、単精度(FP32)なら 32.76 GB 必要で、24 GB GPU では BF16 のまま載り、16 GB 以下では 4bit 量子化がほぼ必須。KV キャッシュは **1 トークンあたり 144 KB**(GQA 効果で MHA 比 1/4)、最大長 40,960 で約 5.9 GB と推論時のメモリ負荷も計算しやすい。

| 部位 | パラメータ数 | 計算根拠 |
|--|--|--|
| 埋め込み | **622,329,856** | 151,936 × 4,096 |
| Attention (全 36 層) | **1,509,958,656** | 1 層 = q(4096²) + k(1024·4096) + v(1024·4096) + o(4096²) + q_norm(128) + k_norm(128) = 41,943,296 |
| MLP / FFN (全 36 層) | **5,435,817,984** | 1 層 = 3 × (4096·12288) = 150,994,944(SwiGLU の gate/up/down) |
| 正規化 (全 36 層 × 2 + 最終) | **294,912 + 4,096 = 299,008** | input_layernorm + post_attention_layernorm = 8,192 per layer × 36 + model.norm (4,096) |
| 出力ヘッド (`lm_head`) | **622,329,856** | untied、151,936 × 4,096 |
| **合計** | **8,190,735,360 (8.191 B)** | 全テンソル numel 総和(HF カードの 8190.7 M と一致) |
| 理論ファイルサイズ (BF16) | **16,381,470,720 bytes ≒ 16.38 GB** | 合計 × 2 byte |
| 実ファイルサイズ | **16,381,470,720 bytes**(`index.json` の `total_size`) | 実測と完全一致(乖離 0%) |
| 整合性 | **完全一致** | 量子化・fp8 等なし、BF16 そのままで保存されている |
| KV キャッシュ (BF16) | **2 × 36 × 8 × 128 × N × 2 = 147,456 × N byte** → 1 トークンあたり **144 KB** | seq=32,768 で ≈ 4.72 GB, seq=40,960 (max) で ≈ 5.90 GB |

## 10. タスクヘッド / アダプタ
純粋な因果言語モデリング用 `lm_head` のみを持ち、分類/QA/埋め込み用の補助ヘッドや LoRA アダプタは一切含まれていない、クリーンな base/instruct チェックポイント。`lm_head.weight` が独立シャード(shard 5)に分離されているため、ベース LM と出力層を別管理したい場合(語彙拡張や重み差し替え)に扱いやすい。用途別の派生は本ベースから追加学習で作る前提の構成。

| 項目 | 値 | 根拠 |
|--|--|--|
| ヘッド種別 | **`lm_head`**(言語モデリングのみ) | `lm_head.weight` のみ、分類/QA 等のキー不在 |
| プーリング (埋め込みモデル) | 該当なし(生成モデル) | — |
| LoRA / アダプタ | **なし** | `lora_A` / `lora_B` / `adapter.*` キー不在 |

## 11. マルチモーダル構成 (該当時のみ)
**テキスト単独のユニモーダルモデル**で、`vision_*` / `audio_*` / `mm_projector.*` / `patch_embed.*` 等のマルチモーダル関連キーは完全に不在。画像/音声対応が必要な場合は Qwen シリーズの別ブランチ(Qwen2-VL, Qwen2-Audio など)を選択する必要がある。

| 項目 | 値 | 根拠 |
|--|--|--|
| サブネット | **該当なし**(テキスト単独) | `vision_*` / `audio_*` / `mm_projector.*` / `patch_embed.*` キーいずれも不在 |
| ビジョンエンコーダ | 該当なし | — |
| 接続層 | 該当なし | — |
| 投影次元 | 該当なし | — |

## 12. 所見
- **系統の特定**: `Qwen3ForCausalLM` + LLaMA 型キー命名 + SwiGLU + RMSNorm + GQA(4:1)+ RoPE の組み合わせから、Qwen3 世代の **dense decoder-only LLM** と確定。MoE 版(`Qwen3-*-MoE`)ではない。
- **世代特有の目印**: Qwen2 系との差分は (a) **attention bias の撤廃**、(b) **QK-Norm の導入**(per `head_dim` の RMSNorm を q/k に適用)、(c) `tie_word_embeddings=false` で **`lm_head` を独立保持**、の 3 点。同規模の LLaMA-3 8B と比べると、`hidden_size` (4096 vs 4096) と `num_hidden_layers` (36 vs 32) は近いが、`intermediate_size` が **12,288**(LLaMA-3 8B は 14,336)、`vocab_size` が **151,936**(LLaMA-3 8B は 128,256)と大きく、コンテキスト長は **40,960**(RoPE θ = 1M)で LLaMA-3 の基本 8,192 より長い。
- **FFN 拡張比 3.0×**(= `12288/4096`)は近年のモデルとしては中庸(LLaMA-3 は 3.5×、Mistral-7B は ~3.5×、Qwen2-7B は 5.4×)。パラメータ配分は埋め込み+lm_head で **1.24 B**(全体の 15.2%)と相対的に大きく、語彙 152K の多言語対応に割り振られている。
- **未取得項目**: シャード 2/3/4(layers 8–35 と `model.norm.weight`)は未ダウンロード。ただし index.json 上で 8〜35 の各層は 0 番層と同一キー構成(11 キー × 層)であり、合計 numel も BF16 実ファイルサイズと 0 バイト単位で一致するため、構造は完全に確定している。
- **推奨される追加検証**: `tokenizer_config.json` によれば Qwen3 は chat template / `<think>` タグ対応(deep-thinking モード)が公式で、`generation_config.json` の EOS / stop トークン列をアプリ側で確認するとよい。
