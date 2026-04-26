# Faiss

Faiss (Facebook AI Similarity Search) は Meta AI Research が開発するベクトル類似検索ライブラリです。

## 概要

- C++ 実装、Python バインディング有り
- CPU / GPU 両対応
- 純粋なライブラリであり、永続化やネットワーク機能は含まれない（DB ではない）

## サポートする index 種別

- `IndexFlat` — 全件線形探索（厳密最近傍）
- `IndexIVF` — 転置ファイル方式（クラスタリング + クラスタ内探索）
- `IndexHNSW` — Hierarchical Navigable Small World グラフ
- `IndexPQ` / `IndexIVFPQ` — Product Quantization による圧縮
- `IndexBinary*` — バイナリベクトル向け

## 特徴

- 大量のベクトル（10^9 規模）に対するスケーラブルな ANN
- GPU 上で数億ベクトルに対するブルートフォース探索が現実的に可能
- 検索精度・速度・メモリのトレードオフを細かく調整可能

## 注意点

- 単独ではサーバプロセスとして動作しないため、Qdrant / Milvus 等との比較では補助的なライブラリ層に位置づけられる
- 永続化は `faiss.write_index` / `faiss.read_index` で手動管理

## 参考

- [Faiss GitHub](https://github.com/facebookresearch/faiss)
