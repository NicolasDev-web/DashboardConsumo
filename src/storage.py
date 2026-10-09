from __future__ import annotations

import hashlib
import uuid
from contextlib import contextmanager
from datetime import date
from pathlib import Path

import duckdb
import pandas as pd

from .constants import DB_PATH


UNIT_COLUMNS = [
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


@contextmanager
def connect(db_path: Path = DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(db_path))
    try:
        yield connection
    finally:
        connection.close()


def initialize_database(db_path: Path = DB_PATH) -> None:
    with connect(db_path) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS import_runs (
                run_id VARCHAR PRIMARY KEY,
                snapshot_date DATE NOT NULL,
                file_name VARCHAR NOT NULL,
                file_sha256 VARCHAR NOT NULL,
                imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                row_count INTEGER NOT NULL,
                warning_count INTEGER NOT NULL,
                status VARCHAR NOT NULL,
                replaced_run_id VARCHAR
            );

            CREATE TABLE IF NOT EXISTS unit_snapshots (
                run_id VARCHAR NOT NULL,
                snapshot_date DATE NOT NULL,
                enterprise_id VARCHAR,
                block_id VARCHAR,
                unit_id VARCHAR NOT NULL,
                city VARCHAR,
                enterprise_name VARCHAR,
                block_name VARCHAR,
                unit_name VARCHAR,
                typology VARCHAR,
                subtypology VARCHAR,
                status_unit_raw VARCHAR,
                status_unit_normalized VARCHAR,
                status_crm_raw VARCHAR,
                reported_floors INTEGER,
                floor INTEGER,
                is_sold BOOLEAN,
                floor_missing BOOLEAN,
                floor_above_reported BOOLEAN,
                status_conflict BOOLEAN,
                typology_missing BOOLEAN,
                subtypology_missing BOOLEAN,
                unknown_status BOOLEAN,
                UNIQUE(snapshot_date, unit_id)
            );
            """
        )


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def active_snapshot_dates(db_path: Path = DB_PATH) -> list[date]:
    initialize_database(db_path)
    with connect(db_path) as con:
        rows = con.execute(
            """
            SELECT DISTINCT snapshot_date
            FROM import_runs
            WHERE status = 'ACTIVE'
            ORDER BY snapshot_date DESC
            """
        ).fetchall()
    return [row[0] for row in rows]


def import_snapshot(
    frame: pd.DataFrame,
    snapshot_date: date,
    file_name: str,
    file_hash: str,
    warning_count: int,
    replace: bool = False,
    db_path: Path = DB_PATH,
) -> str:
    initialize_database(db_path)
    run_id = str(uuid.uuid4())
    payload = frame[UNIT_COLUMNS].copy()
    payload.insert(0, "snapshot_date", pd.Timestamp(snapshot_date))
    payload.insert(0, "run_id", run_id)

    with connect(db_path) as con:
        existing = con.execute(
            """
            SELECT run_id FROM import_runs
            WHERE snapshot_date = ? AND status = 'ACTIVE'
            """,
            [snapshot_date],
        ).fetchone()
        if existing and not replace:
            raise ValueError(
                "Já existe um snapshot ativo nessa data. Marque a opção de substituição."
            )

        con.execute("BEGIN TRANSACTION")
        try:
            replaced_id = existing[0] if existing else None
            if replaced_id:
                con.execute(
                    "UPDATE import_runs SET status = 'REPLACED' WHERE run_id = ?",
                    [replaced_id],
                )
                con.execute(
                    "DELETE FROM unit_snapshots WHERE run_id = ?", [replaced_id]
                )

            con.execute(
                """
                INSERT INTO import_runs (
                    run_id, snapshot_date, file_name, file_sha256,
                    row_count, warning_count, status, replaced_run_id
                ) VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
                """,
                [
                    run_id,
                    snapshot_date,
                    file_name,
                    file_hash,
                    len(payload),
                    warning_count,
                    replaced_id,
                ],
            )
            con.register("snapshot_payload", payload)
            con.execute(
                """
                INSERT INTO unit_snapshots
                SELECT * FROM snapshot_payload
                """
            )
            con.unregister("snapshot_payload")
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
    return run_id


def load_snapshot(snapshot_date: date, db_path: Path = DB_PATH) -> pd.DataFrame:
    initialize_database(db_path)
    with connect(db_path) as con:
        return con.execute(
            """
            SELECT u.* EXCLUDE (run_id), r.file_name, r.imported_at
            FROM unit_snapshots u
            JOIN import_runs r USING (run_id)
            WHERE u.snapshot_date = ? AND r.status = 'ACTIVE'
            """,
            [snapshot_date],
        ).df()


def load_all_active(db_path: Path = DB_PATH) -> pd.DataFrame:
    initialize_database(db_path)
    with connect(db_path) as con:
        return con.execute(
            """
            SELECT u.* EXCLUDE (run_id)
            FROM unit_snapshots u
            JOIN import_runs r USING (run_id)
            WHERE r.status = 'ACTIVE'
            ORDER BY snapshot_date
            """
        ).df()


def import_history(db_path: Path = DB_PATH) -> pd.DataFrame:
    initialize_database(db_path)
    with connect(db_path) as con:
        return con.execute(
            """
            SELECT snapshot_date, file_name, imported_at, row_count,
                   warning_count, status, file_sha256
            FROM import_runs
            ORDER BY imported_at DESC
            """
        ).df()

