from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .constants import REQUIRED_COLUMNS


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    invalid_rows: pd.DataFrame = field(default_factory=pd.DataFrame)

    @property
    def is_valid(self) -> bool:
        return not self.errors


def validate_structure(frame: pd.DataFrame) -> ValidationResult:
    result = ValidationResult()
    missing = sorted(REQUIRED_COLUMNS.difference(frame.columns))
    if missing:
        result.errors.append("Colunas obrigatórias ausentes: " + ", ".join(missing))
        return result

    column_names = [str(column) for column in frame.columns]
    duplicated_required = sorted(
        column
        for column in REQUIRED_COLUMNS
        if column_names.count(column) > 1
        or any(
            candidate.startswith(f"{column}.")
            and candidate.removeprefix(f"{column}.").isdigit()
            for candidate in column_names
        )
    )
    if duplicated_required:
        result.errors.append(
            "Colunas obrigatórias duplicadas: " + ", ".join(duplicated_required)
        )
        return result

    if frame.empty:
        result.errors.append("A planilha não contém registros de unidades.")
        return result

    invalid_mask = pd.Series(False, index=frame.index)
    for column in ("ID Empreendimento", "ID Bloco", "ID da Unidade"):
        values = frame[column].astype("string").str.strip()
        empty_mask = values.isna() | values.eq("")
        invalid_mask |= empty_mask
        if empty_mask.any():
            result.errors.append(
                f"{int(empty_mask.sum()):,} registro(s) sem {column}.".replace(",", ".")
            )

    unit_ids = frame["ID da Unidade"].astype("string").str.strip()
    empty_mask = unit_ids.isna() | unit_ids.eq("")
    duplicate_mask = unit_ids.duplicated(keep=False) & ~empty_mask

    if duplicate_mask.any():
        duplicate_count = int(unit_ids[duplicate_mask].nunique())
        result.errors.append(
            f"{duplicate_count:,} ID(s) de unidade duplicado(s).".replace(",", ".")
        )

    invalid_mask |= duplicate_mask
    if invalid_mask.any():
        result.invalid_rows = frame.loc[invalid_mask].copy()
    return result

