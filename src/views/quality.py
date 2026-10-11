from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from ..exports import csv_bytes
from ..storage import import_history
from ..transform import warning_counts
from ..ui import br_int, br_pct, empty_state, insight, section, strong


ISSUE_MASKS = {
    "Andar não informado": "floor_missing",
    "Pavimentos não informado": "reported_floors",
    "Andar superior aos pavimentos": "floor_above_reported",
    "Divergência entre status oficial e CRM": "status_conflict",
    "Tipologia não informada": "typology_missing",
    "Subtipologia não informada": "subtypology_missing",
    "Status não reconhecido": "unknown_status",
}


DETAIL_LABELS = {
    "city": "Cidade", "enterprise_name": "Empreendimento", "block_name": "Bloco", "unit_name": "Unidade",
    "floor": "Andar", "reported_floors": "Pavimentos", "status_unit_raw": "Status oficial",
    "status_crm_raw": "Status CRM", "typology": "Tipologia", "subtypology": "Subtipologia",
}


def _issue_mask(frame: pd.DataFrame, column: str) -> pd.Series:
    if column == "reported_floors":
        return frame[column].isna()
    return frame[column].fillna(False).astype(bool)


def render(frame: pd.DataFrame, snapshot_date) -> None:
    if frame.empty:
        empty_state("Nenhuma unidade no recorte", "Remova alguns filtros para avaliar a qualidade dos dados.")
        return

    counts = warning_counts(frame)
    affected = pd.Series(False, index=frame.index)
    for column in ISSUE_MASKS.values():
        affected |= _issue_mask(frame, column)
    clean_share = 1 - affected.sum() / len(frame)
    present = {label: value for label, value in sorted(counts.items(), key=lambda item: -item[1]) if value > 0}

    if not present:
        insight(f"{strong('Todos os registros')} passaram sem nenhum alerta.", tone="positive")
    else:
        top_label, top_count = next(iter(present.items()))
        insight(
            f"{strong(br_pct(clean_share))} dos registros não têm nenhum alerta. "
            "Os alertas não mudam os totais de vendas: nenhum registro é corrigido ou excluído.",
            f"O ponto mais frequente é {strong(top_label.lower())} ({html.escape(br_int(top_count))} registros). "
            f"Ao todo, {html.escape(br_int(affected.sum()))} registros têm pelo menos um alerta.",
            tone="positive" if clean_share >= 0.95 else "attention",
        )

    if present:
        section("O que precisa de conferência", "Escolha um tipo de alerta para ver e exportar os registros.")
        summary = pd.DataFrame(
            [{"Tipo de alerta": label, "Registros": value, "Do total": br_pct(value / len(frame), 2)} for label, value in present.items()]
        )
        st.dataframe(summary, hide_index=True, use_container_width=True)
        selected = st.selectbox("Ver registros de", list(present))
        detail = frame.loc[_issue_mask(frame, ISSUE_MASKS[selected]), [
            "unit_id", "city", "enterprise_name", "block_name", "unit_name", "floor",
            "reported_floors", "status_unit_raw", "status_crm_raw", "typology", "subtypology",
        ]].copy()
        st.dataframe(
            detail.drop(columns="unit_id").rename(columns=DETAIL_LABELS),
            hide_index=True, use_container_width=True,
        )
        detail.insert(0, "snapshot_date", snapshot_date)
        st.download_button("Exportar registros com alerta", csv_bytes(detail), file_name=f"qualidade_{snapshot_date}.csv", mime="text/csv")

    with st.expander("Ver histórico de importações"):
        st.caption("Importações substituídas continuam registradas para auditoria.")
        history = import_history()
        if not history.empty:
            history["file_sha256"] = history["file_sha256"].str.slice(0, 12) + "…"
            st.dataframe(history, hide_index=True, use_container_width=True)
