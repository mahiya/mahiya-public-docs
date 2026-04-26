# BBQ (Better Binary Quantization)

BBQ は Elasticsearch / Lucene における、ベクトル量子化の手法です。

## 概要

- 高次元 dense vector を低ビット表現（1bit / 2bit など）に圧縮することで、メモリとストレージのコストを大きく削減
- 単純な scalar quantization に比べ、再ランキングを併用することで recall を維持しやすい
- Elasticsearch 8.16 以降で利用可能

## 特徴

- メモリフットプリントを大幅に削減（約 1/32）
- HNSW グラフと組み合わせて、近似最近傍探索の高速化を実現
- ランダム回転＋ビット符号化により、内積近似の品質を保つ

## ユースケース

- 大規模ベクトル検索（数億件規模）でのコスト最適化
- Embedding モデルの dim が大きいケース（768 / 1024 / 1536 dim 等）

## 参考

- [Elastic Blog: Better Binary Quantization](https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch)
