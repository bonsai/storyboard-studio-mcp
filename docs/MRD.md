# 市場要求仕様書 (MRD: Market Requirements Document)

**製品名（仮称）:** StoryboardStudio MCP  
**ドキュメントバージョン:** 1.0  
**作成日:** 2026年10月5日

---

## 1. エグゼクティブサマリー (Executive Summary)

StoryboardStudio MCP は、映像制作者、アニメーター、Web/ゲームクリエイター向けに、1つのテキストプロンプトから「2Dアニメ（SVG）」「3Dレイアウト（Blender bpy）」「高精細ルック（SDXL）」の3つの異なる粒度の絵コンテアセットをCLI/MCP経由で一括自動生成し、さらにVision LLMによる自動修正と成功データの学習を行う次世代の絵コンテ制作エージェントシステムです。

従来の絵コンテ制作における「構図・タイミング・完成イメージの認識ギャップ」を解消し、プリプロダクション工程の速度を大幅に向上させます。

---

## 2. ターゲットユーザーとペルソナ (Target Users & Personas)

### プライマリペルソナ：映像ディレクター / 映像クリエイター
- **課題:** クライアントやチームへ構図や演出の意図を伝える際、2Dのラフスケッチだけでは「カメラワークやレンズ感（パース）」が伝わらず、手戻りが発生する。
- **ニーズ:** 3Dのカメラレイアウトと完成版ルックの双方を、アイデア出しの段階で素早く可視化したい。

### セカンダリペルソナ：AI生成クリエイター / 技術開発者
- **課題:** 画像生成AI（SDXL等）単体では、カメラの焦点距離や被写体の正確な3D空間配置をコントロールするのが困難。
- **ニーズ:** MCP（Model Context Protocol）を活用し、Claude DesktopやCursor、自作CLIエージェントからローカルツール（Blender/ComfyUI）をシームレスに操作・制御したい。

---

## 3. 市場の課題と機会 (Market Problem & Opportunity)

### 課題 (Problems)
- **絵コンテ表現の粒度不足:** 単一の画像生成AIは「見栄え」は良いが、「カメラワーク（レンズmm）」「オブジェクトの立体関係」「動きのタイミング」の検証ができない。
- **ツール間の分断:** 2D作画、3Dブロックアウト（Blender）、AI画像生成（SDXL）が個別のワークフローとなっており、データ連携・修正の手間が大きい。
- **ノウハウの属性化・再利用不能:** 「このカメラアングルとPromptの組み合わせが上手くいった」という成功パターンが蓄積・再利用されない。

### 機会 (Opportunities)
- **MCP（Model Context Protocol）の普及:** LLMエージェントからローカルツール（Blender CLI、ComfyUI API、ローカルDB）を統合制御する標準規格としての位置づけ。
- **Vision LLMと3D/生成AIの融合:** Vision LLMによる自動フィードバック機構（Self-Correction）を入れることで、人間が介在せずにクオリティを底上げ可能。

---

## 4. 製品ビジョンとコンセプト (Product Vision)

> 「1つのアイディアから、動き・空間・質感のすべてを網羅した絵コンテを自動生成し、使えば使うほど賢くなる自律型クリエイティブパートナー」

```
[ Prompt ] ──► [ MCP Agent ] ──► ① 2D SVG (Timing & Symbol)
                                 ② 3D bpy (Camera & Depth)  ──┐ (ControlNet)
                                 ③ SDXL   (Look & Lighting) ◄─┘
                                 └─► [ Auto-Correction & DB Learning ]
```

---

## 5. 主要機能要件 (Key Requirements)

### 5.1. 多粒度マルチモーダル生成 (Multi-Granularity Generation)
- **REQ-1.1 [2Dモーショングラフィックス生成]:** 軽量な2D SVGアニメーションコードを生成し、オブジェクトの移動タイミング・視線誘導を検証可能にすること。
- **REQ-1.2 [3Dブロックアウト・カメラ制御 (bpy)]:** Blender PythonスクリプトをCLIバックグラウンドで実行し、指定されたカメラアングル（焦点距離、高さ、ターゲット追従）およびDepth/Wireframe画像を書き出すこと。
- **REQ-1.3 [完成ビジュアル生成 (SDXL + ControlNet)]:** REQ-1.2で生成されたDepth画像をControlNetの入力とし、プロンプトに沿った完成イメージ（16:9等）を生成・出力すること。

### 5.2. インターフェース要件 (MCP / CLI First)
- **REQ-2.1 [MCP準拠]:** Stdio接続可能なFastMCP / SDKベースのMCPサーバーとして実装し、Claude Desktop, Cursor, Custom Agent等から呼び出し可能であること。
- **REQ-2.2 [完全ローカル/CLI実行]:** GUIを立ち上げず、`blender --background` や WebUI API 呼び出しにより、すべてヘッドレス（CLI）で動作可能であること。

### 5.3. 自律修正機能 (Self-Correction Loop)
- **REQ-3.1 [Blenderエラーログ解析]:** スクリプト実行時のPython文法エラーやコンテキストエラーを自律解析し、修正プロンプトを生成すること。
- **REQ-3.2 [Vision LLM による評価と差分修正]:** 書き出されたDepth/レンダリング画像を評価し、「カメラ距離の不備」「構図の崩れ」を検知した場合、bpy パラメータやPromptの差分更新を行い再生成を実行すること。

### 5.4. ナレッジ蓄積・学習機能 (Learning & Knowledge Base)
- **REQ-4.1 [成功レシピの保存]:** 高評価を得た構図パラメータ（カメラレンズ値、オブジェクト配置）、SDXL Prompt、ControlNetの重みを構造化データ（SQLite/JSON）として保存すること。
- **REQ-4.2 [過去パターンの検索・適用]:** 新しいシーン生成時、タグやキーワード（例: cyberpunk_chase, low_angle）で過去の成功レシピを検索し、Prompt/スクリプトのベースとして自動適用すること。

---

## 6. 非機能要件 (Non-Functional Requirements)

- **パフォーマンス:** 1カット（SVG + bpy 3D Depth + SDXL）の一括生成が、ローカルGPU環境（例: RTX 3090/4090）において60秒以内で完了すること。
- **拡張性:** 将来的にSDXL以外のモデル（Flux, Cascade等）や、Blender以外のツール（Unreal Engine CLI等）へのプラグイン拡張が可能なMCPツール構成とすること。
- **ポータビリティ:** Windows / macOS (Apple Silicon) / Linux 環境で、指定の環境変数・依存関係をセットアップすることで同等に動作すること。

---

## 7. 成功指標 (KPIs / Success Metrics)

- **絵コンテ制作時間の削減率:** 従来の3Dレイアウト＋画像合成手順と比較して、80%以上の制作時間短縮を達成する。
- **修正レスポンス精度 (Self-Correction Success Rate):** Vision LLM / エラーチェックによる自動リトライで、2回以内の修正で所望の構図が得られる確率 85% 以上。
- **ナレッジ再利用率 (Recipe Reuse Rate):** ユーザーが新規カット作成時に過去の保存レシピを参照・適用する割合 40% 以上。

---

## 8. ロードマップ (Product Roadmap)

- **Phase 1 (PoC / Alpha):** FastMCP サーバーの構築。SVG生成、Blender CLI連動、SDXL API連携の基本パイプライン実装。
- **Phase 2 (Beta - Correction & Learning):** SQLiteによる成功レシピDBの実装。Vision LLM による画角評価・自動リトライ機能の統合。
- **Phase 3 (v1.0 Release):** マルチカット（一連の連続シーン）の一括生成・一貫性（Character Consistency）維持機能の追加、ドキュメント公開。
