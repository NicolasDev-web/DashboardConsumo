from __future__ import annotations

import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..constants import COLORS
from ..exports import csv_bytes
from ..metrics import grouped_metrics, portfolio_kpis
from ..ui import br_int, br_pct, empty_state, kpi_card, plotly_layout, section, sorted_unique


STATUS_CODES = {
    "VENDIDO": "VD",
    "EXCLUSIVO PLATAFORMA": "EX",
    "NÃO LANÇADO": "NL",
    "PRÉ VENDA": "PV",
    "PERMUTADO": "PM",
    "BLOQUEADO": "BL",
    "RESERVADO COM CONTRATO PRE ATIVO": "RC",
    "LANÇADO": "LA",
    "RESERVA PARA PERMUTA": "RP",
    "RESERVADO": "RE",
}


def infer_stack(frame: pd.DataFrame) -> pd.DataFrame:
    """Infere prumada pelo sufixo da unidade sem inferir ou corrigir o andar."""
    result = frame.copy()
    unit_number = pd.to_numeric(result["unit_name"], errors="coerce")
    stack = unit_number.mod(100).astype("Int64")
    result["inferred_stack"] = stack.where(
        result["floor"].notna() & stack.between(1, 12)
    )
    return result


def _block_summary(frame: pd.DataFrame) -> pd.DataFrame:
    summary = grouped_metrics(frame, ["block_id", "block_name"])
    summary = summary.sort_values(["stock", "total"], ascending=False).reset_index(drop=True)
    duplicates = summary["block_name"].duplicated(keep=False)
    summary["block_label"] = summary["block_name"]
    summary.loc[duplicates, "block_label"] = (
        summary.loc[duplicates, "block_name"]
        + " · "
        + summary.loc[duplicates, "block_id"].astype("string").str.slice(0, 4)
    )
    return summary


def _compact_kpis(frame: pd.DataFrame, context: str) -> None:
    kpis = portfolio_kpis(frame)
    columns = st.columns(4)
    with columns[0]:
        kpi_card("Unidades", br_int(kpis["total"]), context)
    with columns[1]:
        kpi_card("Vendidas", br_int(kpis["sold"]), "Status oficial igual a VENDIDO")
    with columns[2]:
        kpi_card("Estoque não vendido", br_int(kpis["stock"]), "Todos os demais status", "stock")
    with columns[3]:
        kpi_card("Consumo", br_pct(kpis["consumption"]), "Vendidas sobre o total", "consumption")


def _comparison_heatmap(frame: pd.DataFrame, summary: pd.DataFrame) -> None:
    top_limit = min(12, len(summary))
    visible_labels = summary.head(top_limit)["block_label"].tolist()
    visible_ids = summary.head(top_limit)["block_id"].tolist()
    stack_detail = grouped_metrics(
        frame.loc[frame["block_id"].isin(visible_ids) & frame["inferred_stack"].notna()],
        ["block_id", "block_name", "inferred_stack"],
    )
    label_map = summary.set_index("block_id")["block_label"]
    stack_detail["block_label"] = stack_detail["block_id"].map(label_map)
    stacks = sorted(stack_detail["inferred_stack"].dropna().astype(int).unique())
    if not stacks:
        empty_state(
            "Sem prumadas comparáveis",
            "Os blocos deste empreendimento não possuem andar e posição inferida válidos.",
        )
        return

    index = pd.MultiIndex.from_product(
        [visible_labels, stacks], names=["block_label", "inferred_stack"]
    )
    grid = stack_detail.set_index(["block_label", "inferred_stack"]).reindex(index)
    stock = grid["stock"].fillna(0).to_numpy().reshape(len(visible_labels), len(stacks))
    total = grid["total"].fillna(0).to_numpy().reshape(len(visible_labels), len(stacks))
    sold = grid["sold"].fillna(0).to_numpy().reshape(len(visible_labels), len(stacks))
    consumption = grid["consumption"].to_numpy().reshape(len(visible_labels), len(stacks))
    text = [["" if value == 0 else str(int(value)) for value in row] for row in stock]
    customdata = [
        [
            [total[row][column], sold[row][column], stock[row][column], consumption[row][column]]
            for column in range(len(stacks))
        ]
        for row in range(len(visible_labels))
    ]

    figure = go.Figure(
        go.Heatmap(
            z=stock,
            x=[f"{stack:02d}" for stack in stacks],
            y=visible_labels,
            text=text,
            texttemplate="%{text}",
            customdata=customdata,
            colorscale=[[0, "#F4F7F5"], [0.01, "#DCE7E1"], [1, COLORS["green_900"]]],
            colorbar={"title": "Estoque"},
            hovertemplate=(
                "%{y}<br>Prumada inferida %{x}<br>Estoque %{customdata[2]:.0f}"
                "<br>Vendidas %{customdata[1]:.0f}<br>Total %{customdata[0]:.0f}"
                "<br>Consumo %{customdata[3]:.1%}<extra></extra>"
            ),
            hoverongaps=False,
        )
    )
    figure.update_xaxes(title="Prumada inferida", side="top")
    figure.update_yaxes(autorange="reversed", title="")
    plotly_layout(
        figure,
        height=max(300, len(visible_labels) * 42 + 110),
        margin={"l": 12, "r": 16, "t": 62, "b": 20},
    )
    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
    if len(summary) > top_limit:
        st.caption(
            f"O mapa mostra os {top_limit} blocos com maior estoque. "
            "Use a busca abaixo para abrir qualquer outro bloco."
        )


def _unit_cells(block: pd.DataFrame, detailed: bool) -> pd.DataFrame:
    comparable = block.loc[
        block["floor"].notna() & block["inferred_stack"].notna()
    ].copy()
    if comparable.empty:
        return pd.DataFrame()

    rows: list[dict] = []
    for (floor, stack), group in comparable.groupby(["floor", "inferred_stack"], sort=True):
        units = group["unit_name"].astype("string").tolist()
        statuses = group["status_unit_normalized"].astype("string").fillna("NÃO INFORMADO").tolist()
        sold = bool(group["is_sold"].all())
        collision = len(group) > 1
        prefix = "!" if collision else ("✓" if sold else "•")
        unit_text = str(units[0]) if len(units) == 1 else f"{units[0]} +{len(units) - 1}"
        status_codes = "/".join(dict.fromkeys(STATUS_CODES.get(status, "OT") for status in statuses))
        label = f"{prefix} {unit_text}"
        if detailed:
            label += f"<br>{status_codes}"
        rows.append(
            {
                "floor": int(floor),
                "stack": int(stack),
                "label": label,
                "units": ", ".join(units),
                "statuses": ", ".join(dict.fromkeys(statuses)),
                "typologies": ", ".join(dict.fromkeys(group["typology"].dropna().astype(str).tolist())),
                "sold": sold,
                "collision": collision,
                "row_indices": group.index.tolist(),
            }
        )
    return pd.DataFrame(rows).sort_values(["floor", "stack"], ascending=[False, True]).reset_index(drop=True)


def _building_grid(block: pd.DataFrame, detailed: bool, chart_key: str) -> list[int]:
    cells = _unit_cells(block, detailed)
    if cells.empty:
        empty_state(
            "Sem unidades posicionáveis",
            "Este bloco não possui combinação válida de andar e prumada inferida.",
        )
        return []

    max_stack = int(cells["stack"].max())
    marker_size = 48 if max_stack <= 4 else (40 if max_stack <= 8 else 30)
    if detailed:
        marker_size += 4
    text_size = 11 if max_stack <= 8 else 9

    fill_colors = [COLORS["green_900"] if sold else "#DCE2DF" for sold in cells["sold"]]
    line_colors = [COLORS["orange"] if conflict else "#A8B6B0" for conflict in cells["collision"]]
    line_widths = [4 if conflict else 1 for conflict in cells["collision"]]
    text_colors = ["#FFFFFF" if sold else COLORS["text"] for sold in cells["sold"]]

    figure = go.Figure(
        go.Scatter(
            x=cells["stack"],
            y=cells["floor"],
            mode="markers+text",
            text=cells["label"],
            textposition="middle center",
            textfont={"size": text_size, "color": text_colors},
            marker={
                "symbol": "square",
                "size": marker_size,
                "color": fill_colors,
                "line": {"color": line_colors, "width": line_widths},
            },
            customdata=cells[["units", "statuses", "typologies", "collision"]],
            hovertemplate=(
                "Unidade(s) %{customdata[0]}<br>Andar %{y:.0f}<br>Prumada inferida %{x:02d}"
                "<br>Status %{customdata[1]}<br>Tipologia %{customdata[2]}"
                "<br>Conflito de posição: %{customdata[3]}<extra></extra>"
            ),
            selected={"marker": {"opacity": 1}},
            unselected={"marker": {"opacity": 0.58}},
        )
    )
    floors = sorted(cells["floor"].unique())
    stacks = list(range(1, int(cells["stack"].max()) + 1))
    figure.update_xaxes(
        title="Prumada inferida",
        tickmode="array",
        tickvals=stacks,
        ticktext=[f"{value:02d}" for value in stacks],
        side="top",
        range=[0.45, max(stacks) + 0.55],
        showgrid=True,
        gridcolor="#E1E9E5",
        fixedrange=True,
    )
    figure.update_yaxes(
        title="Andar",
        tickmode="array",
        tickvals=floors,
        range=[min(floors) - 0.6, max(floors) + 0.6],
        showgrid=True,
        gridcolor="#E1E9E5",
        fixedrange=True,
    )
    figure.update_layout(clickmode="event+select")
    plotly_layout(
        figure,
        height=min(860, max(430, len(floors) * 38 + 150)),
        margin={"l": 16, "r": 16, "t": 70, "b": 30},
    )
    event = st.plotly_chart(
        figure,
        use_container_width=True,
        config={"displayModeBar": False, "scrollZoom": False},
        on_select="rerun",
        selection_mode="points",
        key=chart_key,
    )
    points = event.selection.points if event and hasattr(event, "selection") else []
    if not points:
        return []
    point_index = points[0].get("point_index", points[0].get("pointIndex"))
    if point_index is None or point_index >= len(cells):
        return []
    return cells.iloc[int(point_index)]["row_indices"]


def _unit_detail(block: pd.DataFrame, selected_indices: list[int]) -> None:
    if not selected_indices:
        st.caption("Selecione uma célula do espelho para consultar a unidade.")
        return
    detail = block.loc[selected_indices].copy()
    conflict = len(detail) > 1
    title = "Posição com mais de uma unidade" if conflict else f"Unidade {detail.iloc[0]['unit_name']}"
    if conflict:
        st.warning(
            "Esta célula possui mais de uma unidade para o mesmo bloco, andar e prumada inferida. "
            "Os registros foram preservados sem correção automática."
        )
    section(title)
    display = detail[[
        "unit_name", "floor", "inferred_stack", "typology", "subtypology",
        "status_unit_normalized", "status_crm_raw",
    ]].rename(
        columns={
            "unit_name": "Unidade",
            "floor": "Andar",
            "inferred_stack": "Prumada inferida",
            "typology": "Tipologia",
            "subtypology": "Subtipologia",
            "status_unit_normalized": "Status oficial",
            "status_crm_raw": "Status CRM",
        }
    )
    st.dataframe(display, hide_index=True, use_container_width=True)


def render(frame: pd.DataFrame, snapshot_date, include_missing: bool) -> None:
    if frame.empty:
        empty_state(
            "Nenhuma unidade no recorte",
            "Remova alguns filtros globais para visualizar os empreendimentos.",
        )
        return

    working = infer_stack(frame)
    enterprises = sorted_unique(working["enterprise_name"])
    selected_enterprise = st.selectbox(
        "Escolha o empreendimento",
        enterprises,
        index=None,
        placeholder="Digite para buscar um empreendimento",
        key="stacks_enterprise",
    )
    if not selected_enterprise:
        section(
            "Comece pelo empreendimento",
            "A seleção limita a análise aos blocos, prumadas e unidades que pertencem ao mesmo contexto.",
        )
        empty_state(
            "Nenhum empreendimento selecionado",
            "Use a busca acima. Depois, compare os blocos e abra o espelho de unidades.",
        )
        return

    enterprise = working.loc[working["enterprise_name"].eq(selected_enterprise)].copy()
    city = enterprise["city"].dropna().astype(str).iloc[0] if enterprise["city"].notna().any() else "Cidade não informada"
    st.markdown(
        f"<div class='mrv-breadcrumb'>{html.escape(city)} <span>/</span> "
        f"{html.escape(selected_enterprise)}</div>",
        unsafe_allow_html=True,
    )
    _compact_kpis(enterprise, selected_enterprise)

    summary = _block_summary(enterprise)
    section(
        "Compare os blocos",
        "O mapa mostra onde o estoque se concentra por bloco e prumada. Números maiores indicam mais unidades não vendidas.",
    )
    total_stock = int(summary["stock"].sum())
    leading = summary.head(2)
    if total_stock and not leading.empty:
        share = leading["stock"].sum() / total_stock
        names = " e ".join(leading["block_name"].tolist())
        st.info(f"{names} concentram {br_pct(share)} do estoque não vendido deste empreendimento.")

    selected_from_ranking: str | None = None
    left, right = st.columns([0.38, 0.62], gap="large")
    with left:
        ranking = summary[["block_label", "total", "stock", "consumption"]].copy()
        ranking["consumption"] *= 100
        ranking = ranking.rename(
            columns={
                "block_label": "Bloco",
                "total": "Unidades",
                "stock": "Estoque",
                "consumption": "Consumo",
            }
        )
        ranking_event = st.dataframe(
            ranking,
            hide_index=True,
            use_container_width=True,
            height=min(480, 44 + len(ranking) * 35),
            on_select="rerun",
            selection_mode="single-row",
            key=f"block_ranking_{selected_enterprise}",
            column_config={
                "Consumo": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100)
            },
        )
        if ranking_event.selection.rows:
            selected_from_ranking = ranking.iloc[ranking_event.selection.rows[0]]["Bloco"]
        st.caption("Selecione uma linha para abrir o bloco no espelho.")
    with right:
        _comparison_heatmap(enterprise, summary)

    section(
        "Abra o espelho do bloco",
        "Andares aparecem nas linhas e prumadas inferidas nas colunas. Clique em uma célula para consultar a unidade.",
    )
    block_options = summary["block_label"].tolist()
    if st.session_state.get("_stacks_enterprise_active") != selected_enterprise:
        st.session_state.pop("stacks_block", None)
        st.session_state["_stacks_enterprise_active"] = selected_enterprise
    if selected_from_ranking in block_options:
        st.session_state["stacks_block"] = selected_from_ranking
    if st.session_state.get("stacks_block") not in block_options:
        st.session_state.pop("stacks_block", None)
    selected_label = st.selectbox("Bloco", block_options, key="stacks_block")
    selected_row = summary.loc[summary["block_label"].eq(selected_label)].iloc[0]
    block = enterprise.loc[enterprise["block_id"].eq(selected_row["block_id"])].copy()
    st.markdown(
        f"<div class='mrv-breadcrumb'>{html.escape(city)} <span>/</span> "
        f"{html.escape(selected_enterprise)} <span>/</span> "
        f"{html.escape(str(selected_row['block_name']))}</div>",
        unsafe_allow_html=True,
    )
    _compact_kpis(block, str(selected_row["block_name"]))

    missing_floor = int(block["floor"].isna().sum())
    invalid_stack = int((block["floor"].notna() & block["inferred_stack"].isna()).sum())
    collision_count = int(
        block.loc[block["floor"].notna() & block["inferred_stack"].notna()]
        .duplicated(["floor", "inferred_stack"], keep=False)
        .sum()
    )
    if missing_floor or invalid_stack or collision_count:
        messages = []
        if missing_floor:
            messages.append(f"{br_int(missing_floor)} sem andar")
        if invalid_stack:
            messages.append(f"{br_int(invalid_stack)} sem prumada válida")
        if collision_count:
            messages.append(f"{br_int(collision_count)} unidades em posições conflitantes")
        st.warning("Atenção aos dados deste bloco: " + "; ".join(messages) + ".")

    mode = st.segmented_control(
        "Conteúdo das células",
        ["Venda × estoque", "Status oficial detalhado"],
        default="Venda × estoque",
        key="stack_display_mode",
    )
    st.markdown(
        "<div class='mrv-map-legend'>"
        "<span><i class='sold'></i>✓ Vendida</span>"
        "<span><i class='stock'></i>• Estoque não vendido</span>"
        "<span><i class='conflict'></i>! Posição conflitante</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    selected_indices = _building_grid(
        block,
        detailed=mode == "Status oficial detalhado",
        chart_key=f"building_grid_{selected_row['block_id']}_{mode}",
    )
    _unit_detail(block, selected_indices)

    with st.expander("Lista e exportação das unidades"):
        table = block.copy()
        if not include_missing:
            table = table.loc[table["floor"].notna()]
        display = table[[
            "unit_name", "floor", "inferred_stack", "typology", "subtypology",
            "status_unit_normalized", "is_sold",
        ]].rename(
            columns={
                "unit_name": "Unidade",
                "floor": "Andar",
                "inferred_stack": "Prumada inferida",
                "typology": "Tipologia",
                "subtypology": "Subtipologia",
                "status_unit_normalized": "Status oficial",
                "is_sold": "Vendida",
            }
        )
        st.dataframe(display, hide_index=True, use_container_width=True)
        export = table.copy()
        export.insert(0, "snapshot_date", snapshot_date)
        st.download_button(
            "Exportar unidades do bloco",
            csv_bytes(export),
            file_name=f"bloco_prumadas_{snapshot_date}.csv",
            mime="text/csv",
        )
