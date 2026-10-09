from __future__ import annotations

import numpy as np
import pandas as pd


def portfolio_kpis(frame: pd.DataFrame) -> dict[str, float | int | None]:
    total = int(frame["unit_id"].nunique())
    sold = int(frame.loc[frame["is_sold"], "unit_id"].nunique()) if total else 0
    stock = total - sold
    return {
        "total": total,
        "sold": sold,
        "stock": stock,
        "consumption": sold / total if total else None,
    }


def grouped_metrics(frame: pd.DataFrame, group_cols: str | list[str]) -> pd.DataFrame:
    columns = [group_cols] if isinstance(group_cols, str) else group_cols
    if frame.empty:
        return pd.DataFrame(columns=columns + ["total", "sold", "stock", "consumption"])

    result = (
        frame.groupby(columns, dropna=False)
        .agg(total=("unit_id", "nunique"), sold=("is_sold", "sum"))
        .reset_index()
    )
    result["sold"] = result["sold"].astype(int)
    result["stock"] = result["total"] - result["sold"]
    result["consumption"] = result["sold"].div(result["total"].replace(0, np.nan))
    return result


def stock_by_status(frame: pd.DataFrame) -> pd.DataFrame:
    unsold = frame.loc[~frame["is_sold"]]
    result = grouped_metrics(unsold, "status_unit_normalized")
    stock_total = int(result["total"].sum())
    result = result.rename(columns={"total": "units"})
    result["share"] = result["units"].div(stock_total) if stock_total else np.nan
    return result[["status_unit_normalized", "units", "share"]].sort_values(
        "units", ascending=False
    )


def floor_metrics(frame: pd.DataFrame, include_missing: bool = False) -> pd.DataFrame:
    working = frame.copy()
    if not include_missing:
        working = working.loc[working["floor"].notna()]
    result = grouped_metrics(working, "floor")
    return result.sort_values("floor", na_position="last")


def with_inferred_shaft(frame: pd.DataFrame) -> pd.DataFrame:
    """Adiciona a prumada inferida sem alterar a dimensão oficial de andar.

    A base não possui uma coluna de prumada. A regra aprovada usa os dois
    últimos dígitos de ``unit_name`` somente quando ``floor`` está informado.
    Valores não numéricos permanecem sem prumada, sem tentativa de correção.
    """

    result = frame.copy()
    unit_number = pd.to_numeric(result["unit_name"], errors="coerce")
    eligible = result["floor"].notna() & unit_number.notna()
    result["inferred_shaft"] = unit_number.mod(100).where(eligible).astype("Int64")
    return result


def inferred_shaft_cells(frame: pd.DataFrame) -> pd.DataFrame:
    """Agrupa unidades por andar e prumada preservando células conflitantes."""

    working = with_inferred_shaft(frame)
    working = working.loc[working["floor"].notna() & working["inferred_shaft"].notna()].copy()
    columns = [
        "floor",
        "inferred_shaft",
        "unit_ids",
        "unit_names",
        "statuses",
        "sold_values",
        "unit_count",
        "collision",
    ]
    if working.empty:
        return pd.DataFrame(columns=columns)

    cells = (
        working.groupby(["floor", "inferred_shaft"], dropna=False, sort=True)
        .agg(
            unit_ids=("unit_id", lambda values: tuple(values.astype(str))),
            unit_names=("unit_name", lambda values: tuple(values.astype(str))),
            statuses=("status_unit_normalized", lambda values: tuple(values.astype(str))),
            sold_values=("is_sold", lambda values: tuple(bool(value) for value in values)),
            unit_count=("unit_id", "nunique"),
        )
        .reset_index()
    )
    cells["collision"] = cells["unit_count"].gt(1)
    return cells[columns]


def filter_units(
    frame: pd.DataFrame,
    cities: list[str] | None = None,
    enterprises: list[str] | None = None,
    blocks: list[str] | None = None,
    typologies: list[str] | None = None,
    statuses: list[str] | None = None,
) -> pd.DataFrame:
    result = frame
    for column, values in [
        ("city", cities),
        ("enterprise_name", enterprises),
        ("block_name", blocks),
        ("typology", typologies),
        ("status_unit_normalized", statuses),
    ]:
        if values:
            result = result.loc[result[column].isin(values)]
    return result.copy()


def snapshot_timeline(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    return grouped_metrics(frame, "snapshot_date").sort_values("snapshot_date")


def transition_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    dates = sorted(pd.to_datetime(frame["snapshot_date"].dropna().unique()))
    rows: list[dict] = []
    for previous_date, current_date in zip(dates, dates[1:]):
        previous = frame.loc[
            pd.to_datetime(frame["snapshot_date"]).eq(previous_date), ["unit_id", "is_sold"]
        ].set_index("unit_id")
        current = frame.loc[
            pd.to_datetime(frame["snapshot_date"]).eq(current_date), ["unit_id", "is_sold"]
        ].set_index("unit_id")

        common = previous.index.intersection(current.index)
        prev_common = previous.loc[common, "is_sold"].astype(bool)
        curr_common = current.loc[common, "is_sold"].astype(bool)
        new_sales = int((~prev_common & curr_common).sum())
        reversals = int((prev_common & ~curr_common).sum())
        elapsed = int((current_date - previous_date).days)
        current_kpis = portfolio_kpis(
            frame.loc[pd.to_datetime(frame["snapshot_date"]).eq(current_date)]
        )
        previous_kpis = portfolio_kpis(
            frame.loc[pd.to_datetime(frame["snapshot_date"]).eq(previous_date)]
        )
        rows.append(
            {
                "previous_date": previous_date.date(),
                "snapshot_date": current_date.date(),
                "days": elapsed,
                "new_sales": new_sales,
                "reversals": reversals,
                "net_sales": new_sales - reversals,
                "monthly_velocity": new_sales / elapsed * 30 if elapsed > 0 else np.nan,
                "consumption_change_pp": (
                    current_kpis["consumption"] - previous_kpis["consumption"]
                )
                * 100,
                "added_units": int(current.index.difference(previous.index).size),
                "removed_units": int(previous.index.difference(current.index).size),
            }
        )
    return pd.DataFrame(rows)
