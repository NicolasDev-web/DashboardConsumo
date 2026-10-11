from __future__ import annotations

import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..constants import COLORS
from ..exports import csv_bytes
from ..metrics import (
    block_sales,
    block_stack_sales,
    floor_metrics,
    portfolio_kpis,
    with_inferred_stack,
)
from ..ui import br_int, br_pct, empty_state, plotly_layout, section, sorted_unique, summary_strip
from .common import enterprise_picker


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
    """Compatibilidade para testes e chamadas anteriores."""

    return with_inferred_stack(frame)


def _block_summary(frame: pd.DataFrame) -> pd.DataFrame:
    return block_sales(frame)


def _compact_kpis(frame: pd.DataFrame, context: str, summary: pd.DataFrame | None = None) -> None:
    kpis = portfolio_kpis(frame)
    items = [
        (br_pct(kpis["consumption"]), "vendido"),
        (f"{br_int(kpis['sold'])} vendidas", f"de {br_int(kpis['total'])} unidades"),
    ]
    if summary is not None and not summary.empty:
        best = summary.iloc[0]
        worst = summary.iloc[-1]
        items.extend(
            [
                (str(best["block_label"]), f"maior avanço · {br_pct(best['consumption'], 0)}"),
                (str(worst["block_label"]), f"menor avanço · {br_pct(worst['consumption'], 0)}"),
            ]
        )
    else:
        items.extend([(br_int(kpis["stock"]), "ainda não vendidas"), (context, "")])
    summary_strip(items)


def _comparison_heatmap(frame: pd.DataFrame, summary: pd.DataFrame, scope: str) -> None:
    if scope == "Menor avanço":
        visible = summary.tail(min(12, len(summary))).sort_values("consumption")
    elif scope == "Maior avanço":
        visible = summary.head(min(12, len(summary)))
    else:
        visible = summary

    visible_labels = visible["block_label"].tolist()
    visible_ids = visible["block_id"].tolist()
    stack_detail = block_stack_sales(frame.loc[frame["block_id"].isin(visible_ids)])
    label_map = summary.set_index("block_id")["block_label"]
    stack_detail["block_label"] = stack_detail["block_id"].map(label_map)
    stacks = sorted(stack_detail["inferred_stack"].dropna().astype(int).unique())
    if not stacks:
        empty_state(
            "Sem prumadas comparáveis",
            "As unidades destes blocos não têm andar ou número que permita identificar a prumada.",
        )
        return

    index = pd.MultiIndex.from_product(
        [visible_labels, stacks], names=["block_label", "inferred_stack"]
    )
    grid = stack_detail.set_index(["block_label", "inferred_stack"]).reindex(index)
    total = grid["total"].fillna(0).to_numpy().reshape(len(visible_labels), len(stacks))
    sold = grid["sold"].fillna(0).to_numpy().reshape(len(visible_labels), len(stacks))
    consumption = grid["consumption"].to_numpy().reshape(len(visible_labels), len(stacks))
    text = [
        [
            "" if not total[row][column] else f"{int(sold[row][column])} vendas<br>de {int(total[row][column])} · {consumption[row][column]:.0%}"
            for column in range(len(stacks))
        ]
        for row in range(len(visible_labels))
    ]
    customdata = [
        [
            [total[row][column], sold[row][column], consumption[row][column]]
            for column in range(len(stacks))
        ]
        for row in range(len(visible_labels))
    ]

    figure = go.Figure(
        go.Heatmap(
            z=consumption,
            x=[f"{stack:02d}" for stack in stacks],
            y=visible_labels,
            text=text,
            texttemplate="%{text}",
            customdata=customdata,
            zmin=0,
            zmax=1,
            colorscale=[[0, "#EEF1EF"], [0.45, "#CFE7DA"], [0.75, "#70BE94"], [1, COLORS["green_900"]]],
            colorbar={"title": "% vendido", "tickformat": ".0%"},
            hovertemplate=(
                "%{y}<br>Prumada %{x}<br>Vendidas %{customdata[1]:.0f} de %{customdata[0]:.0f}"
                "<br>Percentual vendido %{customdata[2]:.1%}<extra></extra>"
            ),
            hoverongaps=False,
        )
    )
    stack_labels = [f"{stack:02d}" for stack in stacks]
    figure.update_xaxes(
        title="Prumada",
        side="top",
        type="category",
        tickmode="array",
        tickvals=stack_labels,
        ticktext=stack_labels,
    )
    figure.update_yaxes(autorange="reversed", title="")
    plotly_layout(
        figure,
        height=max(320, len(visible_labels) * 48 + 110),
        margin={"l": 12, "r": 16, "t": 62, "b": 20},
    )
    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
    st.caption("Cada célula mostra o percentual vendido e, abaixo, vendidas/total da prumada.")


def _block_ranking(
    summary: pd.DataFrame,
    enterprise_rate: float,
    display_metric: str,
    chart_key: str,
) -> str | None:
    metric_column = "sold" if display_metric == "Unidades vendidas" else "consumption"
    ordered = summary.sort_values(
        [metric_column, "consumption", "total", "block_label"],
        ascending=[True, True, True, True],
    ).reset_index(drop=True)
    colors = [
        COLORS["green_900"] if value >= enterprise_rate else COLORS["orange"]
        for value in ordered["consumption"]
    ]
    labels = [
        f"{br_int(row.sold)} vendidas · total {br_int(row.total)} · {br_pct(row.consumption, 0)}"
        for row in ordered.itertuples()
    ]
    x_values = ordered[metric_column]
    figure = go.Figure(
        go.Bar(
            x=x_values,
            y=ordered["block_label"],
            orientation="h",
            marker_color=colors,
            text=labels,
            textposition="outside",
            cliponaxis=False,
            customdata=ordered[["sold", "total", "stock", "consumption"]],
            hovertemplate=(
                "%{y}<br>%{customdata[0]:,.0f} unidades vendidas"
                "<br>%{customdata[1]:,.0f} unidades no bloco"
                "<br>%{customdata[3]:.1%} vendido"
                "<br>%{customdata[2]:,.0f} ainda não vendidas<extra></extra>"
            ),
        )
    )
    if display_metric == "Unidades vendidas":
        average_sold = float(summary["sold"].mean())
        figure.add_vline(
            x=average_sold,
            line_color=COLORS["muted"],
            line_dash="dot",
            annotation_text=f"média {br_int(round(average_sold))} vendas",
            annotation_position="top",
        )
        figure.update_xaxes(
            range=[0, max(1, float(summary["sold"].max())) * 1.55],
            title="Unidades vendidas",
            dtick=5 if summary["sold"].max() >= 20 else 2,
        )
    else:
        figure.add_vline(
            x=enterprise_rate,
            line_color=COLORS["muted"],
            line_dash="dot",
            annotation_text=f"média {br_pct(enterprise_rate, 0)}",
            annotation_position="top",
        )
        figure.update_xaxes(range=[0, 1.35], tickformat=".0%", title="Percentual vendido")
    figure.update_yaxes(title="", automargin=True)
    plotly_layout(
        figure,
        height=max(350, len(ordered) * 34 + 100),
        margin={"l": 8, "r": 118, "t": 28, "b": 42},
    )
    event = st.plotly_chart(
        figure,
        use_container_width=True,
        config={"displayModeBar": False},
        on_select="rerun",
        selection_mode="points",
        key=chart_key,
    )
    points = event.selection.points if event and hasattr(event, "selection") else []
    if not points:
        return None
    point_index = points[0].get("point_index", points[0].get("pointIndex"))
    if point_index is None or int(point_index) >= len(ordered):
        return None
    return str(ordered.iloc[int(point_index)]["block_label"])


def _performance_highlights(summary: pd.DataFrame, display_metric: str) -> None:
    metric_column = "sold" if display_metric == "Unidades vendidas" else "consumption"
    ordered = summary.sort_values(
        [metric_column, "consumption", "block_label"],
        ascending=[False, False, True],
    )
    best = ordered.head(3)
    worst = ordered.tail(3).sort_values([metric_column, "consumption", "block_label"])
    best_title = "Mais unidades vendidas" if metric_column == "sold" else "Maior percentual vendido"
    worst_title = "Menos unidades vendidas" if metric_column == "sold" else "Menor percentual vendido"

    def rows(frame: pd.DataFrame) -> str:
        return "".join(
            "<li>"
            f"<span>{html.escape(str(row.block_label))}</span>"
            f"<strong>{br_int(row.sold)} vendidas · {br_int(row.total)} total · {br_pct(row.consumption, 0)}</strong>"
            "</li>"
            for row in frame.itertuples()
        )

    st.markdown(
        "<div class='mrv-performance'>"
        f"<div><h4>{best_title}</h4><ol>" + rows(best) + "</ol></div>"
        f"<div><h4>{worst_title}</h4><ol>" + rows(worst) + "</ol></div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.caption("Cada linha mostra unidades vendidas, total do bloco e percentual vendido.")


def _floor_comparison(block: pd.DataFrame) -> None:
    floors = floor_metrics(block)
    if floors.empty:
        return
    best = floors.sort_values(["consumption", "sold"], ascending=False).iloc[0]
    worst = floors.sort_values(["consumption", "sold"], ascending=True).iloc[0]
    if floors["consumption"].nunique() == 1:
        st.info(
            f"Todos os andares têm o mesmo avanço: {br_pct(best['consumption'], 0)} vendido."
        )
    else:
        st.info(
            f"O {int(best['floor'])}º andar tem o maior avanço ({br_int(best['sold'])} de "
            f"{br_int(best['total'])}, {br_pct(best['consumption'], 0)}). "
            f"O menor está no {int(worst['floor'])}º andar ({br_pct(worst['consumption'], 0)})."
        )
    labels = [
        f"{br_int(row.sold)}/{br_int(row.total)} · {br_pct(row.consumption, 0)}"
        for row in floors.itertuples()
    ]
    figure = go.Figure(
        go.Bar(
            x=floors["floor"],
            y=floors["consumption"],
            marker_color=COLORS["green_700"],
            text=labels,
            textposition="outside",
            cliponaxis=False,
            customdata=floors[["sold", "total", "stock"]],
            hovertemplate=(
                "%{x:.0f}º andar<br>%{customdata[0]:,.0f} de %{customdata[1]:,.0f} vendidas"
                "<br>%{y:.1%} vendido<br>%{customdata[2]:,.0f} ainda não vendidas<extra></extra>"
            ),
        )
    )
    figure.update_xaxes(title="Andar", dtick=1)
    figure.update_yaxes(title="Percentual vendido", tickformat=".0%", range=[0, 1.16])
    plotly_layout(figure, height=320, margin={"l": 12, "r": 12, "t": 12, "b": 42})
    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})


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
            "As unidades deste bloco não têm andar ou número que permita posicioná-las.",
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
                "Unidade(s) %{customdata[0]}<br>Andar %{y:.0f}<br>Prumada %{x:02d}"
                "<br>Status %{customdata[1]}<br>Tipologia %{customdata[2]}"
                "<br>Mais de uma unidade na posição: %{customdata[3]}<extra></extra>"
            ),
            selected={"marker": {"opacity": 1}},
            unselected={"marker": {"opacity": 0.58}},
        )
    )
    floors = sorted(cells["floor"].unique())
    stacks = list(range(1, int(cells["stack"].max()) + 1))
    figure.update_xaxes(
        title="Prumada",
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
            "inferred_stack": "Prumada",
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
    selected_enterprise = enterprise_picker(enterprises, key="stacks_enterprise", allow_empty=True)
    if not selected_enterprise:
        empty_state(
            "Escolha um empreendimento",
            "Use a busca acima para comparar vendas por bloco, prumada e andar.",
        )
        return

    enterprise = working.loc[working["enterprise_name"].eq(selected_enterprise)].copy()
    city = enterprise["city"].dropna().astype(str).iloc[0] if enterprise["city"].notna().any() else "Cidade não informada"
    summary = _block_summary(enterprise)
    enterprise_kpis = portfolio_kpis(enterprise)
    _compact_kpis(enterprise, f"{selected_enterprise} · {city}", summary)

    section(
        "Vendas por bloco",
        "O número de unidades vendidas aparece primeiro; o total do bloco e o percentual aparecem ao lado.",
    )
    display_metric = st.segmented_control(
        "Comparar por",
        ["Unidades vendidas", "Percentual vendido"],
        default="Unidades vendidas",
        key="block_ranking_metric",
    ) or "Unidades vendidas"
    selected_from_ranking: str | None
    left, right = st.columns([0.7, 0.3], gap="large")
    with left:
        selected_from_ranking = _block_ranking(
            summary,
            float(enterprise_kpis["consumption"] or 0),
            display_metric,
            f"block_sales_{selected_enterprise}",
        )
        st.caption("Clique em uma barra para abrir o bloco no detalhe abaixo.")
    with right:
        _performance_highlights(summary, display_metric)

    section(
        "Como cada prumada está vendendo",
        "Prumada é a coluna de apartamentos com o mesmo final, como 101, 201 e 301.",
    )
    heatmap_scope = st.segmented_control(
        "Blocos exibidos",
        ["Menor avanço", "Maior avanço", "Todos"],
        default="Menor avanço",
        key="stack_heatmap_scope",
    ) or "Menor avanço"
    _comparison_heatmap(enterprise, summary, heatmap_scope)

    section(
        "Detalhe do bloco",
        "Selecione um bloco para comparar os andares e localizar cada unidade no espelho.",
    )
    # O detalhe abre no menor avanço para conduzir a investigação mais útil.
    block_options = summary.iloc[::-1]["block_label"].tolist()
    if st.session_state.get("_stacks_enterprise_active") != selected_enterprise:
        st.session_state["stacks_block"] = str(summary.iloc[-1]["block_label"])
        st.session_state["_stacks_enterprise_active"] = selected_enterprise
    if selected_from_ranking in block_options:
        st.session_state["stacks_block"] = selected_from_ranking
    if st.session_state.get("stacks_block") not in block_options:
        st.session_state.pop("stacks_block", None)
    selected_label = st.selectbox("Bloco", block_options, key="stacks_block")
    selected_row = summary.loc[summary["block_label"].eq(selected_label)].iloc[0]
    block = enterprise.loc[enterprise["block_id"].eq(selected_row["block_id"])].copy()
    _compact_kpis(block, str(selected_row["block_name"]))

    section("Vendas por andar", "Percentual vendido em cada andar, sempre acompanhado do volume.")
    _floor_comparison(block)

    section(
        "Espelho de unidades",
        "Cada quadrado é uma unidade: andares nas linhas e prumadas nas colunas. Clique para ver os detalhes.",
    )

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
            messages.append(f"{br_int(invalid_stack)} sem prumada identificável")
        if collision_count:
            messages.append(f"{br_int(collision_count)} unidades dividindo a mesma posição")
        st.caption("Observação sobre os dados deste bloco: " + "; ".join(messages) + ".")

    mode = st.segmented_control(
        "Mostrar nas unidades",
        ["Vendida ou não", "Status detalhado"],
        default="Vendida ou não",
        key="stack_display_mode",
    ) or "Vendida ou não"
    legend = (
        "<span><i class='sold'></i>✓ Vendida</span>"
        "<span><i class='stock'></i>• Em estoque</span>"
        "<span><i class='conflict'></i>! Mais de uma unidade na posição</span>"
    )
    if mode == "Status detalhado":
        present = set(block["status_unit_normalized"].dropna().astype(str))
        legend += "".join(
            f"<span><b>{code}</b>&nbsp;{html.escape(status.capitalize())}</span>"
            for status, code in STATUS_CODES.items()
            if status in present
        )
    st.markdown(f"<div class='mrv-map-legend'>{legend}</div>", unsafe_allow_html=True)
    selected_indices = _building_grid(
        block,
        detailed=mode == "Status detalhado",
        chart_key=f"building_grid_{selected_row['block_id']}_{mode}",
    )
    _unit_detail(block, selected_indices)

    with st.expander("Ver lista de unidades do bloco e exportar"):
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
                "inferred_stack": "Prumada",
                "typology": "Tipologia",
                "subtypology": "Subtipologia",
                "status_unit_normalized": "Status oficial",
                "is_sold": "Vendida",
            }
        )
        st.dataframe(display, hide_index=True, use_container_width=True)
        export = table.drop(columns="snapshot_date", errors="ignore")
        export.insert(0, "snapshot_date", snapshot_date)
        st.download_button(
            "Exportar unidades do bloco",
            csv_bytes(export),
            file_name=f"bloco_prumadas_{snapshot_date}.csv",
            mime="text/csv",
        )
