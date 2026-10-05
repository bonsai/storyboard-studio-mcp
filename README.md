# StoryboardStudio MCP

**MCP-native pre-production system** that generates multi-granularity storyboard assets from text prompts:

1. **2D SVG Motion** – timing-validated animation code  
2. **3D Depth / Blockout** – Blender headless (bpy) Depth maps  
3. **Final Look (SDXL)** – ControlNet Depth-guided image generation  

LLM agents (Claude Desktop, Cursor, etc.) control the entire pipeline via **Stdio + FastMCP**.  
Includes **Vision-based self-correction** and a **SQLite Knowledge Database** of successful recipes.

---

## Architecture

```
[ MCP Client ] (Claude Desktop / Cursor / Custom Agent)
     │
     ▼ (Stdio / JSON-RPC)
[ StoryboardStudio MCP Server (Python FastMCP) ]
     │
     ├─► SVG Motion Engine          → .svg
     ├─► Blender CLI Runner         → Depth / Wireframe PNG
     ├─► ComfyUI / SD-WebUI Client  → Final Image (ControlNet)
     ├─► Vision Evaluator           → Score + Refinement Delta
     └─► Knowledge Engine (SQLite)  → storyboard_knowledge.db
```

---

## Requirements

| Component              | Version / Notes                          |
|------------------------|------------------------------------------|
| Python                 | 3.11+                                    |
| Blender                | 4.0+ (with `blender` in PATH)            |
| ComfyUI **or** A1111   | Running on `127.0.0.1:8188` or `:7860`   |
| Ollama (optional)      | For local Vision evaluation              |
| GPU                    | RTX 3090+ recommended (target < 60 s/shot) |

```bash
pip install -r requirements.txt
```

---

## Quick Start

### 1. Initialize Knowledge DB
```bash
python scripts/init_db.py
```

### 2. Run the MCP Server
```bash
python server.py
```

### 3. Register with Claude Desktop / Cursor

Add to your MCP config (`claude_desktop_config.json` or Cursor settings):

```json
{
  "mcpServers": {
    "storyboard-studio": {
      "command": "python",
      "args": ["/absolute/path/to/storyboard-studio-mcp/server.py"],
      "env": {
        "BLENDER_PATH": "blender",
        "COMFYUI_URL": "http://127.0.0.1:8188",
        "OUTPUT_DIR": "/absolute/path/to/storyboard-studio-mcp/outputs"
      }
    }
  }
}
```

See `mcp_config.json` for a ready-to-use template.

---

## MCP Tools

| Tool                        | Description                                      |
|-----------------------------|--------------------------------------------------|
| `create_svg_anim`           | Save & validate SVG animation code               |
| `render_blender_blockout`   | Run Blender headless → Depth PNG                 |
| `generate_sdxl_image`       | ComfyUI/WebUI + ControlNet Depth → final image   |
| `evaluate_render_vision`    | Vision LLM scores framing / composition          |
| `save_successful_recipe`    | Store high-rated camera + prompt to SQLite       |
| `search_learned_recipes`    | Retrieve past successful recipes by tag          |

---

## Project Structure

```
storyboard-studio-mcp/
├── server.py                 # FastMCP entry point (all tools)
├── modules/
│   ├── blender_runner.py     # Blender CLI + Depth injection
│   ├── sdxl_client.py        # ComfyUI / A1111 API client
│   ├── vision_evaluator.py   # Vision LLM evaluation
│   └── knowledge_db.py       # SQLite recipe store
├── scripts/
│   └── init_db.py            # Create storyboard_knowledge.db
├── outputs/
│   ├── svg/
│   ├── blender/
│   └── sdxl/
├── storage/
│   └── storyboard_knowledge.db
├── tests/
├── mcp_config.json
├── requirements.txt
└── README.md
```

---

## Development Roadmap (from WBS)

**Phase 1 (MVP)** – Core pipeline  
**Phase 2** – Self-Correction Loop + Knowledge Engine  

See the original Technical Specifications / PRD / MRD for full details.

---

## License

MIT

---

**StoryboardStudio MCP** – Reduce storyboard iteration friction to near zero.
