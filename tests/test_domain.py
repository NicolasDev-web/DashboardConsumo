from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from src.constants import INITIAL_WORKBOOK
from src.importer import read_snapshot
from src.metrics import floor_metrics, portfolio_kpis, transition_metrics
from src.storage import active_snapshot_dates, import_snapshot, load_snapshot
from src.transform import transform_snapshot, warning_counts
from src.validation import validate_structure
from src.views.floors import infer_stack


@pytest.fixture(scope="session")
def initial_snapshot() -> pd.DataFrame:
    raw = read_snapshot(INITIAL_WORKBOOK)
    assert validate_structure(raw).is_valid
    return transform_snapshot(raw)


def test_initial_snapshot_reconciles_with_sdd(initial_snapshot: pd.DataFrame) -> None:
    assert portfolio_kpis(initial_snapshot) == {
        "total": 59139,
        "sold": 49040,
        "stock": 10099,
        "consumption": pytest.approx(0.8292328244),
    }
    assert initial_snapshot["enterprise_name"].nunique() == 178
    assert initial_snapshot["city"].nunique() == 24
    assert initial_snapshot[["enterprise_id", "block_id"]].drop_duplicates().shape[0] == 1818


def test_quality_counts_reconcile_with_sdd(initial_snapshot: pd.DataFrame) -> None:
    counts = warning_counts(initial_snapshot)
    assert counts["Andar não informado"] == 281
    assert counts["Pavimentos não informado"] == 224
    assert counts["Andar superior aos pavimentos"] == 264
    assert counts["Divergência entre status oficial e CRM"] == 237


def test_floor_one_reconciles_with_sdd(initial_snapshot: pd.DataFrame) -> None:
    floor_one = floor_metrics(initial_snapshot).query("floor == 1").iloc[0]
    assert int(floor_one["total"]) == 8431
    assert int(floor_one["sold"]) == 7001
    assert int(floor_one["stock"]) == 1430
    assert floor_one["consumption"] == pytest.approx(0.830388, abs=1e-6)


def test_inferred_stacks_preserve_floor_rule_and_flag_collisions(
    initial_snapshot: pd.DataFrame,
) -> None:
    positioned = infer_stack(initial_snapshot)
    comparable = positioned.loc[positioned["inferred_stack"].notna()]
    assert comparable["inferred_stack"].between(1, 12).all()
    assert positioned.loc[positioned["floor"].isna(), "inferred_stack"].isna().all()
    collision_rows = comparable.duplicated(
        ["block_id", "floor", "inferred_stack"], keep=False
    )
    assert int(collision_rows.sum()) == 6


def test_validation_blocks_duplicate_and_empty_ids() -> None:
    frame = pd.DataFrame(
        {
            "ID Empreendimento": ["e", "e", "e"],
            "ID Bloco": ["b", "b", "b"],
            "ID da Unidade": ["u1", "u1", None],
            "Cidade": ["A"] * 3,
            "Empreendimento": ["E"] * 3,
            "Bloco": ["B"] * 3,
            "Unidade": ["1", "2", "3"],
            "Status Unidade": ["VENDIDO"] * 3,
            "Pavimentos": [2] * 3,
            "Posição Vertical": [1] * 3,
        }
    )
    result = validate_structure(frame)
    assert not result.is_valid
    assert len(result.invalid_rows) == 3


def test_transitions_ignore_added_and_removed_units() -> None:
    frame = pd.DataFrame(
        {
            "snapshot_date": pd.to_datetime(["2026-01-01"] * 3 + ["2026-01-31"] * 3),
            "unit_id": ["a", "b", "removed", "a", "b", "added"],
            "is_sold": [False, True, False, True, False, True],
        }
    )
    result = transition_metrics(frame).iloc[0]
    assert result["new_sales"] == 1
    assert result["reversals"] == 1
    assert result["net_sales"] == 0
    assert result["added_units"] == 1
    assert result["removed_units"] == 1


def test_storage_import_and_transactional_replacement(tmp_path, initial_snapshot: pd.DataFrame) -> None:
    db_path = tmp_path / "test.duckdb"
    sample = initial_snapshot.head(25).copy()
    snapshot_date = date(2026, 10, 8)
    import_snapshot(sample, snapshot_date, "base.xlsx", "hash-a", 0, db_path=db_path)
    assert active_snapshot_dates(db_path) == [snapshot_date]
    assert len(load_snapshot(snapshot_date, db_path)) == 25

    with pytest.raises(ValueError):
        import_snapshot(sample, snapshot_date, "base.xlsx", "hash-a", 0, db_path=db_path)

    replacement = sample.head(10).copy()
    import_snapshot(
        replacement,
        snapshot_date,
        "replacement.xlsx",
        "hash-b",
        0,
        replace=True,
        db_path=db_path,
    )
    assert len(load_snapshot(snapshot_date, db_path)) == 10
