#!/usr/bin/env python3
"""
StoryboardStudio MCP Server
FastMCP-based multi-granularity storyboard generator.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from modules.blender_runner import render_blender_blockout
from modules.knowledge_db import KnowledgeDB
from modules.sdxl_client import generate_sdxl_image
from modules.vision_evaluator import evaluate_render_vision

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./outputs"))
SVG_DIR = OUTPUT_DIR / "svg"
SVG_DIR.mkdir(parents=True, exist_ok=True)

mcp = FastMCP("StoryboardStudio")
db = KnowledgeDB(os.getenv("KNOWLEDGE_DB", "./storage/storyboard_knowledge.db"))


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def create_svg_anim(filename: str, svg_code: str) -> str:
    """
    Save SVG animation code to disk and perform basic validation.
    Returns the absolute file path.
    """
    if not filename.endswith(".svg"):
        filename += ".svg"
    path = SVG_DIR / filename
    path.write_text(svg_code, encoding="utf-8")
    # Basic sanity check
    if "<svg" not in svg_code.lower():
        return f"WARNING: Saved to {path} but content may not be valid SVG"
    return str(path.resolve())


@mcp.tool()
def render_blender_blockout_tool(
    script_code: str,
    output_name: str = "blockout",
) -> dict[str, Any]:
    """
    Execute Blender headless with the provided bpy script.
    Returns path to Depth PNG, stderr, and status.
    """
    return render_blender_blockout(script_code=script_code, output_name=output_name)


@mcp.tool()
async def generate_sdxl_image_tool(
    prompt: str,
    depth_path: str,
    weight: float = 0.8,
    negative_prompt: str = "blurry, low quality, deformed, ugly",
) -> str:
    """
    Generate final image via SDXL + ControlNet Depth.
    Returns path to the generated PNG.
    """
    return await generate_sdxl_image(
        prompt=prompt,
        depth_path=depth_path,
        weight=weight,
        negative_prompt=negative_prompt,
    )


@mcp.tool()
async def evaluate_render_vision_tool(
    image_path: str,
    criteria: str = "",
) -> dict[str, Any]:
    """
    Score a rendered image with a Vision LLM.
    Returns score (0-10), feedback, and suggested params_delta.
    """
    return await evaluate_render_vision(
        image_path=image_path,
        criteria=criteria or None,  # type: ignore
    )


@mcp.tool()
def save_successful_recipe(
    tag: str,
    camera_params: dict[str, Any],
    prompt: str,
    description: str = "",
    sdxl_negative: str = "",
    controlnet_weight: float = 0.8,
    rating: int = 5,
) -> str:
    """
    Store a high-quality recipe (camera + prompt) into the Knowledge DB.
    Returns the new Recipe ID.
    """
    return db.save_recipe(
        tag=tag,
        camera_params=camera_params,
        sdxl_prompt=prompt,
        description=description or None,
        sdxl_negative=sdxl_negative or None,
        controlnet_weight=controlnet_weight,
        rating=rating,
    )


@mcp.tool()
def search_learned_recipes(query_tag: str, limit: int = 5) -> list[dict[str, Any]]:
    """
    Search the Knowledge DB for past successful recipes by tag/keyword.
    """
    return db.search_recipes(query_tag=query_tag, limit=limit)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
