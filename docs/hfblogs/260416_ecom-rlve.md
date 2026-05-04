# Ecom-RLVE: e コマース会話エージェント向けの適応的検証可能環境

## 発行元
- **発行組織**: Hugging Face (PyTorch OpenEnv Hackathon / Cerebral Valley)
- **著者**: Rahul Bajaj (thebajajra), Jaya Nupur (ai-queen), Anuj Garg (pmodan), Ben Burtenshaw (burtenshaw), Owlgebra AI ほか
- **発行日**: 2026-04-16
- **URL**: https://huggingface.co/blog/ecom-rlve

## 一言概要
RLVE フレームワークを単一ターン推論パズルから「マルチターン・ツール活用型 e コマース会話」に拡張し、8 環境 / 12 軸難易度カリキュラム / 検証可能な報酬を備えた EcomRLVE-GYM を提案するにゃ。

## ブログで説明している内容

- **背景**
  - LLM は流暢でもショッピングタスクの完遂は苦手 (制約フィルタリング、ツール呼び出し、製品 ID 幻覚回避が必要)
  - SFT は表面的なツール使用しか教えられない
  - 解決策: RLVR (Reinforcement Learning with Verifiable Rewards) + 適応難易度
- **EcomRLVE-GYM の 8 環境**
  - Product Discovery / Substitution / Cart Building (E_CART) / Return + Replacement / Order Tracking / Policy QA / Bundle Planning / Multi-Intent Journey
  - すべて検証可能な報酬関数つき
- **報酬設計**
  - `Total = r_task + r_eff - r_hall`
  - r_task: F1 や段階的スコア
  - r_eff: `1 - (agent_turns / max_budget)` (ユーザー起因ターンは除外)
  - r_hall: 推奨製品 ID がセッション中に検索されたかチェック
  - 不正 JSON や違法ツール呼び出しは即時失敗
- **12 軸の難易度カリキュラム**
  - 制約数 (d=0 で 2 → d=12 で 8)、制約省略率 (5% → ~80%)、検索結果ディストラクタ率 (0% → 24%)、在庫切れ率 (0% → 50%)
  - 他にターン予算、入力ノイズ、コンテキスト切替、検索深度、注文履歴サイズ、ポリシー複雑性、ツール予算など
  - 各環境ごとに成功率を独立追跡し、能力フロンティアでの学習を維持
- **Cart Building (E_CART) の詳細**
  - 必要スキル: Product Discovery / Variant Selection / Cart Management / Clarification Dialogue / Multi-Item Orders
  - ツール: `catalog_search`, `catalog_get_variants`, `cart_add`, `cart_view`, `user_get_visit_history`, `ask_user`
  - バリアント合成: カテゴリ別優先 (`connector_type`, `size`, `material`)、3 バリアント生成 (1 ターゲット + 2 ディストラクタ)
  - 複合キー検証: `(product_id, variant_id, qty)`
- **環境スケーリング C1 ⊂ C2 ⊂ C4 ⊂ C8**
  - C1: Cart のみ
  - C2: + Substitution
  - C4: + Product Discovery, Returns
  - C8: + Status, Policy, Bundle, Journey
- **実験設定**
  - ベースモデル: Qwen 3 8B
  - アルゴリズム: DAPO (G=8 rollouts/prompt)
  - 学習率: 1e-5、訓練ステップ: 300
  - カタログ: 2M products with FAISS index (`Alibaba-NLP/gte-modernbert-base`, 768-dim)
  - ユーザーシミュレータ: Qwen3.5 9.7B
- **データセット & コード**
  - データ: `owlgebra-ai/Amazebay-catalog-2M` (2.05M 製品)
  - GitHub: https://github.com/owlgebra-ai/EcomRLVE-Gym
  - モデル: `owlgebra-ai/wufus`
  - HF Spaces にライブデモ
- **早期結果**
  - C1 環境で 300 ステップ訓練、適応スケジューリングにより段階的な学習信号を確認

## 注目ポイントの解説

RLVE のアイデアを e コマース会話に持ち込んだ点が新規性のキモにゃ。並べ替えや数独のような単一ターン検証可能タスクとは違い、会話エージェントは複数ターン・ユーザーシミュレータとの動的やりとり・ツール呼び出しの組み合わせ爆発に直面する。それを「複合キー検証」「製品 ID の検索履歴チェック」「効率報酬」の組み合わせでアルゴリズム的に検証可能にした構成は、LLM Judge に頼らず再現性の高い RL 訓練を成立させているにゃん。

12 軸の難易度カリキュラムも実用的にゃ。実際の e コマースでは「ユーザーが制約を全部明示するか」「在庫切れがどれだけあるか」「ノイズの多い入力か」など多様な軸で難しさが変動する。これらを単一の難易度値 d に集約しつつ、各環境が独立に成功率を追跡してレベルを上げる設計は、エージェントが「飽和して退屈」「難しすぎて学習信号ゼロ」のどちらにも陥らないように工夫されているにゃん。

バリアント処理を明示的に教育課題として扱った点も注目にゃん。"Anker 65W USB-C 充電器" のような商品を `(product_id, variant_id)` 複合キーで検証することで、エージェントが「正しい製品を見つけたが間違ったバリアントを選んだ」というよくある失敗パターンを学習段階から扱える。実運用のショッピングエージェントに直結する課題設定で、ベンチマークというより実装のテンプレートに近い価値があるにゃん。
