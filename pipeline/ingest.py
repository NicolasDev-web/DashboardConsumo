from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.constants import DB_PATH
from src.importer import read_snapshot
from src.metrics import portfolio_kpis, snapshot_timeline, transition_metrics
from src.storage import (
    active_snapshot_dates,
    import_history,
    import_snapshot,
    load_all_active,
    load_snapshot,
    sha256_bytes,
)
from src.transform import transform_snapshot, warning_counts
from src.validation import validate_structure


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "web" / "data-generated"

WEB_COLUMNS = [
    "enterprise_id",
    "block_id",
    "unit_id",
    "city",
    "enterprise_name",
    "block_name",
    "unit_name",
    "typology",
    "subtypology",
    "status_unit_raw",
    "status_unit_normalized",
    "status_crm_raw",
    "reported_floors",
    "floor",
    "is_sold",
    "floor_missing",
    "floor_above_reported",
    "status_conflict",
    "typology_missing",
    "subtypology_missing",
    "unknown_status",
]


def _json_value(value: Any) -> Any:
    if value is None or value is pd.NA:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if isinstance(value, np.generic):
        return value.item()
    return value


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [
        {key: _json_value(value) for key, value in row.items()}
        for row in frame.to_dict(orient="records")
    ]


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _snapshot_payload(frame: pd.DataFrame) -> dict[str, Any]:
    data = frame[WEB_COLUMNS].copy()
    rows = [
        [_json_value(value) for value in row]
        for row in data.itertuples(index=False, name=None)
    ]
    return {"schemaVersion": 1, "columns": WEB_COLUMNS, "rows": rows}


def export_web_data(
    output_dir: Path = DEFAULT_OUTPUT,
    db_path: Path = DB_PATH,
) -> dict[str, Any]:
    dates = active_snapshot_dates(db_path)
    if not dates:
        raise ValueError("Não existe nenhum snapshot ativo para publicar.")

    history = import_history(db_path)
    active_history = history.loc[history["status"].eq("ACTIVE")].copy()
    generated_at = datetime.now(timezone.utc).isoformat()
    snapshots: list[dict[str, Any]] = []

    for snapshot_date in dates:
        frame = load_snapshot(snapshot_date, db_path)
        file_name = f"snapshots/{snapshot_date.isoformat()}.json"
        _write_json(output_dir / file_name, _snapshot_payload(frame))

        source = active_history.loc[
            pd.to_datetime(active_history["snapshot_date"]).dt.date.eq(snapshot_date)
        ]
        source_row = source.iloc[0] if not source.empty else None
        snapshots.append(
            {
                "date": snapshot_date.isoformat(),
                "file": file_name,
                "rowCount": int(len(frame)),
                "kpis": portfolio_kpis(frame),
                "warnings": warning_counts(frame),
                "sourceFile": None if source_row is None else str(source_row["file_name"]),
                "sourceHash": None if source_row is None else str(source_row["file_sha256"]),
                "importedAt": None
                if source_row is None
                else _json_value(source_row["imported_at"]),
            }
        )

    all_snapshots = load_all_active(db_path)
    timeline = snapshot_timeline(all_snapshots)
    transitions = transition_metrics(all_snapshots)
    velocity = {
        "timeline": _records(timeline),
        "transitions": _records(transitions),
        "method": {
            "identity": "ID da Unidade",
            "saleRule": "Mudança de não vendido para VENDIDO entre duas fotos.",
            "monthlyRule": "Novas vendas divididas pelos dias entre fotos, multiplicadas por 30.",
            "coverage": "Unidades adicionadas ou removidas não contam como venda.",
        },
    }
    _write_json(output_dir / "velocity.json", velocity)

    manifest = {
        "schemaVersion": 1,
        "generatedAt": generated_at,
        "latestDate": dates[0].isoformat(),
        "snapshots": snapshots,
    }
    _write_json(output_dir / "manifest.json", manifest)
    return manifest


def ingest(
    workbook: Path,
    snapshot_date: date,
    replace: bool,
    db_path: Path = DB_PATH,
) -> str:
    content = workbook.read_bytes()
    raw = read_snapshot(content)
    validation = validate_structure(raw)
    if not validation.is_valid:
        details = "\n".join(f"- {message}" for message in validation.errors)
        raise ValueError(f"A planilha não passou na validação:\n{details}")
    transformed = transform_snapshot(raw)
    warnings = warning_counts(transformed)
    return import_snapshot(
        transformed,
        snapshot_date,
        workbook.name,
        sha256_bytes(content),
        sum(warnings.values()),
        replace=replace,
        db_path=db_path,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Valida um snapshot e prepara os dados consumidos pelo Next.js."
    )
    parser.add_argument("--file", type=Path, help="Arquivo .xlsx que será importado.")
    parser.add_argument("--date", type=date.fromisoformat, help="Data da foto em AAAA-MM-DD.")
    parser.add_argument("--replace", action="store_true", help="Substitui a foto da mesma data.")
    parser.add_argument(
        "--export-only",
        action="store_true",
        help="Apenas atualiza os arquivos web a partir do DuckDB local.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--database", type=Path, default=DB_PATH)
    return parser


def main() -> None:
    args = _parser().parse_args()
    if not args.export_only:
        if args.file is None or args.date is None:
            raise SystemExit("Use --file e --date, ou escolha --export-only.")
        run_id = ingest(args.file, args.date, args.replace, args.database)
        print(f"Snapshot importado: {run_id}")

    manifest = export_web_data(args.output, args.database)
    latest = manifest["snapshots"][0]
    print(
        f"Dados web preparados em {args.output}: "
        f"{latest['rowCount']:,} unidades na foto de {latest['date']}."
    )


if __name__ == "__main__":
    main()
