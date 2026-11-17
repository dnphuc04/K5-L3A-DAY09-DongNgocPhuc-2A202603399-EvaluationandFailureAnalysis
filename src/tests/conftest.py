from __future__ import annotations

from pathlib import Path

import pytest

from lab8.config_loader import repo_path
from lab8.db import init_store, load_json, load_jsonl

WORLD = load_json(repo_path("data", "public_world_state.json"))
CLAIMS = load_jsonl(repo_path("data", "public_claims.jsonl"))
BY_ID = {row["claim_id"]: row for row in CLAIMS}


@pytest.fixture(autouse=True)
def isolate_shape_registry():
    """Keep runtime variant registration local to the test that requested it."""
    from lab8.shapes import SHAPES

    original = SHAPES.copy()
    try:
        yield
    finally:
        SHAPES.clear()
        SHAPES.update(original)


@pytest.fixture
def public_db(tmp_path: Path) -> Path:
    store = tmp_path / "public.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    return store
