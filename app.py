from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from src.constants import INITIAL_WORKBOOK
from src.importer import WorkbookReadError, read_snapshot
from src.metrics import filter_units
from src.storage import (
    active_snapshot_dates,
    import_snapshot,
    initialize_database,
    load_all_active,
    load_snapshot,
    sha256_bytes,
)
from src.transform import transform_snapshot, warning_counts
from src.ui import hero, inject_mrv_theme, sorted_unique
from src.validation import validate_structure
from src.views import enterprise, floors, overview, quality, velocity


st.set_page_config(
    page_title="Consumo e estoque imobiliário",
    page_icon="▰",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_mrv_theme()
initialize_database()


def import_payload(payload: bytes, file_name: str, snapshot_date: date, replace: bool) -> None:
    try:
        raw = read_snapshot(payload)
        validation = validate_structure(raw)
        if not validation.is_valid:
            for message in validation.errors:
                st.sidebar.error(message)
            if not validation.invalid_rows.empty:
                st.sidebar.download_button(
                    "Baixar registros inválidos",
                    validation.invalid_rows.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
                    file_name="registros_invalidos.csv",
                    mime="text/csv",
                )
            return

        transformed = transform_snapshot(raw)
        warnings = warning_counts(transformed)
        import_snapshot(
            transformed,
            snapshot_date,
            file_name,
            sha256_bytes(payload),
            sum(warnings.values()),
            replace=replace,
        )
        st.session_state["import_success"] = (
            f"Snapshot de {snapshot_date.strftime('%d/%m/%Y')} importado com "
            f"{len(transformed):,} unidades.".replace(",", ".")
        )
        st.rerun()
    except (WorkbookReadError, ValueError) as exc:
        st.sidebar.error(str(exc))
    except Exception as exc:
        st.sidebar.error(f"A importação não foi concluída: {exc}")


with st.sidebar:
    st.markdown("## Consumo & estoque")
    st.caption("Gestão comercial · painel local")

    page = st.radio(
        "Navegação",
        ["Visão geral", "Blocos e prumadas", "Detalhe do empreendimento", "Velocidade", "Qualidade dos dados"],
        label_visibility="collapsed",
    )

    with st.expander("Importar snapshot", expanded=not bool(active_snapshot_dates())):
        snapshot_input = st.date_input("Data do snapshot", value=date.today(), format="DD/MM/YYYY")
        uploaded = st.file_uploader("Arquivo Excel", type=["xlsx"])
        replace_snapshot = st.checkbox("Substituir snapshot existente")
        if st.button("Importar arquivo", type="primary", use_container_width=True, disabled=uploaded is None):
            import_payload(uploaded.getvalue(), uploaded.name, snapshot_input, replace_snapshot)
        if INITIAL_WORKBOOK.exists():
            st.caption("Ou use a base incluída no projeto.")
            if st.button("Carregar base inicial", use_container_width=True):
                import_payload(INITIAL_WORKBOOK.read_bytes(), INITIAL_WORKBOOK.name, snapshot_input, replace_snapshot)

    if "import_success" in st.session_state:
        st.success(st.session_state.pop("import_success"))


dates = active_snapshot_dates()
if not dates:
    hero("nenhum snapshot importado")
    st.markdown(
        """
        <div class="mrv-empty">
          <strong>Comece pela carga inicial</strong><br>
          Escolha a data do snapshot na barra lateral e use <em>Carregar base inicial</em>.
          A aplicação valida a planilha antes de persistir qualquer registro.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


with st.sidebar:
    st.divider()
    selected_date = st.selectbox(
        "Snapshot ativo",
        dates,
        format_func=lambda value: value.strftime("%d/%m/%Y"),
    )


frame = load_snapshot(selected_date)


def valid_state(key: str, options: list[str]) -> None:
    if key in st.session_state:
        st.session_state[key] = [value for value in st.session_state[key] if value in options]


with st.sidebar:
    st.markdown("### Filtros")
    city_options = sorted_unique(frame["city"])
    valid_state("filter_city", city_options)
    selected_cities = st.multiselect("Cidade", city_options, key="filter_city", placeholder="Selecione")

    cascade = filter_units(frame, cities=selected_cities)
    if page == "Blocos e prumadas":
        selected_enterprises = []
        selected_blocks = []
        st.caption("Escolha o empreendimento e o bloco diretamente no espelho de unidades.")
    else:
        enterprise_options = sorted_unique(cascade["enterprise_name"])
        valid_state("filter_enterprise", enterprise_options)
        selected_enterprises = st.multiselect("Empreendimento", enterprise_options, key="filter_enterprise", placeholder="Selecione")

        cascade = filter_units(cascade, enterprises=selected_enterprises)
        block_options = sorted_unique(cascade["block_name"])
        valid_state("filter_block", block_options)
        selected_blocks = st.multiselect("Bloco", block_options, key="filter_block", placeholder="Selecione")

        cascade = filter_units(cascade, blocks=selected_blocks)
    typology_options = sorted_unique(cascade["typology"])
    valid_state("filter_typology", typology_options)
    selected_typologies = st.multiselect("Tipologia", typology_options, key="filter_typology", placeholder="Selecione")

    status_options = sorted_unique(cascade["status_unit_normalized"])
    valid_state("filter_status", status_options)
    selected_statuses = st.multiselect("Status oficial", status_options, key="filter_status", placeholder="Selecione")
    include_missing_floor = st.checkbox("Incluir andar não informado", value=False)

    if st.button("Limpar filtros", use_container_width=True):
        for key in ["filter_city", "filter_enterprise", "filter_block", "filter_typology", "filter_status"]:
            st.session_state[key] = []
        st.rerun()


filtered = filter_units(
    frame,
    cities=selected_cities,
    enterprises=selected_enterprises,
    blocks=selected_blocks,
    typologies=selected_typologies,
    statuses=selected_statuses,
)

hero(selected_date.strftime("%d/%m/%Y"))

if page == "Visão geral":
    overview.render(filtered, selected_date)
elif page == "Blocos e prumadas":
    floors.render(filtered, selected_date, include_missing_floor)
elif page == "Detalhe do empreendimento":
    enterprise.render(filtered, selected_date)
elif page == "Velocidade":
    velocity.render(load_all_active())
else:
    quality.render(filtered, selected_date)
