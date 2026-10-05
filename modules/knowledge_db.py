"""SQLite Knowledge Engine for successful storyboard recipes."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB = Path(__file__).parent.parent / "storage" / "storyboard_knowledge.db"


class KnowledgeDB:
    def __init__(self, db_path: str | Path = DEFAULT_DB):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag TEXT NOT NULL,
                    description TEXT,
                    camera_params JSON NOT NULL,
                    sdxl_prompt TEXT NOT NULL,
                    sdxl_negative TEXT,
                    controlnet_weight REAL DEFAULT 0.8,
                    rating INTEGER DEFAULT 5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_recipes_tag ON recipes(tag);
                """
            )

    def save_recipe(
        self,
        tag: str,
        camera_params: dict[str, Any],
        sdxl_prompt: str,
        description: str | None = None,
        sdxl_negative: str | None = None,
        controlnet_weight: float = 0.8,
        rating: int = 5,
    ) -> str:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO recipes
                    (tag, description, camera_params, sdxl_prompt, sdxl_negative, controlnet_weight, rating)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tag,
                    description,
                    json.dumps(camera_params),
                    sdxl_prompt,
                    sdxl_negative,
                    controlnet_weight,
                    rating,
                ),
            )
            conn.commit()
            return str(cur.lastrowid)

    def search_recipes(self, query_tag: str, limit: int = 10) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM recipes
                WHERE tag LIKE ?
                ORDER BY rating DESC, created_at DESC
                LIMIT ?
                """,
                (f"%{query_tag}%", limit),
            ).fetchall()
            results = []
            for row in rows:
                d = dict(row)
                d["camera_params"] = json.loads(d["camera_params"])
                results.append(d)
            return results
