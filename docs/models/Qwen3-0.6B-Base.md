# Qwen3-0.6B-Base アーキテクチャ解析レポート

**Hugging Face リポジトリ**: Qwen/Qwen3-0.6B-Base
**URL**: https://huggingface.co/Qwen/Qwen3-0.6B-Base
**解析対象シャード**: model.safetensors (単一ファイル / 1,192,135,096 bytes ≒ 1.11 GiB)
**解析日**: 2026-04-16

## サマリ

Qwen3-0.6B-Base は Alibaba が公開する Qwen3 シリーズの最小クラス(約 0.6B)で、LLaMA 系の命名規約を踏襲しつつ **QK-Norm** と **head_dim=128(hidden より広い attention 空間)** という Qwen3 独自の設計要素を備えた dense decoder-only Transformer である。以下はその要点。

- **アーキテクチャ系統**: LLaMA 系 decoder-only Transformer(Qwen3 dense, `Qwen3ForCausalLM`)
- **総パラメータ数**: 596,049,920(≒ 0.596B)。内訳: 埋め込み 155.58M、Attention 176.17M、MLP 264.24M、Norm 0.058M、LM ヘッドは tied(追加 0)
- **特徴的な要素**:
  1. GQA(16 クエリヘッド / 8 KV ヘッド, 比 2:1)
  2. **QK-Norm**(`q_norm` / `k_norm` を per-head 128 次元で保持)— Qwen3 系の識別子
  3. SwiGLU MLP(拡張比 3.0、`intermediate_size=3072`)
  4. RoPE(`rope_theta=1,000,000`、scaling なし、`max_position_embeddings=32,768`)
  5. Tied word embeddings(`lm_head.weight` 不在 & `tie_word_embeddings=true`)

## 1. メタ情報 / ファイル

このセクションでは、解析の**入力となった物理ファイルの構成**を記録する。safetensors は shape / dtype / 任意メタデータを含むヘッダと raw バイト列で構成されるフォーマットで、`metadata()` が空辞書(または `format: pt` のみ)なら Hugging Face 標準保存。モデルが大きい場合は `model.safetensors.index.json` により複数シャードに分割されるが、本モデルは 1.11 GiB と単一ファイルに収まるサイズのため分割なし。

| 項目 | 値 | 備考 |
|--|--|--|
| safetensors metadata | `{'format': 'pt'}` | PyTorch 由来、追加メタなし |
| シャード構成 | 単一ファイル、1,192,135,096 bytes | `model.safetensors.index.json` なし |
| ダウンロード済みシャード | `model.safetensors`(1.11 GiB) | 全重みをこの 1 ファイルから解析 |
| 付随ファイル | `config.json` / `tokenizer_config.json` / `generation_config.json` | 解析後も保持 |

## 2. モデル識別

モデルの素性は **`config.json` の `architectures` / `model_type`** と、**safetensors キーの prefix パターン**の 2 つから特定する。前者は Hugging Face Transformers がロード時に使うクラス名、後者は「重みが実際にどのモジュール階層に配置されているか」を示す。両者が整合し、かつ `auto_map` が無い(=カスタム modeling コードを持ち込まない)場合、素の Transformers 実装で読み込める「標準モデル」と判定できる。本モデルはその条件を満たす。

| 項目 | 値 | 根拠 |
|--|--|--|
| `architectures` | `["Qwen3ForCausalLM"]` | config.json |
| `model_type` | `qwen3` | config.json |
| キー prefix の系統 | `model.embed_tokens` / `model.layers.{i}.self_attn.{q,k,v,o}_proj` / `model.layers.{i}.mlp.{gate,up,down}_proj` / `model.norm` — LLaMA 系命名 | safetensors キー |
| `auto_map` (custom code) | なし | config.json |

## 3. 全体構造

モデルの「骨格」を決める 6 軸(層数、隠れ次元、語彙、最終正規化、重み共有)を整理する。decoder-only Transformer では `num_hidden_layers × hidden_size` がおおよその表現容量を決め、`vocab_size × hidden_size` が埋め込み層の重さを決める。本モデルは 28 層 × 1024 次元 × 152k 語彙で、**埋め込み単体で 155.6M(全体の約 26%)を占める**点に注意(0.6B 級モデルは語彙が相対的に重くなりがち)。tied embeddings によって `lm_head` 側は重みを持たず、入力埋め込みの転置を再利用する。

| 項目 | 値 | 根拠 |
|--|--|--|
| 構成 | decoder-only Transformer | `model.layers.*` のみ、cross-attn なし |
| `num_hidden_layers` | 28 | `layers.{i}` の最大 index 27 + 1(config.json と一致) |
| `hidden_size` | 1024 | `model.embed_tokens.weight.shape = (151936, 1024)` |
| `vocab_size` | 151,936 | 同上(config.json と一致) |
| 最終正規化 | RMSNorm, shape `(1024,)` | `model.norm.weight` |
| `tie_word_embeddings` | True | `lm_head.weight` 不在 + `config.tie_word_embeddings=true` |

## 4. Attention サブレイヤー

Attention は自己注意 (self-attention) の内部構造を決めるブロックで、**`q_proj` と `k_proj` の出力次元の比率**から MHA / MQA / GQA の種別を判定できる。本モデルは `q_proj → 2048`、`k_proj → 1024` で比 2:1、`head_dim=128` で割ると 16 クエリヘッド:8 KV ヘッドの **GQA(group size 2)**。Qwen3 固有のシグネチャは以下の 2 点:

1. **QK-Norm**: Q/K を内積前に per-head で RMSNorm する追加正規化。attention logits のスケール安定化に寄与し、Qwen3 / OLMo-2 系で採用された比較的新しい手法。
2. **`head_dim=128` と `hidden_size=1024` の不一致**: 通常は `hidden_size / num_heads = head_dim` だが、本モデルは `16 × 128 = 2048` と hidden の 2 倍を attention 空間に確保している。`o_proj (1024, 2048)` で最後に hidden に戻す。0.6B という小ささに対して attention 表現力を厚めに持たせる設計判断。

| 項目 | 値 | 根拠 |
|--|--|--|
| Attention 種別 | **GQA(16:8, group size 2)** | `q_proj` 出力 2048 / `head_dim` 128 = 16 ヘッド、`k_proj` 出力 1024 / 128 = 8 KV ヘッド |
| `num_attention_heads` | 16 | `q_proj.weight.shape = (2048, 1024)` |
| `num_key_value_heads` | 8 | `k_proj.weight.shape = (1024, 1024)` |
| `head_dim` | 128 | config.json `head_dim=128`(`hidden_size/H = 1024/16 = 64` とは不一致、**config 側の 128 が正**) |
| QK-Norm | **あり** | `self_attn.q_norm.weight (128,)`, `self_attn.k_norm.weight (128,)` を全 28 層で検出 |
| バイアス項 | なし | `*_proj.bias` キー 0 件、`attention_bias=false` |
| MLA パラメータ | 該当なし | `kv_a_proj_with_mqa` 等のキーなし |
| 出力射影 `o_proj` | `(1024, 2048)` | `o_proj.weight` |

## 5. 位置埋め込み

Transformer は系列順序に不変のため、位置情報を何らかの形で注入する必要がある。現代 LLM は **RoPE(Rotary Position Embedding)** が主流で、Q/K のペアを周波数ごとに回転させることで位置依存性を表現する。学習可能パラメータを持たないため safetensors には位置関連のキーは現れず、**`rope_theta`(周波数の基底)と `max_position_embeddings`(最大学習長)**で挙動が決まる。

本モデルは `rope_theta=1,000,000` と大きめの基底を採用(LLaMA-2 の 10,000、LLaMA-3 の 500,000 より更に大きい)し、これにより長距離の位置解像度を確保して **32k context を scaling(YaRN 等)なしで素に学習**している。Sliding window は無効で、全トークン間 full attention。

| 項目 | 値 | 根拠 |
|--|--|--|
| 位置埋め込み方式 | RoPE(学習パラメータなし、オンザフライ計算) | 学習済み位置埋め込みキーなし |
| `rope_theta` | 1,000,000 | config.json |
| `rope_scaling` | `null`(なし) | config.json |
| `partial_rotary_factor` | 未設定(= 1.0、全次元に回転を適用) | config.json にキーなし |
| `max_position_embeddings` | 32,768 | config.json |
| Sliding Window | 無効(`sliding_window=null`, `use_sliding_window=false`) | config.json |

## 6. MLP / FFN サブレイヤー

Attention と並ぶもう一方のサブレイヤー。**Gated Linear Unit 系**(SwiGLU / GeGLU)は `gate_proj` + `up_proj` + `down_proj` の 3 行列で `down(silu(gate(x)) * up(x))` を計算する形式で、LLaMA 以降の事実上の標準。拡張比 `intermediate_size / hidden_size` は表現力とパラメータ量のトレードオフを決める。

本モデルは拡張比 **3.0**(LLaMA の約 2.69、Qwen2.5 の 2.75 よりやや大きい)。MoE ではなく全層 dense で、`experts.*` や `gate.weight`、`shared_experts.*` といった MoE 特有のキーは存在しない。

| 項目 | 値 | 根拠 |
|--|--|--|
| MLP タイプ | **SwiGLU**(3 線形) | `mlp.gate_proj` + `mlp.up_proj` + `mlp.down_proj` |
| `hidden_act` | `silu` | config.json |
| `intermediate_size` | 3072(拡張比 `I/D = 3.0`) | `gate_proj.weight.shape = (3072, 1024)` |
| MoE | なし | `experts.*` / `gate.weight` / `shared_experts.*` いずれも不在 |
| `num_experts` | 該当なし | — |
| `num_experts_per_tok` | 該当なし | — |
| `moe_intermediate_size` | 該当なし | — |
| Shared experts | 該当なし | — |
| Dense/MoE 混在 | 全層 dense | — |

## 7. 正規化層

正規化層の種別は **norm 系キーに `.bias` があるか否か**で判別する。`.weight` のみ → RMSNorm、`.weight` + `.bias` → LayerNorm。LLaMA 以降は計算量・安定性の観点で RMSNorm が主流。配置は **Pre-Norm**(sublayer の入力側で正規化)が現代 LLM のデフォルトで、学習安定性が Post-Norm より高い。

本モデルは各 Transformer block に通常の 2 枚(`input_layernorm`, `post_attention_layernorm`)に加えて **QK-Norm の 2 枚(`q_norm`, `k_norm`)** が入るため、1 層あたり計 4 枚の正規化を持つ。

| 項目 | 値 | 根拠 |
|--|--|--|
| 正規化タイプ | RMSNorm | norm 系キーに `.bias` なし、`.weight` のみ |
| `rms_norm_eps` | 1e-6 | config.json |
| 層内正規化数 | 2 枚(`input_layernorm`, `post_attention_layernorm`) + QK-Norm 2 枚(`q_norm`, `k_norm`) | 各層 4 つの norm。Pre-Norm 構造 |
| 最終 norm | `model.norm.weight (1024,)` | 1 枚 |

## 8. 数値精度 / 量子化

安定版の BF16 で全重みが保存されている。BF16 は FP16 より指数部が広く(FP32 と同じ 8bit)学習で扱いやすい反面、仮数部が短いので推論時に FP16 と比べて微妙な丸め挙動が出ることがある。`qweight` / `scales` / `qzeros` / `g_idx` といった量子化特有のキーも `quantization_config` もないため、これは **「元のベースモデル(未量子化)」** と判定できる。GPTQ / AWQ / INT4 等の派生を使いたい場合は別途量子化バリアントを探す必要がある。

| 項目 | 値 | 根拠 |
|--|--|--|
| dtype 分布 | **全テンソル BF16**(596,049,920 要素すべて) | safetensors inspect、`torch_dtype="bfloat16"` |
| 量子化スキーム | 未量子化 | `qweight` / `scales` / `qzeros` / `g_idx` キーなし、`quantization_config` なし |
| 混合精度 | なし | 単一 dtype |

## 9. パラメータ数 / メモリ

パラメータ数の内訳は「**どこに重みが偏っているか**」を理解するのに重要。本モデルでは MLP が約 44.3%、Attention が約 29.6%、埋め込みが約 26.1% を占める。0.6B 級として埋め込みの比率が高い(語彙 152k のため)のが特徴で、**埋め込み / LM ヘッドの tied 化によって実質 155M 分を節約**している(untied なら総パラメータは +26% 増える)。

実ファイルサイズ(1.1103 GiB)は `パラメータ数 × 2 bytes` の理論値とほぼ一致し、差分 35 KB は safetensors ヘッダ分で納得のいく値。KV キャッシュは長文脈推論時のメモリ支配要因で、32k 全長で約 917 MiB、一般的な 1k 程度なら約 29 MiB。

| 部位 | パラメータ数 | 計算根拠 |
|--|--|--|
| 埋め込み | 155,582,464 | V × D = 151,936 × 1,024 |
| Attention(全層) | 176,167,936 | per-layer 6,291,712 × 28 層<br>per-layer = q(2048·1024) + k(1024·1024) + v(1024·1024) + o(1024·2048) + q_norm(128) + k_norm(128) |
| MLP / FFN(全層) | 264,241,152 | per-layer 9,437,184 × 28 層<br>per-layer = 3 × (3072·1024) |
| 正規化 | 58,368 | 28 × (input_layernorm 1024 + post_attn_layernorm 1024) + 最終 norm 1024 |
| 出力ヘッド | 0(tied) | `lm_head.weight` 不在 → 埋め込みと共有 |
| **合計** | **596,049,920** | 全テンソル numel の合計 |
| 理論ファイルサイズ(BF16) | 1,192,099,840 bytes(≒ 1.1103 GiB) | 596,049,920 × 2 |
| 実ファイルサイズ | 1,192,135,096 bytes(≒ 1.1103 GiB) | 実測 |
| 整合性 | 一致(差分 35,256 bytes ≒ 0.003%、safetensors ヘッダ分) | — |
| KV キャッシュ(seq=32,768) | 約 917 MiB | `2 × 28 × 8 × 128 × 32768 × 2 bytes` |
| KV キャッシュ(seq=1,024) | 約 28.6 MiB | `2 × 28 × 8 × 128 × 1,024 × 2 bytes` |

## 10. タスクヘッド / アダプタ

`Qwen3ForCausalLM` は単純な因果言語モデルで、分類ヘッドや QA ヘッド、プーリング層は持たない。LoRA 等のアダプタもマージされていない(`lora_A` / `lora_B` / `adapter.*` が無い)ため、**素のベースモデル**である。`lm_head` は tied embeddings により `embed_tokens.weight` を転置して使うので、独立した重みは持たない。

| 項目 | 値 | 根拠 |
|--|--|--|
| ヘッド種別 | `lm_head`(tied weight、実体は `embed_tokens.weight` を転置利用) | `Qwen3ForCausalLM` + `lm_head.weight` 不在 |
| プーリング(埋め込みモデル) | 該当なし(生成モデル) | — |
| LoRA / アダプタ | なし | `lora_A` / `lora_B` / `adapter.*` キーなし |

## 11. マルチモーダル構成(該当時のみ)

視覚(`vision_*`, `vision_tower`, `patch_embed`)、音声(`audio_*`)、プロジェクタ(`mm_projector.*`)のいずれのキーも存在せず、本モデルは **テキスト専用** の単一モダリティ。Qwen3 系には VL 版(Qwen3-VL)もあるが、本リポジトリには含まれない。

| 項目 | 値 | 根拠 |
|--|--|--|
| サブネット | 該当なし(テキスト単一モダリティ) | `vision_*` / `audio_*` / `mm_projector.*` キーなし |
| ビジョンエンコーダ | 該当なし | — |
| 接続層 | 該当なし | — |
| 投影次元 | 該当なし | — |

## 12. 所見

本モデルが **Qwen3 dense 系列の最小構成** であることは、以下の 3 つの証拠の合致から確定的に言える。(a) `Qwen3ForCausalLM` クラス名と `model_type=qwen3`、(b) LLaMA 互換の重みキー命名、(c) Qwen3 特有の QK-Norm の存在。これらを踏まえた本モデルの設計的特徴と周辺との関係は以下の通り。

- **GQA 比 2:1**: LLaMA-3 8B(4:1)より保守的で、KV キャッシュを抑えすぎず表現力を確保する小型モデル向けバランス。
- **`head_dim=128` を保ちつつ `hidden_size=1024`**: `H*head_dim=2048` と hidden の 2 倍を attention 空間に割く構成で、0.6B 級としては attention に厚めに寄せた設計。Qwen3 シリーズで共通して見られるパターン。
- **MLP 拡張比 3.0**: LLaMA 系の 2.6875 や Qwen2.5 の 2.75 より若干大きく、FFN 厚めで総パラメータの約 44% を MLP が占める。
- **RoPE base 1e6 + 32k context**: RoPE scaling なしで 32k を素でサポート。長文処理を base 学習段階で担保している。
- **未確認/未取得の項目**: なし。単一シャードで全重みが取得済み、config と完全整合。`tokenizer.json` は未取得だが `vocab_size=151,936` は埋め込み shape から確認済み。
