from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import pandas as pd

from .constants import HEADER_ROW, SHEET_NAME


class WorkbookReadError(ValueError):
    """Erro legível ao usuário durante a leitura do workbook."""


def read_snapshot(source: str | Path | bytes | BinaryIO) -> pd.DataFrame:
    """Lê a aba POC usando a segunda linha como cabeçalho."""
    try:
        payload = BytesIO(source) if isinstance(source, bytes) else source
        # Calamine lê o workbook inteiro em poucos segundos; o fallback mantém
        # compatibilidade em ambientes nos quais a dependência ainda não exista.
        try:
            workbook = pd.ExcelFile(payload, engine="calamine")
        except ImportError:
            if hasattr(payload, "seek"):
                payload.seek(0)
            workbook = pd.ExcelFile(payload, engine="openpyxl")
        if SHEET_NAME not in workbook.sheet_names:
            raise WorkbookReadError(f"A aba '{SHEET_NAME}' é obrigatória.")
        frame = pd.read_excel(
            workbook,
            sheet_name=SHEET_NAME,
            header=HEADER_ROW,
            dtype={
                "ID Empreendimento": "string",
                "ID Bloco": "string",
                "ID da Unidade": "string",
                # O número da unidade é também um identificador de exibição.
                # Forçar texto preserva valores como 01–09, usados na ficha.
                "Unidade": "string",
            },
        )
        frame = frame.dropna(how="all").reset_index(drop=True)
        return frame
    except WorkbookReadError:
        raise
    except Exception as exc:
        raise WorkbookReadError(
            "Não foi possível ler o arquivo. Confirme que ele é um .xlsx válido."
        ) from exc
