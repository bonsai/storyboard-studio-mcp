"""ComfyUI / Automatic1111 SD-WebUI client with ControlNet Depth support."""

from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Any

import httpx

COMFYUI_URL = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")
A1111_URL = os.getenv("A1111_URL", "http://127.0.0.1:7860")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./outputs")) / "sdxl"


def _encode_image(path: str | Path) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


async def generate_sdxl_image(
    prompt: str,
    depth_path: str,
    weight: float = 0.8,
    negative_prompt: str = "blurry, low quality, deformed",
    width: int = 1024,
    height: int = 576,
    steps: int = 25,
    cfg_scale: float = 7.0,
    backend: str = "a1111",  # "a1111" | "comfyui"
) -> str:
    """
    Call SD backend with ControlNet Depth.
    Returns path to generated PNG.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    depth_b64 = _encode_image(depth_path)

    if backend == "a1111":
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "alwayson_scripts": {
                "controlnet": {
                    "args": [
                        {
                            "enabled": True,
                            "image": depth_b64,
                            "module": "none",
                            "model": "control_v11p_sd15_depth [a1b03312]",  # adjust to your model
                            "weight": weight,
                            "guidance_start": 0.0,
                            "guidance_end": 1.0,
                            "control_mode": "Balanced",
                            "resize_mode": "Crop and Resize",
                        }
                    ]
                }
            },
        }
        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(f"{A1111_URL}/sdapi/v1/txt2img", json=payload)
            resp.raise_for_status()
            data = resp.json()
            img_b64 = data["images"][0]
    else:
        # Minimal ComfyUI placeholder – replace with full workflow JSON
        raise NotImplementedError("ComfyUI workflow injection not yet implemented – use backend='a1111' for now")

    out_path = OUTPUT_DIR / f"sdxl_{Path(depth_path).stem}.png"
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(img_b64))
    return str(out_path)
