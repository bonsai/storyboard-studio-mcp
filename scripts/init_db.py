#!/usr/bin/env python3
"""Initialize the Storyboard Knowledge Database."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "storage" / "storyboard_knowledge.db"

SCHEMA = """
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

def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print(f"✅ Knowledge DB initialized at: {DB_PATH}")

if __name__ == "__main__":
    main()
