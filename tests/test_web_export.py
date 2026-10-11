from __future__ import annotations

import json

import pytest

from pipeline.ingest import WEB_COLUMNS, export_web_data
from src.constants import DB_PATH


def test_web_export_reconciles_with_active_snapshot(tmp_path) -> None:
    manifest = export_web_data(tmp_path, DB_PATH)

    assert manifest["latestDate"] == "2026-10-08"
    assert len(manifest["snapshots"]) == 1

    snapshot_meta = manifest["snapshots"][0]
    assert snapshot_meta["rowCount"] == 59139
    assert snapshot_meta["kpis"] == {
        "total": 59139,
        "sold": 49040,
        "stock": 10099,
        "consumption": pytest.approx(0.8292328244),
    }

    snapshot = json.loads(
        (tmp_path / snapshot_meta["file"]).read_text(encoding="utf-8")
    )
    assert snapshot["schemaVersion"] == 1
    assert snapshot["columns"] == WEB_COLUMNS
    assert len(snapshot["rows"]) == 59139

    velocity = json.loads((tmp_path / "velocity.json").read_text(encoding="utf-8"))
    assert len(velocity["timeline"]) == 1
    assert velocity["transitions"] == []
