"""Basic smoke tests for StoryboardStudio MCP modules."""

import sys
from pathlib import Path

# Allow importing from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.knowledge_db import KnowledgeDB


def test_knowledge_db_roundtrip(tmp_path):
    db_path = tmp_path / "test.db"
    db = KnowledgeDB(db_path)

    rid = db.save_recipe(
        tag="test_low_angle",
        camera_params={"lens": 24, "location": [0, -5, 1.2], "rotation": [1.4, 0, 0]},
        sdxl_prompt="cinematic low angle shot of a car, cyberpunk",
        description="Test recipe",
        rating=8,
    )
    assert rid is not None

    results = db.search_recipes("low_angle")
    assert len(results) >= 1
    assert results[0]["tag"] == "test_low_angle"
    assert results[0]["camera_params"]["lens"] == 24


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        test_knowledge_db_roundtrip(Path(d))
    print("✅ Basic knowledge DB test passed")
