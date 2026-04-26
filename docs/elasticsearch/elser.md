# ELSER (Elastic Learned Sparse EncodeR)

ELSER は Elastic 社が開発した、英語向けのスパースベクトルエンコーダです。

## 概要

- ドメイン非依存のセマンティック検索を、ファインチューニング不要で実現することを目的としたモデル
- BM25 と組み合わせることで、ハイブリッド検索（lexical + semantic）の精度向上に寄与
- Elasticsearch 8.8 以降で本番利用可能

## 特徴

- スパースベクトル形式のため、転置インデックスとの相性が良い
- 推論時にトークン重み（学習済み expansion terms）を出力
- Dense Retrieval と比較して、語彙的な手がかりも保持しやすい

## 利用方法

Elasticsearch の ML ノードに ELSER モデルをデプロイすることで、`text_expansion` クエリ経由で利用できる。

```json
POST _ml/trained_models/.elser_model_2/deployment/_start
```

詳細な手順や検証結果は今後追記予定。

## 参考

- [Elastic Blog: ELSER](https://www.elastic.co/blog/may-2023-launch-information-retrieval-elasticsearch-ai-model)
