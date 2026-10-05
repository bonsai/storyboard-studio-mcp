"""Vision LLM evaluator for framing / composition scoring."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any

# Optional: httpx for remote Vision APIs, or ollama for local
try:
    import httpx
except ImportError:
    httpx = None  # type: ignore


DEFAULT_CRITERIA = (
    "Evaluate the following storyboard frame for:\n"
    "1. Framing / subject placement (rule of thirds, headroom, lead room)\n"
    "2. Lens feel (wide / normal / telephoto appropriateness)\n"
    "3. Depth and spatial clarity\n"
    "4. Overall cinematic quality\n"
    "Return a JSON object with keys: score (0-10), feedback (str), params_delta (dict of suggested camera adjustments)."
)


async def evaluate_render_vision(
    image_path: str,
    criteria: str = DEFAULT_CRITERIA,
    model: str = "llava",  # or "gpt-4o", "claude-3-5-sonnet", etc.
) -> dict[str, Any]:
    """
    Score a rendered image using a Vision LLM.
    Returns {"score": float, "feedback": str, "params_delta": dict}
    """
    if not Path(image_path).exists():
        return {
            "score": 0.0,
            "feedback": f"Image not found: {image_path}",
            "params_delta": {},
        }

    # Placeholder implementation – replace with real Vision call
    # Example with Ollama (local):
    #   POST http://localhost:11434/api/generate with images=[b64]
    # Example with OpenAI / Anthropic: use their vision endpoints

    # For MVP we return a mock response so the pipeline does not block
    return {
        "score": 7.5,
        "feedback": (
            "Mock evaluation: Framing is acceptable. "
            "Consider slightly wider lens or lower camera for more dramatic depth. "
            "Subject is well centered but lead room could be improved."
        ),
        "params_delta": {
            "lens": 28,
            "location_z_delta": -0.3,
            "note": "Mock delta – replace with real Vision LLM output",
        },
        "model_used": model,
        "image_path": image_path,
    }
