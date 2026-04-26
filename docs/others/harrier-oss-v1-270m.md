# harrier-oss-v1-270m アーキテクチャ解析レポート

**Hugging Face リポジトリ**: microsoft/harrier-oss-v1-270m
**URL**: https://huggingface.co/microsoft/harrier-oss-v1-270m
**解析対象シャード**: model.safetensors (単一ファイル)
**参照論文**: 論文未公開 — Microsoft Bing チームによるブログ記事 (2026-04-07) および Gemma 3 Technical Report (arXiv:2503.19786) を参照
**解析日**: 2026-04-17

## サマリ
- **アーキテクチャ系統**: Gemma 3 系 decoder-only Transformer（テキスト埋め込み特化、`Gemma3TextModel`）
- **総パラメータ数**: 268,098,176（約 270M）— 埋め込み層が全体の 62.6% を占める
- **特徴的な要素**: GQA (4:1), GeGLU MLP, QK-Norm, サンドイッチ正規化 (4 norms/layer), RoPE (θ=1M), last-token pooling + L2 正規化, 262K 語彙, 知識蒸留によるコンパクトモデル

## 1. メタ情報 / ファイル

本モデルは単一の safetensors ファイルに全重みが格納されており、シャード分割は行われていない。BF16 で約 0.499 GB と非常にコンパクトで、理論ファイルサイズ（268M × 2 bytes = 0.499 GB）と完全に一致する。metadata には PyTorch フォーマットを示す `format: pt` のみが記録されている。

| 項目 | 値 | 備考 |
|--|--|--|
| safetensors metadata | `{"format": "pt"}` | PyTorch フォーマット |
| シャード構成 | 単一ファイル, 0.499 GB | index.json なし |
| ダウンロード済みシャード | `model.safetensors` (0.499 GB) | 全テンソル解析済み |
| 付随ファイル | config.json, tokenizer.json, tokenizer_config.json, config_sentence_transformers.json, modules.json, mteb_v2_eval_prompts.json | sentence-transformers 互換構成 |

## 2. モデル識別

Gemma 3 のテキストモデル部分（`Gemma3TextModel`）をベースに、Microsoft が対照学習 + 知識蒸留で埋め込みモデルとして訓練したものである。E5 シリーズ (E5, Multilingual E5, E5-Mistral, GritLM) の後継にあたり、GPT-5 を用いた大規模合成データ生成と LLM リランカーによるフィルタリングが特徴。`auto_map` やカスタムモデリングコードは使用されておらず、標準の transformers ライブラリで直接ロード可能。

| 項目 | 値 | 根拠 |
|--|--|--|
| `architectures` | `["Gemma3TextModel"]` | config.json |
| `model_type` | `gemma3_text` | config.json |
| キー prefix の系統 | `layers.*.self_attn.q_proj` / `layers.*.mlp.gate_proj` → Gemma/LLaMA 系 | safetensors キー |
| `auto_map` (custom code) | なし | config.json |

## 3. 全体構造

18 層の decoder-only Transformer で、`hidden_size=640` と小さく抑えられている。Gemma 3 1B モデル（26 層, hidden_size=1152）と比較すると大幅に縮小されており、270m バリアントとして独自設計されたものと推察される。`lm_head.weight` は存在せず、言語モデリングヘッドを持たない純粋な特徴抽出モデルである。vocab_size=262,144 の巨大な埋め込み層がパラメータの 62.6% を占める点が本モデル最大の構造的特徴であり、小型モデルながら Gemma 3 の 262K 語彙（100 言語超対応）をそのまま維持している。

| 項目 | 値 | 根拠 |
|--|--|--|
| 構成 | decoder-only | キー prefix (`layers.*`) |
| `num_hidden_layers` | 18 | `layers.{0-17}.*` の最大インデックス + 1 |
| `hidden_size` | 640 | `embed_tokens.weight.shape[1]` = 640 |
| `vocab_size` | 262,144 | `embed_tokens.weight.shape[0]` = 262144 |
| 最終正規化 | RMSNorm, shape (640,) | `norm.weight` — bias なし |
| `tie_word_embeddings` | 該当なし（lm_head 不在） | `lm_head.weight` キーが存在しない — 埋め込みモデルのため言語モデリングヘッド自体が不要 |

## 4. Attention サブレイヤー

GQA を採用し、Q ヘッド数 4 に対して KV ヘッド数 1 の 4:1 比率である。これは Gemma 3 の特徴的な設計で、KV キャッシュメモリを大幅に削減する。`head_dim=256` は hidden_size=640 に対して大きく、Gemma 3 Technical Report で述べられた設計方針を踏襲している。QK-Norm（`q_norm.weight`, `k_norm.weight`）が全層に存在し、Gemma 2 で使用されていた logit soft-capping を置き換えたものである（Gemma 3 論文 Section 2.1）。`query_pre_attn_scalar=256`（= head_dim）によるスケーリングも Gemma 3 固有の設定である。

| 項目 | 値 | 根拠 |
|--|--|--|
| Attention 種別 | GQA (4:1) | `q_proj.shape[0]`=1024 / head_dim=256 = 4 heads, `k_proj.shape[0]`=256 / 256 = 1 head |
| `num_attention_heads` | 4 | config.json, `q_proj.weight` shape (1024, 640) |
| `num_key_value_heads` | 1 | config.json, `k_proj.weight` shape (256, 640) |
| `head_dim` | 256 | config.json `head_dim=256` |
| QK-Norm | あり | `layers.*.self_attn.q_norm.weight` (256,), `k_norm.weight` (256,) 全 18 層に存在 |
| バイアス項 | なし | `attention_bias=false`, `*_proj.bias` キー不在 |
| MLA パラメータ | 該当なし | MLA 関連キー不在 |
| 出力射影 `o_proj` | shape (640, 1024) | `layers.*.self_attn.o_proj.weight` |
| `query_pre_attn_scalar` | 256 | config.json — attention score を `√256` でスケーリング |
| `attn_logit_softcapping` | null（無効） | config.json — QK-Norm で代替 |

## 5. 位置埋め込み

RoPE を使用し、base frequency `θ=1,000,000` は Gemma 3 のグローバル attention 層の設定と同じである。Gemma 3 論文では、長コンテキスト対応のためにグローバル層の RoPE θ を従来の 10K から 1M に引き上げた旨が述べられている。config.json 上に `sliding_window=512` と `rope_local_base_freq=10000.0` のパラメータが存在するが、`layer_types` は全 18 層が `"full_attention"` であり、実際にはスライディングウィンドウ attention は使用されていない。これは埋め込みモデルとして last-token pooling で全コンテキストにアクセスする必要があるため、意図的に全層をグローバル attention にしたものと推測される。

| 項目 | 値 | 根拠 |
|--|--|--|
| 位置埋め込み方式 | RoPE | Gemma 3 系標準, config.json `rope_theta` |
| `rope_theta` | 1,000,000.0 | config.json |
| `rope_scaling` | null（なし） | config.json |
| `rope_local_base_freq` | 10,000.0 | config.json — ローカル attention 層用だが layer_types が全て full_attention のため未使用 |
| `partial_rotary_factor` | 未設定 | config.json に記載なし — 全次元に RoPE 適用と推定 |
| `max_position_embeddings` | 32,768 | config.json |
| Sliding Window | `sliding_window=512`, `sliding_window_pattern=1` だが `layer_types` が全て `"full_attention"` のため**実質無効** | config.json + layer_types |

## 6. MLP / FFN サブレイヤー

GeGLU（`gelu_pytorch_tanh` + gate 機構）を採用し、`gate_proj` + `up_proj` + `down_proj` の 3 層構成である。拡張比は 2048/640 = 3.2 で、一般的な SwiGLU/GeGLU モデルの 8/3 ≈ 2.67 よりやや大きい。Gemma 3 は活性化関数に GELU（tanh 近似）を使用しており、LLaMA 系の SiLU (SwiGLU) とは異なる点が特徴。MoE は採用されておらず、全層が dense MLP である。

| 項目 | 値 | 根拠 |
|--|--|--|
| MLP タイプ | GeGLU（gate + up + down の 3 層構成） | `gate_proj` + `up_proj` + `down_proj` キー存在 |
| `hidden_act` | `gelu_pytorch_tanh` | config.json |
| `intermediate_size` | 2,048 (拡張比 2048/640 = 3.2) | `gate_proj.weight.shape[0]` = 2048 |
| MoE | なし | `experts.*` キー不在 |
| `num_experts` | 該当なし | — |
| `num_experts_per_tok` | 該当なし | — |
| `moe_intermediate_size` | 該当なし | — |
| Shared experts | なし | — |
| Dense/MoE 混在 | 全層 dense | `layer_types` が全て `"full_attention"` |

## 7. 正規化層

Gemma 3 論文で説明されている「サンドイッチ正規化」（pre-norm + post-norm の 4 枚構成）を採用している。通常の Pre-Norm Transformer では attention 前と MLP 前の 2 枚だが、本モデルは attention 後（`post_attention_layernorm`）と MLP 後（`post_feedforward_layernorm`）にも正規化を追加している。この設計は Gemma 2 から継承されたもので、学習の安定性向上に寄与する。`rms_norm_eps=1e-06` は一般的な `1e-05`〜`1e-06` の範囲内。

| 項目 | 値 | 根拠 |
|--|--|--|
| 正規化タイプ | RMSNorm | norm キーに `.bias` なし、config.json `rms_norm_eps` 存在 |
| `rms_norm_eps` | 1e-06 | config.json |
| 層内正規化数 | 4 枚/層: `input_layernorm` + `post_attention_layernorm` + `pre_feedforward_layernorm` + `post_feedforward_layernorm` | safetensors キー一覧 — サンドイッチ正規化 |

## 8. 数値精度 / 量子化

全テンソルが BF16 で統一されており、混合精度や量子化は一切適用されていない。0.499 GB という軽量さから、量子化なしでも CPU やエッジデバイスでの推論が十分に現実的なサイズである。Microsoft のブログでは「低性能デバイスへのデプロイ」を想定した小型バリアントとして位置づけられている。

| 項目 | 値 | 根拠 |
|--|--|--|
| dtype 分布 | 全 236 テンソルが BF16 | safetensors inspect 結果 |
| 量子化スキーム | 未量子化 | `qweight`/`scales`/`qzeros` キー不在, `quantization_config` なし |
| 混合精度 | なし — 全テンソル BF16 統一 | dtype 集計 |

## 9. パラメータ数 / メモリ

埋め込み層が全体の 62.6% を占める構造は、262K という巨大語彙と hidden_size=640 の小さいモデル次元の組み合わせに起因する。Transformer 層自体は約 100M パラメータと軽量である。MLP がパラメータの 26.4% を、Attention が 11.0% を占める。KV キャッシュは GQA 4:1 の恩恵で、seq=32K でも約 0.56 GB に抑えられる。

| 部位 | パラメータ数 | 計算根拠 |
|--|--|--|
| 埋め込み (`embed_tokens`) | 167,772,160 (62.6%) | 262,144 × 640 |
| Attention (全 18 層) | 29,500,416 (11.0%) | (655,360 + 163,840 + 163,840 + 655,360 + 256 + 256) × 18 = 1,638,912 × 18 |
| MLP / FFN (全 18 層) | 70,778,880 (26.4%) | (1,310,720 × 3) × 18 = 3,932,160 × 18 |
| 正規化 (全 18 層 + final) | 46,720 (0.02%) | (640 × 4) × 18 + 640 |
| 出力ヘッド | 0 | 埋め込みモデルのため `lm_head` なし |
| **合計** | **268,098,176** | 全テンソル numel の合計 |
| 理論ファイルサイズ (BF16) | 0.499 GB | 268,098,176 × 2 bytes |
| 実ファイルサイズ | 0.499 GB | 実測値 |
| 整合性 | 完全一致 | 量子化なし、BF16 統一 |
| KV キャッシュ (seq=32,768) | 約 0.56 GB | 2 × 18 × 1 × 256 × 32,768 × 2 bytes = 603,979,776 bytes |

## 10. タスクヘッド / アダプタ

言語モデリングヘッド (`lm_head`) を持たない純粋な特徴抽出モデルである。sentence-transformers ライブラリと統合されており、last-token pooling + L2 正規化で固定長 640 次元のテキスト埋め込みを生成する。タスク指示（"Instruct: ... \nQuery: ..."）をクエリ側に付与する instruction-following 型の埋め込みモデルであり、E5-Mistral の設計を継承している。

| 項目 | 値 | 根拠 |
|--|--|--|
| ヘッド種別 | なし（`lm_head` 不在）— 特徴抽出専用 | safetensors キー一覧 |
| プーリング | last-token pooling + L2 正規化 | Model Card, config_sentence_transformers.json |
| 埋め込み次元 | 640 | `hidden_size` = 640 |
| LoRA / アダプタ | なし | `lora_A`, `lora_B`, `adapter.*` キー不在 |

## 11. マルチモーダル構成

テキスト単独のユニモーダルモデルである。`vision_model.*`, `vision_tower.*`, `audio_*`, `mm_projector.*` 等のマルチモーダル関連キーは完全に不在。Gemma 3 の 4B/12B/27B モデルは SigLIP ビジョンエンコーダを搭載しているが、1B 以下のバリアントはテキスト専用であり、本モデルもその系統に属する。

| 項目 | 値 | 根拠 |
|--|--|--|
| サブネット | なし — テキスト単独 | マルチモーダル関連キー prefix 不在 |
| ビジョンエンコーダ | 該当なし | — |
| 接続層 | 該当なし | — |
| 投影次元 | 該当なし | — |

## 12. 所見

**アーキテクチャ系統の特定根拠**: キー命名規則 (`layers.*.self_attn.q_proj`, `layers.*.mlp.gate_proj`)、config.json の `model_type: gemma3_text` / `architectures: ["Gemma3TextModel"]`、および 4 枚のサンドイッチ正規化・QK-Norm・GeGLU の組み合わせから、Gemma 3 テキストモデルのバックボーンであることが確実である。ただし Gemma 3 公式の 1B モデル（26 層, hidden_size=1152）とは異なるハイパーパラメータ構成（18 層, hidden_size=640）であり、Microsoft が独自にアーキテクチャ規模を調整して事前学習または蒸留したものと推定される。

**同世代モデルとの比較で目立つ点**:
- **語彙支配型のパラメータ配分**: 262K 語彙 × 640 次元 = 167M パラメータが埋め込み層に集中（全体の 62.6%）。同規模の埋め込みモデル（例: Embeddinggemma-270m）と同等の語彙サイズだが、hidden_size が小さいため相対比率が極めて高い。
- **全層グローバル attention**: Gemma 3 本来の 5:1 ローカル/グローバル interleaving を廃し、全 18 層をフル attention にしている。これは last-token pooling で入力全体の情報を最終トークンに集約する必要がある埋め込みモデルとして合理的な変更。
- **MTEB v2 でのコストパフォーマンス**: 0.499 GB (BF16) で MTEB v2 スコア 66.5 を達成し、OpenAI text-embedding-3-large (58.92) や Amazon Titan Embed v2 (60.37) を大幅に上回る。Microsoft ブログによれば、20 億超の弱教師付きデータと 1000 万超の高品質データによる大規模訓練、および 27B モデルからの知識蒸留がこの性能の源泉である。
- **head_dim=256 の特異性**: hidden_size=640 に対して head_dim=256 は異例に大きく、`o_proj` の入力次元（= num_heads × head_dim = 4 × 256 = 1024）が hidden_size (640) を超える。これは Gemma 3 アーキテクチャ固有の設計で、attention の表現力を確保するための選択と考えられる。

**解析時に未確認だった項目**:
- Harrier の専用論文は 2026-04-17 時点で未公開。ブログ記事と Model Card の情報を基に記述した。
- `tokenizer_config.json` は 1.2MB 超と大きく、全容は未精査（SentencePiece 262K 語彙の定義を含む）。
- `config_sentence_transformers.json` および `modules.json` の詳細（プロンプトテンプレート等）は解析対象外とした。
- ベースモデル（蒸留前の教師モデル）が harrier-oss-v1-27b なのか、あるいは別の内部モデルなのかは明記されていない。
