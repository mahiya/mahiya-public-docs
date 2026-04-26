# Qdrant

Qdrant は Rust で書かれたオープンソースのベクトルデータベースです。

## 概要

- Rust 実装による高速性とメモリ安全性
- gRPC / REST 両対応の API
- Self-hosted / Qdrant Cloud / Embedded（qdrant-client の in-memory）の各形態で利用可能
- Apache 2.0 ライセンス

## 主な機能

- HNSW ベースの ANN 探索
- Scalar / Product / Binary Quantization に対応
- Payload（メタデータ）に基づくフィルタリング検索
  - ペイロードインデックスによる高速化
- Sparse Vector / Dense Vector の併用（ハイブリッド検索）
- Multi-tenant 構成（コレクション or ペイロードフィルタによる分離）

## アーキテクチャの特徴

- ストレージは memmap ベース、または in-memory モード
- Distributed mode により、シャーディング・レプリケーションをサポート
- Optimizer によるバックグラウンドでのセグメント統合・最適化

## ユースケース

- RAG（Retrieval-Augmented Generation）におけるベクトルストア
- 推薦システムのアイテム類似度検索
- 画像・テキストのマルチモーダル検索

## 参考

- [Qdrant 公式サイト](https://qdrant.tech/)
- [Qdrant GitHub](https://github.com/qdrant/qdrant)
