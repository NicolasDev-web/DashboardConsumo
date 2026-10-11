from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from src.constants import INITIAL_WORKBOOK, REQUIRED_COLUMNS
from src.importer import read_snapshot
from src.metrics import (
    block_sales,
    block_stack_sales,
    floor_band_comparison,
    floor_metrics,
    portfolio_kpis,
    progress_summary,
    stock_by_group,
    transition_metrics,
)
from src.storage import (
    active_snapshot_dates,
    import_history,
    import_snapshot,
    load_snapshot,
)
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


def test_unit_numbers_preserve_source_leading_zeroes(
    initial_snapshot: pd.DataFrame,
) -> None:
    leading_zeroes = initial_snapshot["unit_name"].str.fullmatch(r"0[1-9]", na=False)

    assert int(leading_zeroes.sum()) == 18
    assert set(initial_snapshot.loc[leading_zeroes, "unit_name"]) == {
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
    }


def test_quality_counts_reconcile_with_sdd(initial_snapshot: pd.DataFrame) -> None:
    counts = warning_counts(initial_snapshot)
    assert counts["Andar não informado"] == 281
    assert counts["Pavimentos não informado"] == 224
    assert counts["Andar superior aos pavimentos"] == 264
    assert counts["Divergência na classificação de venda (oficial × CRM)"] == 237


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


def test_validation_blocks_empty_snapshot() -> None:
    result = validate_structure(pd.DataFrame(columns=sorted(REQUIRED_COLUMNS)))

    assert not result.is_valid
    assert result.errors == ["A planilha não contém registros de unidades."]


def test_validation_blocks_empty_hierarchy_ids() -> None:
    frame = pd.DataFrame(
        {
            "ID Empreendimento": [None, "e"],
            "ID Bloco": ["b", "  "],
            "ID da Unidade": ["u1", "u2"],
            "Cidade": ["A", "A"],
            "Empreendimento": ["E", "E"],
            "Bloco": ["B", "B"],
            "Unidade": ["1", "2"],
            "Status Unidade": ["VENDIDO", "LANÇADO"],
            "Pavimentos": [2, 2],
            "Posição Vertical": [1, 1],
        }
    )

    result = validate_structure(frame)

    assert not result.is_valid
    assert len(result.invalid_rows) == 2
    assert "1 registro(s) sem ID Empreendimento." in result.errors
    assert "1 registro(s) sem ID Bloco." in result.errors


def test_validation_blocks_duplicated_required_header() -> None:
    frame = pd.DataFrame(
        {
            "ID Empreendimento": ["e"],
            "ID Bloco": ["b"],
            "ID da Unidade": ["u1"],
            "ID da Unidade.1": ["u2"],
            "Cidade": ["A"],
            "Empreendimento": ["E"],
            "Bloco": ["B"],
            "Unidade": ["1"],
            "Status Unidade": ["VENDIDO"],
            "Pavimentos": [2],
            "Posição Vertical": [1],
        }
    )

    result = validate_structure(frame)

    assert not result.is_valid
    assert result.errors == ["Colunas obrigatórias duplicadas: ID da Unidade"]


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


def test_failed_replacement_rolls_back_previous_snapshot(
    tmp_path, initial_snapshot: pd.DataFrame
) -> None:
    db_path = tmp_path / "rollback.duckdb"
    snapshot_date = date(2026, 10, 8)
    original = initial_snapshot.head(5).copy()
    import_snapshot(
        original,
        snapshot_date,
        "original.xlsx",
        "hash-original",
        0,
        db_path=db_path,
    )
    invalid_replacement = pd.concat(
        [original.head(1), original.head(1)], ignore_index=True
    )

    with pytest.raises(Exception):
        import_snapshot(
            invalid_replacement,
            snapshot_date,
            "invalid.xlsx",
            "hash-invalid",
            0,
            replace=True,
            db_path=db_path,
        )

    restored = load_snapshot(snapshot_date, db_path)
    history = import_history(db_path)
    assert set(restored["unit_id"]) == set(original["unit_id"])
    assert len(restored) == len(original)
    assert history[["file_name", "status"]].to_dict(orient="records") == [
        {"file_name": "original.xlsx", "status": "ACTIVE"}
    ]


def test_stock_groups_cover_all_unsold_units(initial_snapshot: pd.DataFrame) -> None:
    groups = stock_by_group(initial_snapshot).set_index("group")["units"]
    assert groups.to_dict() == {"Em comercialização": 6448, "Reservadas": 320, "Fora de venda": 3331}
    assert groups.sum() == 10099


def test_progress_summary_shows_stock_concentration(initial_snapshot: pd.DataFrame) -> None:
    summary = progress_summary(initial_snapshot).set_index("band")
    assert summary["enterprises"].sum() == 178
    assert summary["stock"].sum() == 10099
    low = summary.loc["Menos de 50% vendido"]
    assert int(low["enterprises"]) == 33
    assert int(low["stock"]) == 6816
    assert int(summary.loc["95% ou mais vendido", "enterprises"]) == 105


def test_floor_band_comparison_ignores_missing_floor(initial_snapshot: pd.DataFrame) -> None:
    comparison = floor_band_comparison(initial_snapshot)
    assert comparison["low"]["total"] == 39144
    assert comparison["high"]["total"] == 10983
    assert comparison["low"]["consumption"] > comparison["high"]["consumption"]


def test_block_sales_orders_by_percent_and_preserves_volume(initial_snapshot: pd.DataFrame) -> None:
    enterprise = initial_snapshot.loc[
        initial_snapshot["enterprise_name"].eq("ALAMEDA IMPERIAL")
    ]
    blocks = block_sales(enterprise)
    assert blocks.iloc[0]["consumption"] == pytest.approx(1.0)
    assert blocks.iloc[-1]["block_name"] == "BLOCO 01"
    assert int(blocks.iloc[-1]["sold"]) == 16
    assert int(blocks.iloc[-1]["total"]) == 20
    assert blocks.iloc[-1]["consumption"] == pytest.approx(0.8)
    assert int(blocks["sold"].sum()) == int(enterprise["is_sold"].sum())
    assert int(blocks["total"].sum()) == enterprise["unit_id"].nunique()


def test_block_stack_sales_reconciles_positioned_units(initial_snapshot: pd.DataFrame) -> None:
    enterprise = initial_snapshot.loc[
        initial_snapshot["enterprise_name"].eq("ALAMEDA IMPERIAL")
    ]
    stacks = block_stack_sales(enterprise)
    assert set(stacks["inferred_stack"].astype(int)) == {1, 2, 3, 4}
    assert int(stacks["total"].sum()) == 332
    assert int(stacks["sold"].sum()) == 316
    assert stacks["consumption"].between(0, 1).all()
