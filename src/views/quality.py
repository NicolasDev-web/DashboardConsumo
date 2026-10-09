from __future__ import annotations

import pandas as pd
import streamlit as st

from ..exports import csv_bytes
from ..storage import import_history
from ..transform import warning_counts
from ..ui import br_int, empty_state, kpi_card, section


ISSUE_MASKS = {
    "Andar não informado": "floor_missing",
    "Pavimentos não informado": "reported_floors",
    "Andar superior aos pavimentos": "floor_above_reported",
    "Divergência entre status oficial e CRM": "status_conflict",
    "Tipologia não informada": "typology_missing",
    "Subtipologia não informada": "subtypology_missing",
    "Status não reconhecido": "unknown_status",
}


def render(frame: pd.DataFrame, snapshot_date) -> None:
    counts = warning_counts(frame)
    affected = pd.Series(False, index=frame.index)
    for label, column in ISSUE_MASKS.items():
        if column == "reported_floors":
            affected |= frame[column].isna()
        else:
            affected |= frame[column].fillna(False).astype(bool)

    cols = st.columns(3)
    with cols[0]:
        kpi_card("Erros bloqueantes", "0", "A carga ativa passou pela validação estrutural")
    with cols[1]:
        kpi_card("Registros com alerta", br_int(affected.sum()), "Uma linha pode ter mais de um alerta", "stock")
    with cols[2]:
        kpi_card("Tipos de alerta", br_int(sum(value > 0 for value in counts.values())), "Categorias presentes no snapshot", "consumption")

    section("Resumo dos alertas", "Alertas não alteram nem excluem registros do cálculo de consumo.")
    summary = pd.DataFrame(
        [{"tipo_problema": key, "registros": value, "proporcao": value / len(frame) if len(frame) else None} for key, value in counts.items()]
    ).sort_values("registros", ascending=False)
    display = summary.rename(columns={"tipo_problema": "Tipo de problema", "registros": "Registros", "proporcao": "Proporção"})
    display["Proporção"] = display["Proporção"] * 100
    st.dataframe(display, hide_index=True, use_container_width=True, column_config={"Proporção": st.column_config.NumberColumn(format="%.2f%%")})

    present_issues = [label for label, value in counts.items() if value > 0]
    if present_issues:
        selected = st.selectbox("Detalhar alerta", present_issues)
        column = ISSUE_MASKS[selected]
        mask = frame[column].isna() if column == "reported_floors" else frame[column].fillna(False).astype(bool)
        detail = frame.loc[mask, [
            "unit_id", "city", "enterprise_name", "block_name", "unit_name", "floor",
            "reported_floors", "status_unit_raw", "status_crm_raw", "typology", "subtypology",
        ]].copy()
        detail.insert(0, "snapshot_date", snapshot_date)
        st.dataframe(detail, hide_index=True, use_container_width=True)
        st.download_button("Exportar registros com problema", csv_bytes(detail), file_name=f"qualidade_{snapshot_date}.csv", mime="text/csv")
    else:
        empty_state("Nenhum alerta", "O snapshot atual não apresenta problemas de qualidade catalogados.")

    section("Histórico de importações", "Execuções substituídas permanecem registradas para auditoria.")
    history = import_history()
    if not history.empty:
        history["file_sha256"] = history["file_sha256"].str.slice(0, 12) + "…"
        st.dataframe(history, hide_index=True, use_container_width=True)
