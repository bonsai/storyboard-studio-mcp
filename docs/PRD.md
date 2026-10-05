# 製品要求仕様書 (PRD: Product Requirements Document)

**製品名:** StoryboardStudio MCP  
**ドキュメントバージョン:** 1.0  
**作成日:** 2026年10月5日  
**ステータス:** 承認待ち (Draft)

---

## 1. 製品概要 (Product Overview)

StoryboardStudio MCP は、テキストプロンプトから「2Dモーショングラフィックス（SVG）」「3Dレイアウト（Blender/bpy）」「完成ルック（SDXL）」の3つの異なる粒度の絵コンテアセットを一括自動生成する、MCP（Model Context Protocol）ネイティブなCLIプリプロダクション支援システムである。

LLMエージェント（Claude Desktop、Cursor等）からStdio経由で直接操作し、Vision LLMによる自動品質評価（Self-Correction）および過去の成功パターンの蓄積・適用（Knowledge Database）を行うことで、絵コンテ制作における意図伝達の手戻りを極限まで削減する。

---

## 2. ユーザーペルソナ & ユースケース

### ペルソナ 1: 映像ディレクター / アニメーター
- **課題:** 2Dラフだけではカメラの画角（レンズ径）や空間奥行きがチームに正しく伝わらず、3Dプリビズの起こし直しが発生する。
- **ユースケース:** テキストで構図を指示し、即座に3D Depth画像と高精細SDXLルックを取得して構図・レンズ感を確定させる。

### ペルソナ 2: AIパイプラインエンジニア / クリエイター
- **課題:** 生の bpy コードをLLMに生成させると文法エラーやBlenderのバージョン不整合で処理が停止する。
- **ユースケース:** Pydanticの宣言的スキーマ（SceneBlueprint）を介して安全にBlenderを制御し、結果をSQLite DBに成功レシピとして蓄積・再利用する。

---

## 3. 機能要求仕様 (Functional Requirements)

### FR-1: MCP統合インターフェース
- **FR-1.1:** FastMCPを採用し、Stdio接続でのMCP Tools / Resources プロトコルに完全準拠すること。
- **FR-1.2:** 外部クライアント（Claude Desktop / Cursor）から直接実行可能なCLI実行構造であること。

### FR-2: 多粒度絵コンテ生成機能 (Multi-Granularity Engine)
- **FR-2.1 (2D):** タイミング検証用の2D SVGアニメーションコード生成およびファイル保存機能。
- **FR-2.2 (3D/bpy):** 宣言的JSONデータ（SceneBlueprint）から確実な bpy コードを自動生成し、Blender CLIバックグラウンド実行で Depth マップをレンダリング出力する機能。
- **FR-2.3 (SDXL):** ComfyUI / SD-WebUI REST APIを呼び出し、FR-2.2のDepth画像を ControlNet 入力とした画像生成機能。

### FR-3: 成功レシピ管理機能 (Knowledge Engine)
- **FR-3.1 (Save):** 評価の高い SceneBlueprint（カメラ/オブジェクト座標）とSDXLプロンプト、ControlNet重みを SQLite DB（storyboard_knowledge.db）に保存する機能。
- **FR-3.2 (Search):** タグやキーワード指定により、類似する過去の成功レシピを検索・JSON抽出する機能。

### FR-4: 自律評価・修正機能 (Self-Correction Loop)
- **FR-4.1:** Blenderのレンダリングログ（stderr）を監視し、エラー発生時にプロンプト・パラメータの補正候補を抽出する機能。
- **FR-4.2:** Vision LLMを活用し、レンダリング画像の画角・被写体収まりをスコアリング評価および差分修正指示を出す機能。

---

## 4. 非機能要求仕様 (Non-Functional Requirements)

- **NFR-1 (パフォーマンス):** 1カット（SVG + 3D Depth + SDXL）の全生成パイプライン処理がローカルGPU（RTX 3090以上想定）環境下で **60秒以内** に完了すること。
- **NFR-2 (堅牢性):** 不正な SceneBlueprint や構図パラメータが入力された場合でも、MCPサーバー全体がクラッシュせず、エラーメッセージを安全に返却すること。
- **NFR-3 (環境独立性):** Blender CLI (`blender -b`) および ComfyUI / SD-WebUI API が起動していれば、OS（Windows / macOS / Linux）に依存せず動作すること。

---

## プロジェクト・カンバンボード (Kanban Board)

```
[ Backlog ] ──► [ To Do ] ──► [ In Progress ] ──► [ Review / Testing ] ──► [ Done ]
```

### 📋 Backlog (次回以降のロードマップ)

| ID | タスクタイトル | 概要 | 優先度 |
|----|----------------|------|--------|
| BLK-01 | Multi-Shot Continuity | 複数カット間におけるキャラクター・背景の一貫性保持機能 | Med |
| BLK-02 | Unreal Engine 5 CLI Plugin | Blenderに加えUE5 headless レンダリング機能の追加 | Low |
| BLK-03 | Web-based Interactive Canvas | 生成されたSVG/Depth/SDXLをブラウザで並べて比較評価するUI | Low |

### 📝 To Do (着手予定)

| ID | タスクタイトル | 概要 | 優先度 |
|----|----------------|------|--------|
| TOD-01 | Vision LLM 評価ツールの追加 | evaluate_render_vision の組み込みとプロンプト設計 | High |
| TOD-02 | ComfyUI WebSocket/API 連携強化 | A1111依存からComfyUI直接ワークフロー実行への移行 | High |
| TOD-03 | エラーハンドリング・フォールバック強化 | Blender/SDXLの接続タイムアウト時等のリカバリ処理追加 | Med |

### 🔄 In Progress (現在進行中)

| ID | タスクタイトル | 概要 | 担当 |
|----|----------------|------|------|
| PRG-01 | FastMCP / SQLite レシピDB統合 | server.py へのSQLite検索・保存ツールの実装と結合 | Lead |
| PRG-02 | GitHub CI/CD & リポジトリ整備 | GitHubへのPush、mcp_config.json テンプレートおよびREADME整備 | Lead |

### 🔍 Review / Testing (レビュー・テスト中)

| ID | タスクタイトル | 概要 | ステータス |
|----|----------------|------|------------|
| REV-01 | MCP-Native bpy スキーマテスト | SceneBlueprint 経由での Blender CLI 正常動作テスト | Testing |
| REV-02 | ControlNet Depth 伝達検証 | BlenderのDepth PNGがSDXLに正しく適用されるかの検証 | Review |

### ✅ Done (完了)

| ID | タスクタイトル | 概要 | 完了日 |
|----|----------------|------|--------|
| DON-01 | MRD (市場要求仕様書) の策定 | 市場課題、ターゲットペルソナ、全体ビジョンのドキュメント化 | 2026-10-05 |
| DON-02 | WBS & 技術仕様書の作成 | フェーズ別タスク分解およびシステム構成・API設計 | 2026-10-05 |
| DON-03 | 宣言的 SceneBlueprint 設計 | 生コード生成からJSON Schemaベースの安全な bpy 生成への切り替え | 2026-10-05 |
| DON-04 | 統合版 server.py の実装 | SVG / bpy / SDXL / SQLite を統合したFastMCPコードの作成 | 2026-10-05 |
