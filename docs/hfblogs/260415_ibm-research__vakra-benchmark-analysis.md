# VAKRA の内側: エージェントの推論・ツール使用・失敗モード分析

## 発行元
- **発行組織**: IBM Research
- **著者**: Ankita Naik (ankita-naik), danish, Ben (Ben871), Anupama Murthi (anupamamurthi), Praveen (praveenv), Siyu (Syhcode) ほか 22 名
- **発行日**: 2026-04-15
- **URL**: https://huggingface.co/blog/ibm-research/vakra-benchmark-analysis

## 一言概要
8,000 以上のローカルホスト API と 62 ドメインを背景に、API 連鎖・ツール選択・マルチホップ推論・ポリシー遵守の 4 能力を実行トレースで評価する VAKRA ベンチマークの設計と結果を解説するにゃ。

## ブログで説明している内容

- **VAKRA の基本仕様**
  - 8,000+ ローカルホスト API、62 ドメイン、3-7 ステップ推論チェーン
  - 実 DB に支援、非構造化取得+自然言語ツール使用制約下で評価
- **4 つの Capability**
  - **Capability 1: API Chaining (BI API)** - 2,077 インスタンス / 54 ドメイン / 1-12 ツール呼び出し / SLOT-BIRD と SEL-BIRD
  - **Capability 2: Tool Selection (Dashboard API)** - 1,597 インスタンス / 17 ドメイン / 6-328 ツール (平均 116) / FastAPI 運用 / OpenAI 仕様の 128 ツール上限への Shortlisting
  - **Capability 3: Multi-Hop Reasoning** - 869 インスタンス / 38 ドメイン / 1-5 ホップ
  - **Capability 4: Multi-Hop, Multi-Source Reasoning & Policy** - 644 インスタンス / 41 ドメイン / API + Document Index / マルチターン対話 / Tool-use Policy
- **API Chaining の例**
  - サッカーチーム検索: `get_data` → `select_data_equal_to` を 3 連鎖 → `get_team_name` → "FC Barcelona"
  - ツールユニバース ID で初期化、SLOT-BIRD は 7 汎用ツール、SEL-BIRD は平均 4 GET 関数
- **Tool-use Policy の例**
  - "Technology & Software のクエリは document retrievers のみ使用、他ツールは使わない" のような制約をプロンプトで指定
- **評価メトリクス**
  - ウォーターフォール型: Policy Adherence (Cap 4 のみ) → Predicted Tool Call Sequence vs Ground Truth → Valid Trajectory のみ最終応答評価
  - ツール応答セット比較で代替パスを認容
  - プログラマティック検証 + LLM ベース評価 (CRAG)
- **スコアリング**
  - `Leaderboard_Score = (1/4) × Σ Capability_n`
  - `Capability_1-3 = correct/total`
  - `Capability_4 = (correct_multi-source × 2 + correct_API-only_or_RAG-only) / (total_multi-source × 2 + total_API-only_or_RAG-only)`
  - マルチソース質問は 2 倍重み付け
- **評価対象モデル**
  - GPT-OSS-120B (SEL-BIRD で最高)
  - Gemini-3-flash-preview (Dashboard APIs で最高)
  - Claude-Sonnet-4-5
  - Granite-4.0-h-Small-32B (ポリシー制約下分析)
- **結果ハイライト**
  - **Capability 1**: GPT-OSS-120B が大幅優位、SLOT-BIRD ではパラメータ名生成エラー、SEL-BIRD ではツール選択エラーが主要
  - **Capability 2**: Gemini-3-flash-preview が全エラーカテゴリで最高、ただしツール呼び出しが正しくても応答統合で失敗するケースあり
  - **Capability 3**: ホップ深度が増えるほど精度低下 (1-hop > 2-hop > 3+ hop)
  - **Capability 4**: 1-hop API > 2-hop API > 1-hop RAG (GPT-OSS-120B はパラメトリック知識で直接回答する傾向)、Hybrid (API-RAG) は一般に低いが Gemini-3-flash-preview の 2-hop API-RAG は例外的に強い
  - **ポリシー影響**: 答えを変えないポリシーは影響小、答えを変えるポリシーは Granite-4.0-h-Small-32B 以外で性能低下
- **リソース**
  - Dataset: https://huggingface.co/datasets/ibm-research/VAKRA
  - Leaderboard: https://ibm-research-vakra.hf.space/
  - GitHub: https://github.com/IBM/vakra
  - IBM Release: https://www.ibm.com/new/announcements/introducing-vakra-benchmark

## 注目ポイントの解説

VAKRA が他のエージェントベンチマークと違うのは、評価の粒度を「最終応答」だけでなく「実行トレース」にまで掘り下げたところにゃ。ウォーターフォール型のパイプラインで Policy Adherence → ツール呼び出し列 → 最終応答と段階的に検証することで、エージェントの失敗が「ツール選択ミス」「引数値ミス」「応答統合ミス」のどこで起きたかを切り分けられる。これはモデル開発者が改善の優先順位を決めるための診断情報として圧倒的に価値が高いにゃん。

ツール応答セット比較による「代替パス認容」も興味深い設計にゃ。厳密にステップマッチングを要求すると正しい解法でも複数あるはずの正解パスを誤りと判定してしまうが、VAKRA は「最終的に必要な情報を回収できたか」をプログラム的+LLM 的に二段階で確認することでこの問題を回避している。これにより、エージェントの多様な推論戦略を許容しつつ正しさは厳密に評価できるにゃん。

ポリシー制約下での分析もリアルで重要にゃん。"Tech 系のクエリは document retriever のみ使う" のような実運用ルールを与えると、Granite-4.0-h-Small-32B 以外のモデルは性能を落とす。これは多くのエージェントが「制約を理解する」より「使えるツールを全部試す」傾向があることを示唆していて、企業導入で頻発する「ポリシー違反」問題のベースラインを提供するベンチマークとしての役割をきちんと果たしているにゃん。
