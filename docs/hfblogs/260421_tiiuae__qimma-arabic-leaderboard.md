# QIMMA قِمّة: 品質を最優先したアラビア語 LLM リーダーボード

## 発行元
- **発行組織**: Technology Innovation Institute (TIIUAE)
- **著者**: Leen AlQadi, Ahmed Alzubaidi, Mohammed Alyafeai, Hamza Alobeidli, Maitha Alhammadi, Shaikha Alsuwaidi, Omar Alkaabi, Basma El Amel Boussaha, Hakim Hacid ほか複数名
- **発行日**: 2026-04-21
- **URL**: https://huggingface.co/blog/tiiuae/qimma-arabic-leaderboard

## 一言概要
52,000 サンプル / 14 ベンチマーク / 109 サブセットを 2 段階品質検証 (LLM 多モデル評価 + ネイティブ話者審査) にかけ、99% ネイティブアラビア語かつコード評価を含む初の品質第一アラビア語 LLM リーダーボードにゃ。

## ブログで説明している内容

- **問題意識**
  - 既存アラビア語ベンチマークは翻訳起因の分布シフト、注釈不一致、エンコーディングエラー、文化的バイアスを抱える
  - 評価スクリプトやサンプル出力の公開不足で再現性に欠陥
  - OALL v1/v2、BALSAM、AraGen、SILMA ABL、ILMAAM、HELM Arabic と比較して QIMMA だけがオープンソース・99% ネイティブ・体系的品質検証・コード評価・サンプルレベル推論公開を全て満たす
- **データセット規模**
  - 52,000 以上のサンプル / 14 ベンチマーク / 109 サブセット / 7 ドメイン
  - ドメイン: Cultural (AraDiCE-Culture, ArabCulture, PalmX), STEM (ArabicMMLU, GAT, 3LM STEM), Legal (ArabLegalQA, MizanQA), Medical (MedArabiQ, MedAraBench), Safety (AraTrust), Poetry & Literature (FannOrFlop), Coding (3LM HumanEval+, 3LM MBPP+)
- **品質検証パイプライン**
  - ステージ 1: Qwen3-235B-A22B-Instruct と DeepSeek-V3-671B による 10 点ルーブリック評価。両モデルいずれかが 7/10 未満なら除外
  - ステージ 2: ネイティブアラビア語話者による文化的・方言的・主観的解釈の検証
- **品質問題の発見数**
  - ArabicMMLU: 14,163 中 436 破棄 (3.1%)
  - MizanQA: 1,769 中 41 破棄 (2.3%)
  - PalmX: 3,001 中 25 破棄 (0.8%)
  - MedAraBench: 4,960 中 33 破棄 (0.7%)
  - FannOrFlop: 6,984 中 43 破棄 (0.6%)
  - 他もすべて記載
- **コードベンチマークの精錬**
  - 破棄ではなく問題文の精錬
  - 3LM HumanEval+: 164 中 145 修正 (88%)
  - 3LM MBPP+: 378 中 308 修正 (81%)
  - 修正カテゴリ: 言語的洗練 / 明確性改善 / 一貫性正規化 / 構造的修正 / 意味的改善
- **評価フレームワーク**
  - LightEval (メイン)、EvalPlus、FannOrFlop
  - メトリクス: MCQ は正規化対数尤度精度、生成型 QA は F1 BERTScore (AraBERT v02)、コードは Pass@1
  - プロンプトテンプレート 6 種 (MCQ, MCQ-C, MCQ-I, QA, QA-C, QA-F)、すべてアラビア語
- **リーダーボード結果 (トップ 10)**
  - 1 位: Qwen/Qwen3.5-397B-A17B-FP8 (68.06)
  - 2 位: Applied-Innovation-Center/Karnak (66.20)
  - 3 位: inceptionai/Jais-2-70B-Chat (65.81)
  - 4 位: Qwen/Qwen2.5-72B-Instruct (65.75)
  - 5 位: Applied-Innovation-Center/AIC-1 (65.37)
  - 6 位: Qwen/Qwen3.5-122B-A10B (64.84)
  - 7 位: Sakalti/Ultiima-72B (64.49)
  - 8 位: meta-llama/Llama-3.3-70B-Instruct (63.96)
  - 9 位: Qwen/Qwen2.5-32B-Instruct (63.26)
  - 10 位: FreedomIntelligence/AceGPT-v2-32B-Chat (61.14)
- **リソース**
  - リーダーボード: https://huggingface.co/spaces/qimma/leaderboard
  - GitHub: https://github.com/tiiuae/QIMMA-leaderboard.git
  - 論文: https://arxiv.org/pdf/2604.03395

## 注目ポイントの解説

QIMMA がほかのアラビア語リーダーボードと違うのは、評価実行の前に「ベンチマーク自体を疑う」という姿勢にゃ。ArabicMMLU で 3.1% (436 件) が破棄対象になったという数字は単なるノイズではなく、広く使われているベンチマークにも体系的な品質問題が残っていることを示している。これは「ベンチマークを使う側の責任」をはっきり提示している点で大きいにゃん。

コード問題文の修正率 88% / 81% という数字も衝撃的にゃ。HumanEval+ や MBPP+ のアラビア語版はそのままだと多くが曖昧・破損していて、リーダーボードに載せる前に大幅な前処理が必要だった。これは「アラビア語コード生成の能力評価」という分野そのものが成立するためにベンチマーク側の品質改善が前提条件であることを物語っているにゃん。

リーダーボード結果も興味深いにゃ。1 位の Qwen3.5-397B-A17B-FP8 がコーディングで圧倒的に強い一方、文化的・言語的タスクでは Jais-2-70B-Chat のようなアラビア語特化モデルが上回る。中規模特化モデルが大規模多言語モデルと競争できるという事実は、地域語向け LLM 開発戦略にとって重要な示唆を与えているにゃん。
