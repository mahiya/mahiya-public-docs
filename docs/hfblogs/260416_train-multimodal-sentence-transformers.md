# Sentence Transformers でマルチモーダル埋め込みモデルを訓練する

## 発行元
- **発行組織**: Hugging Face
- **著者**: Tom Aarsen (tomaarsen) ほか 60 名 (stefan-jo, kalyan-ks, ceyda, splevine, ahujachirag, pcuenq など)
- **発行日**: 2026-04-16
- **URL**: https://huggingface.co/blog/train-multimodal-sentence-transformers

## 一言概要
Qwen3-VL-Embedding-2B を Visual Document Retrieval で 1 エポック微調整するだけで NDCG@10 を 0.888 → 0.947 に押し上げ、4 倍大きいモデルすら上回るマルチモーダル埋め込み訓練の完全レシピにゃ。

## ブログで説明している内容

- **なぜ微調整が必要か**
  - 汎用マルチモーダル埋め込みモデルは特定ドメインに最適化されていない
  - VDR タスク例: 1 エポック微調整で NDCG@10 が 0.888 → 0.947
  - 4 倍大きい Qwen3-VL-Embedding-8B (0.923) も上回る
- **モデルロード**
  - `SentenceTransformer("Qwen/Qwen3-VL-Embedding-2B", model_kwargs={"attn_implementation": "flash_attention_2", "torch_dtype": "bfloat16"}, processor_kwargs={"min_pixels": 28*28, "max_pixels": 600*600})`
  - `model.modalities` で `['text', 'image', 'video', 'message']` を確認可能
  - VLM チェックポイントから直接ロードもできる (`Qwen/Qwen3-VL-2B`)
  - Router ベースで text/image エンコーダを別々に組む構成も可能 (`siglip2` + `MiniLM`)
- **データセット**
  - `tomaarsen/llamaindex-vdr-en-train-preprocessed` (53,512 英語サンプル)
  - 元データ `llamaindex/vdr-multilingual-train` (500k 多言語)
  - 構成: query (テキスト) / positive (画像) / negative_0..3 (画像)
  - 列名は label/score 以外順序で扱われる
  - サポート型: text, image, audio, video, multimodal 辞書
- **損失関数**
  - `CachedMultipleNegativesRankingLoss(model, mini_batch_size=1)` でグラデーントキャッシング
  - `MatryoshkaLoss` で `[2048, 1536, 1024, 512, 256, 128, 64]` 次元を同時最適化
- **訓練引数**
  - `per_device_train_batch_size=64`, `learning_rate=2e-5`, `warmup_ratio=0.1`
  - `bf16=True` (VLM では fp16 より bf16 推奨)
  - `batch_sampler=BatchSamplers.NO_DUPLICATES` でバッチ内ネガティブ確保
- **評価器**
  - `InformationRetrievalEvaluator` をクエリ/コーパス/関連ドキュメントで構築
  - 4 つのハードネガティブを ID オフセットでコーパスに追加
  - `truncate_dim` 指定で次元別評価
- **完全な訓練スクリプト**
  - データロード → 損失定義 → 評価器構築 → `SentenceTransformerTrainer.train()` → 各 Matryoshka 次元評価 → 保存 → Hub プッシュ
- **評価結果**
  - tomaarsen/Qwen3-VL-Embedding-2B-vdr (2.1B): 0.947
  - Qwen/Qwen3-VL-Embedding-8B (8.1B): 0.923
  - nvidia/omni-embed-nemotron-3b (4.7B): 0.915
  - nvidia/llama-nemotron-embed-vl-1b-v2 (1.7B): 0.912
  - nomic-ai/nomic-embed-multimodal-7b (8.3B): 0.912
  - llamaindex/vdr-2b-multi-v1 (2.2B): 0.912
  - Qwen/Qwen3-VL-Embedding-2B (基本, 2.1B): 0.888
- **Matryoshka 次元別性能 (微調整モデル)**
  - 2048: 0.9480 (100%)
  - 1536: 0.9439 (99.6%)
  - 1024: 0.9464 (99.8%)
  - 512: 0.9451 (99.7%)
  - 256: 0.9372 (98.9%)
  - 128: 0.9058 (95.5%)
  - 64: 0.8758 (92.4%)
- **マルチモーダル Reranker (CrossEncoder)**
  - Any-to-Any + LogitScore: `score = log(P("1")) - log(P("0"))`
  - 特徴抽出 + Pooling + Dense の 2 アーキテクチャを提示
  - chat_template に "query" と "document" ロールを追加
  - マルチデータセット (`image_to_text`, `text_to_image`) で訓練
- **メモリ効率化**
  - `mini_batch_size=1`, `flash_attention_2`, `bfloat16`, `min/max_pixels` 指定、評価時 `batch_size=1`

## 注目ポイントの解説

NDCG@10 が 0.888 → 0.947 という改善幅は、わずか 53,512 サンプル・1 エポックで達成できる規模感にゃ。しかも結果として 4 倍大きい同系列モデル (Qwen3-VL-Embedding-8B) を上回るので、「巨大モデルを使うかドメイン微調整するか」という戦略選択において、後者がコストパフォーマンス的に強いことを実証しているにゃん。

Matryoshka Loss と組み合わせる設計が秀逸にゃ。微調整モデルは 1024 次元でほぼピーク性能 (99.8%) を保ち、512 次元でも 99.7%、64 次元でさえ 92.4%。これはデプロイ時にストレージや検索コストを 4 倍 / 32 倍削減できるという意味で、実運用の VDR システムに直結する利点にゃん。`save_pretrained(..., truncate_dim=1024)` でデフォルトの埋め込み次元を変えられる点も、Hub 上での利便性を高めているにゃん。

最も実装的に重要なのは「マルチモーダル微調整がテキストのみ訓練とほぼ同じコードで書ける」という事実にゃ。違いは `model_kwargs` と `processor_kwargs` を渡すこと、`mini_batch_size=1` でグラデーントキャッシングを使うこと、評価時 `batch_size=1` にすること、それくらい。`SentenceTransformerTrainer` がマルチモーダル対応を自動処理するので、テキスト用の知識をそのまま転用できる設計は、コミュニティへの参入障壁を大きく下げているにゃん。
