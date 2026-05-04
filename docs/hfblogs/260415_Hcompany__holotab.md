# HoloTab by HCompany: AI ブラウザコンパニオン

## 発行元
- **発行組織**: HCompany
- **著者**: Marc Thibault (marc-thibault-h), Pierre-Louis Cedoz (plcedoz38), Hamza Benchekroun (hamza-hcompany), Kai Yuan (h-kaiy), Aurélien Lac (h-aurelien-lac), Tony Wu (h-tonywu), Antonio Loison (antonioloison), Axel Moyal (axmoy), Emrick Sinitambirivoutin (emricksini-h), Aleix Cambray (h-aleixcambray) ほか 17 名
- **発行日**: 2026-04-15
- **URL**: https://huggingface.co/blog/Hcompany/holotab

## 一言概要
HCompany の最先端コンピュータ操作モデル Holo3-35B-A3B を Chrome 拡張機能として無料提供し、「一度見せれば何度でも実行できる」Routines 機能でブラウザ作業を自動化するにゃ。

## ブログで説明している内容

- **HoloTab の位置づけ**
  - Chrome 拡張機能として提供される AI ブラウザコンパニオン
  - 無料アクセス可能、技術スキル不要
  - Chrome Web Store 直リンク: https://chromewebstore.google.com/detail/holotab/hlaoiikljjgcjdhkakedfngifaopbcop
- **基盤モデル: Holo3-35B-A3B**
  - 発表日: 2026 年 3 月 31 日
  - 35B パラメータの最先端コンピュータ使用 AI
  - Image-Text-to-Text タイプ
  - ダウンロード数 48.2k、引用 313
- **Routines 機能**
  - コンセプト: "一度見せれば、何度でも実行できる"
  - フロー: ユーザーが操作を記録 → HoloTab がスクリーン+操作をリアルタイム捕捉 → 音声ナレーションと視覚情報からコンテキスト理解 → ルーチン自動生成 → 再実行/スケジューリング
  - ユースケース 1: 20 以上の e コマースサイトで競合価格を交差参照しスプレッドシートを更新
  - ユースケース 2: 複数の求人サイトから候補リストを収集し追跡ドキュメントに統合
- **内部処理**
  - ビジョンモデルによる画面内容の理解
  - アクション計画
  - インターフェース理解 (UI 解釈)
  - フォーム入力やナビゲーションを人間と同様に実行
- **アクセシビリティ戦略**
  - 無料提供
  - ノーコード化
  - 技術チームがいない組織への民主化
- **HCompany 関連リリース**
  - Holo3: Breaking the Computer Use Frontier (2026-04-01)
  - Holotron-12B - High Throughput Computer Use Agent (2026-03-17)
- **記事に含まれていない情報**
  - ベンチマーク数値、技術仕様書、デモビデオ、API ドキュメント、セキュリティ/プライバシー詳細などは未記載

## 注目ポイントの解説

HoloTab の本質は「コンピュータ操作 AI を一般ユーザーが触れる形で配布する」というディストリビューション戦略にゃ。Holo3-35B-A3B 自体はクラウド API として動かすことも可能なはずだけど、あえて Chrome 拡張機能として無料化することで、技術チームを持たない組織や個人にもブラウザ作業自動化を広げようとしている。これはモデル提供企業にとって「自社モデルの実用性をユーザー体験で証明する」マーケティング手段でもあるにゃん。

Routines 機能のデモンストレーション・バイ・エグザンプル方式 (記録すれば学習する) も興味深いにゃ。従来の RPA はスクリプトを書くか、要素セレクタを指定するかが必要だったが、ビジョンモデルが画面と音声ナレーションから意図を読み取って自動的にルーチン化するアプローチは、非エンジニアの作業自動化体験を一段ジャンプさせる可能性があるにゃん。e コマース価格交差参照や採用候補リスト集約のような「人間がブラウザを使ってやっている繰り返し作業」が直接ターゲットになるにゃん。

ただし、ベンチマーク数値や技術仕様、セキュリティ説明が記事に含まれていない点は注意が必要にゃ。実運用では「どこで処理が走るか」「資格情報をどう扱うか」「ハルシネーションが起きたときの安全策は何か」が決定的に重要になる。配布優先のアナウンス記事という性格を踏まえつつ、本格採用検討時には技術ドキュメントや Holo3 論文 ("Holo3: Breaking the Computer Use Frontier") を併読する必要があるにゃん。
