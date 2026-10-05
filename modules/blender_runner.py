"""Blender CLI headless runner for Depth / blockout renders."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./outputs")) / "blender"
BLENDER_BIN = os.getenv("BLENDER_PATH", "blender")


def render_blender_blockout(
    script_code: str,
    output_name: str = "depth",
    resolution: tuple[int, int] = (1920, 1080),
    engine: str = "BLENDER_EEVEE_NEXT",
) -> dict[str, Any]:
    """
    Write a temporary .py script, run Blender headless, capture Depth PNG + stderr.
    Returns {"path": str | None, "stderr": str, "status": "ok" | "error", "returncode": int}
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{output_name}_depth.png"

    # Inject output path & resolution into the provided script if possible
    # (callers should already include camera & render settings; this is a safety net)
    full_script = f"""
import bpy
import sys

# Ensure output directory exists
import os
os.makedirs(r"{OUTPUT_DIR}", exist_ok=True)

{script_code}

# Force render settings (override if script forgot)
scene = bpy.context.scene
scene.render.resolution_x = {resolution[0]}
scene.render.resolution_y = {resolution[1]}
scene.render.filepath = r"{output_path}"
scene.render.engine = "{engine}"

# Prefer depth pass when possible
if hasattr(scene, "view_layers"):
    for vl in scene.view_layers:
        if hasattr(vl, "use_pass_z"):
            vl.use_pass_z = True

bpy.ops.render.render(write_still=True)
print("RENDER_COMPLETE:", r"{output_path}")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(full_script)
        script_path = tmp.name

    try:
        result = subprocess.run(
            [BLENDER_BIN, "-b", "--python", script_path],
            capture_output=True,
            text=True,
            timeout=120,
        )
        status = "ok" if result.returncode == 0 and output_path.exists() else "error"
        return {
            "path": str(output_path) if output_path.exists() else None,
            "stderr": result.stderr,
            "stdout": result.stdout,
            "status": status,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "path": None,
            "stderr": "Blender timed out after 120s",
            "stdout": "",
            "status": "error",
            "returncode": -1,
        }
    finally:
        Path(script_path).unlink(missing_ok=True)
