from __future__ import annotations

import unicodedata

import pandas as pd

from .constants import KNOWN_STATUSES


def normalize_text(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().str.upper()


def _optional(frame: pd.DataFrame, column: str) -> pd.Series:
    if column in frame.columns:
        return frame[column]
    return pd.Series(pd.NA, index=frame.index, dtype="string")


def _integer_or_na(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    is_integer = numeric.isna() | (numeric.mod(1).abs() < 1e-9)
    return numeric.where(is_integer).round().astype("Int64")


def transform_snapshot(frame: pd.DataFrame) -> pd.DataFrame:
    status = normalize_text(frame["Status Unidade"])
    crm_raw = _optional(frame, "Status Unidade CRM")
    crm_status = normalize_text(crm_raw)
    floors = _integer_or_na(frame["Posição Vertical"])
    reported = _integer_or_na(frame["Pavimentos"])

    sold = status.eq("VENDIDO").fillna(False)
    crm_sold = crm_status.eq("VENDIDO").fillna(False)
    crm_present = crm_raw.notna() & crm_raw.astype("string").str.strip().ne("")

    result = pd.DataFrame(
        {
            "enterprise_id": frame["ID Empreendimento"].astype("string").str.strip(),
            "block_id": frame["ID Bloco"].astype("string").str.strip(),
            "unit_id": frame["ID da Unidade"].astype("string").str.strip(),
            "city": frame["Cidade"].astype("string").str.strip(),
            "enterprise_name": frame["Empreendimento"].astype("string").str.strip(),
            "block_name": frame["Bloco"].astype("string").str.strip(),
            "unit_name": frame["Unidade"].astype("string").str.strip(),
            "typology": _optional(frame, "Tipologia").astype("string").str.strip(),
            "subtypology": _optional(frame, "Subtipologia").astype("string").str.strip(),
            "status_unit_raw": frame["Status Unidade"].astype("string"),
            "status_unit_normalized": status,
            "status_crm_raw": crm_raw.astype("string"),
            "reported_floors": reported,
            "floor": floors,
            "is_sold": sold.astype(bool),
            "floor_missing": floors.isna(),
            "floor_above_reported": (floors > reported).fillna(False),
            "status_conflict": (crm_present & sold.ne(crm_sold)).fillna(False),
            "typology_missing": _optional(frame, "Tipologia").isna()
            | _optional(frame, "Tipologia").astype("string").str.strip().eq(""),
            "subtypology_missing": _optional(frame, "Subtipologia").isna()
            | _optional(frame, "Subtipologia").astype("string").str.strip().eq(""),
            "unknown_status": ~status.isin(KNOWN_STATUSES),
        }
    )
    return result


def warning_counts(frame: pd.DataFrame) -> dict[str, int]:
    return {
        "Andar não informado": int(frame["floor_missing"].sum()),
        "Pavimentos não informado": int(frame["reported_floors"].isna().sum()),
        "Andar superior aos pavimentos": int(frame["floor_above_reported"].sum()),
        "Divergência entre status oficial e CRM": int(frame["status_conflict"].sum()),
        "Tipologia não informada": int(frame["typology_missing"].sum()),
        "Subtipologia não informada": int(frame["subtypology_missing"].sum()),
        "Status não reconhecido": int(frame["unknown_status"].sum()),
    }


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return "_".join(normalized.lower().split())
