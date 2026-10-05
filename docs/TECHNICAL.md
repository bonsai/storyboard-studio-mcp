# 技術仕様書 (Technical Specifications)

**製品名:** StoryboardStudio MCP  
**ドキュメントバージョン:** 1.0  
**作成日:** 2026年10月5日

---

## 1. システム構成・アーキテクチャ

Stdio接続ベースのMCP（Model Context Protocol）サーバーを中心に、ローカルCLIツール（Blender）、ローカルAPI（ComfyUI / Ollama / OpenAI API等）を非同期実行するパイプライン構成。

```
[ MCP Client ] (Claude Desktop / Cursor / Custom Agent CLI)
     │
     ▼ (Stdio / JSON-RPC)
[ StoryboardStudio MCP Server (Python FastMCP) ]
     │
     ├─► [ 1. SVG Motion Engine ] ──► SVG Code (.svg)
     │
     ├─► [ 2. Blender CLI Runner ] ──► subprocess ("blender -b -P ...") ──► Depth/Wireframe PNG
     │                                                                           │
     ├─► [ 3. ComfyUI / SD-WebUI API Client ] ◄───────────────────────────────────┘ (ControlNet)
     │         └──► Final Image (.png)
     │
     ├─► [ 4. Vision Evaluator (Ollama / Claude Vision API) ] ──► Rating & Refinement Delta
     │
     └─► [ 5. Knowledge Engine (SQLite) ] ──► Recipe Database (storyboard_knowledge.db)
```

---

## 2. コンポーネントおよび外部ツールインターフェース仕様

### 2.1. Blender (bpy) Headless 実行仕様
- **実行方式:** `subprocess.run(["blender", "-b", "--python", script_path])` による非同期バックグラウンド処理。
- **コンテキスト設定:**
  - レンダリングエンジン: CYCLES または BLENDER_EEVEE_NEXT（迅速処理時は Workbench / Depth Pass）
  - 出力パス・解像度（デフォルト 1920×1080 / 1024×576）およびカメラ焦点距離（lens）を自動インジェクション。
- **エラー検知:** Standard Error (stderr) から Python トレースバックをキャプチャし、ログ解析モジュールへ渡す。

### 2.2. ComfyUI / SD-WebUI API 仕様
- **通信形式:** REST API (`http://127.0.0.1:8188/prompt` または `http://127.0.0.1:7860/sdapi/v1/txt2img`)
- **ControlNet 連携:**
  - Preprocessor: none（Blender側で出力したZ-Depth画像を使用）
  - Model: controlnet-depth-sdxl / control_v11p_sd15_depth
  - Weight / Guidance: 0.6 〜 0.95（可変制御）

### 2.3. Knowledge Database (SQLite) スキーマ仕様
- **ファイルパス:** `./storage/storyboard_knowledge.db`

```sql
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT NOT NULL,                  -- 例: 'cyberpunk_chase', 'low_angle_car'
    description TEXT,                   -- シーンの自然言語概要
    camera_params JSON NOT NULL,        -- {"lens": 24, "location": [0, -5, 1.2], "rotation": [1.4, 0, 0]}
    sdxl_prompt TEXT NOT NULL,          -- 使用プロンプト
    sdxl_negative TEXT,                 -- ネガティブプロンプト
    controlnet_weight REAL DEFAULT 0.8, -- ControlNet適用強度
    rating INTEGER DEFAULT 5,           -- 5段階評価
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recipes_tag ON recipes(tag);
```

---

## 3. MCP Tool 関数シグネチャ定義

| ツール名 | 引数 (Arguments) | 戻り値 (Return) | 説明 |
|----------|------------------|-----------------|------|
| `create_svg_anim` | filename: str, svg_code: str | str (ファイルパス) | SVGコードの保存と検証 |
| `render_blender_blockout` | script_code: str, output_name: str | Dict[str, Any] (path, stderr, status) | Blender CLI実行とDepth画像書き出し |
| `generate_sdxl_image` | prompt: str, depth_path: str, weight: float | str (生成画像パス) | ComfyUI/WebUI API呼出による画像生成 |
| `evaluate_render_vision` | image_path: str, criteria: str | Dict[str, Any] (score, feedback, params_delta) | Vision LLMによる画角・構図の自律採点 |
| `save_successful_recipe` | tag: str, camera_params: dict, prompt: str | str (Recipe ID) | 成功パターンのDB登録 |
| `search_learned_recipes` | query_tag: str | List[Dict] (過去成功事例) | DBからの設定検索・抽出 |

---

## 4. 開発タスク分解 (WBS: Work Breakdown Structure)

### Phase 1: Core Pipeline & MVP (1〜3週)

**1.0 環境構築 & MCPサーバー基盤**
- 1.1 プロジェクトディレクトリ・FastMCP サーバー骨組み作成
- 1.2 出力ディレクトリ管理 (`/outputs/svg`, `/outputs/blender`, `/outputs/sdxl`) の実装
- 1.3 mcp_config.json の定義と Client (Claude / Cursor) 接続検証

**2.0 生成エンジン開発 (Phase 1 モジュール)**
- 2.1 [SVG] SVGファイル書き出しツール (`create_svg_anim`) の実装
- 2.2 [bpy] Blender CLIラッパー (`render_blender_blockout`) 実装
  - 2.2.1 バックグラウンドプロセス起動ロジック
  - 2.2.2 レンダリング結果 (Depth/Pass) のファイル出力インジェクション
  - 2.2.3 stderr からのPythonエラー検知ロジック
- 2.3 [SDXL] ComfyUI / SD-WebUI APIクライアント (`generate_sdxl_image`) 実装
  - 2.3.1 txt2img API リクエストパケット生成
  - 2.3.2 ControlNet (Depth) Base64/ファイル参照処理の統合

**3.0 パイプライン結合テスト (MVP)**
- 3.1 「SVG ➔ bpy ➔ SDXL」の一括パイプライン呼び出しテスト

### Phase 2: Self-Correction & Knowledge Engine (4〜6週)

**4.0 自律修正機能 (Self-Correction Loop) の実装**
- 4.1 [Log Analyzer] Blender実行ログ解析ツール (`check_blender_errors`) の実装
- 4.2 [Param Refiner] camera_params / lens 値のピンポイント更新ツール実装
- 4.3 [Vision Evaluator] Vision LLM 連携評価ツール (`evaluate_render_vision`) の実装
  - 4.3.1 画像エンコード & Vision LLM プロンプトテンプレート作成
  - 4.3.2 評価スコア・修正アングル指示（JSON）のパース処理

**5.0 ナレッジベース・学習エンジン (Knowledge Engine) の実装**
- 5.1 SQLite データベーススキーマ作成 & 初期化スクリプトの実装
- 5.2 成功レシピ登録ツール (`save_successful_recipe`) の実装
- 5.3 類似タグ検索ツール (`search_learned_recipes`) の実装

**6.0 エージェント統合テスト & 調整**
- 6.1 エージェント用システムプロンプト (プロトコル指示) のチューニング
- 6.2 「参照 ➔ 生成 ➔ 評価 ➔ 修正 ➔ 保存」ループ全体の自動実行検証

---

## 5. 成果物一覧 (Deliverables)

| 区分 | 成果物 | 概要 |
|------|--------|------|
| ソースコード | `server.py` | FastMCPベースの統合MCPサーバー |
| | `modules/blender_runner.py` | Blender CLI制御 & Depthパス出力モジュール |
| | `modules/sdxl_client.py` | ComfyUI / SD-WebUI APIクライアント |
| | `modules/vision_evaluator.py` | Vision LLMによる自動評価モジュール |
| | `modules/knowledge_db.py` | SQLite接続・レシピ検索保存モジュール |
| データベース | `storyboard_knowledge.db` | 成功レシピ・設定が蓄積されるSQLite DB |
| 設定・ドキュメント | `mcp_config.json` | MCPクライアント用登録設定ファイル |
| | `README.md` | ローカル環境（Blender/ComfyUI）連携セットアップガイド |
| | `docs/MRD.md` / `docs/PRD.md` / `docs/TECHNICAL.md` | 要求・仕様ドキュメント一式 |
