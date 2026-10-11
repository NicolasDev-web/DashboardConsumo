from __future__ import annotations

import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..constants import COLORS, LOW_PROGRESS_LABEL
from ..exports import csv_bytes
from ..metrics import enterprise_progress, floor_band_comparison, floor_metrics, portfolio_kpis, progress_summary, stock_by_group
from ..ui import br_int, br_pct, empty_state, insight, kpi_card, plotly_layout, section, strong
from .common import stock_composition


LOW_SAMPLE = 200


def _headline(kpis: dict, low: pd.Series, enterprise_count: int, sellable: int) -> None:
    if not kpis["stock"]:
        insight(f"Todas as {strong(br_int(kpis['total']))} unidades do recorte estão vendidas.", tone="positive")
        return

    headline = f"{strong(br_pct(kpis['consumption']))} das unidades estão vendidas. "
    concentrated = enterprise_count >= 3 and low["enterprises"] and low["stock_share"] >= 0.3
    if concentrated:
        where = (
            f"um único empreendimento"
            if low["enterprises"] == 1
            else f"apenas {strong(br_int(low['enterprises']))} empreendimentos"
        )
        headline += (
            f"Das {strong(br_int(kpis['stock']))} que restam, {strong(br_pct(low['stock_share'], 0))} estão em "
            f"{where} com menos da metade vendida."
        )
    else:
        headline += f"Restam {strong(br_int(kpis['stock']))} unidades em estoque."
    other = kpis["stock"] - sellable
    detail = (
        f"{html.escape(br_int(sellable))} delas estão em comercialização agora; "
        f"{html.escape(br_int(other))} estão reservadas ou fora de venda (não lançadas, bloqueadas ou em permuta)."
    )
    insight(headline, detail, tone="attention" if concentrated else "")


def _top_stock_chart(enterprises: pd.DataFrame) -> None:
    top = enterprises.loc[enterprises["stock"].gt(0)].nlargest(10, "stock").sort_values("stock")
    if top.empty:
        st.success("Nenhum empreendimento com estoque no recorte.")
        return
    labels = [f"{br_int(stock)} · {br_pct(rate, 0)} vendido" for stock, rate in zip(top["stock"], top["consumption"])]
    fig = go.Figure(
        go.Bar(
            x=top["stock"],
            y=top["enterprise_name"],
            orientation="h",
            text=labels,
            textposition="outside",
            cliponaxis=False,
            marker_color=COLORS["green_900"],
            customdata=top[["city", "total", "sold"]],
            hovertemplate="%{y} · %{customdata[0]}<br>%{x:,.0f} em estoque de %{customdata[1]:,.0f} unidades<extra></extra>",
        )
    )
    plotly_layout(fig, height=len(top) * 38 + 40, margin={"l": 8, "r": 130, "t": 8, "b": 8})
    fig.update_xaxes(visible=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption(
        "Ao lado de cada barra, quanto do empreendimento já foi vendido. Lançamentos recentes "
        "costumam aparecer aqui; confira a fase de cada um antes de priorizar."
    )


def _floor_section(frame: pd.DataFrame, overall: float) -> None:
    floors = floor_metrics(frame)
    if floors.empty:
        return
    section("Vendas por andar", "Unidades sem andar informado ficam fora desta comparação.")
    comparison = floor_band_comparison(frame)
    if comparison:
        low, high = comparison["low"], comparison["high"]
        gap = (low["consumption"] - high["consumption"]) * 100
        if abs(gap) >= 3:
            better = "baixos" if gap > 0 else "altos"
            st.markdown(
                f"Andares **{better}** vendem mais: até o {comparison['low_max']}º andar, "
                f"**{br_pct(low['consumption'])}** vendido; do {comparison['high_min']}º para cima, "
                f"**{br_pct(high['consumption'])}**."
            )
        else:
            st.markdown("O % vendido é parecido entre andares baixos e altos.")

    small = floors["total"].lt(LOW_SAMPLE)
    fig = go.Figure(
        go.Bar(
            x=floors["floor"],
            y=floors["consumption"],
            marker_color=["#A9D9C1" if flag else COLORS["green_700"] for flag in small],
            customdata=floors[["total", "stock"]],
            hovertemplate="%{x:.0f}º andar<br>%{y:.1%} vendido<br>%{customdata[0]:,.0f} unidades · %{customdata[1]:,.0f} em estoque<extra></extra>",
        )
    )
    fig.add_hline(
        y=overall, line_dash="dot", line_color=COLORS["text"], line_width=1,
        annotation_text=f"média {br_pct(overall)}", annotation_position="top right",
    )
    fig.update_xaxes(title="Andar", dtick=1)
    fig.update_yaxes(title="", tickformat=".0%", range=[0, 1.05])
    plotly_layout(fig, height=320, margin={"l": 8, "r": 8, "t": 24, "b": 8})
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    note = "A diferença não prova preferência por andar: prédios altos pertencem a outros empreendimentos."
    if small.any():
        note += f" Barras claras têm menos de {LOW_SAMPLE} unidades e são menos confiáveis."
    st.caption(note)


def _enterprise_table(enterprises: pd.DataFrame, snapshot_date) -> None:
    with st.expander(f"Ver todos os empreendimentos ({br_int(len(enterprises))})"):
        table = enterprises.sort_values(["stock", "total"], ascending=False)
        display = table[["city", "enterprise_name", "band", "total", "stock", "consumption"]].rename(
            columns={
                "city": "Cidade", "enterprise_name": "Empreendimento", "band": "Situação",
                "total": "Unidades", "stock": "Em estoque", "consumption": "Vendido",
            }
        )
        display["Situação"] = display["Situação"].astype(str)
        display["Vendido"] = display["Vendido"] * 100
        st.dataframe(
            display,
            hide_index=True,
            use_container_width=True,
            column_config={"Vendido": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100)},
        )
        export = table.drop(columns="band").copy()
        export.insert(0, "snapshot_date", snapshot_date)
        st.download_button(
            "Exportar resumo em CSV", csv_bytes(export),
            file_name=f"resumo_empreendimentos_{snapshot_date}.csv", mime="text/csv",
        )


def render(frame: pd.DataFrame, snapshot_date) -> None:
    if frame.empty:
        empty_state("Nenhuma unidade no recorte", "Remova alguns filtros para voltar a visualizar o portfólio.")
        return

    kpis = portfolio_kpis(frame)
    enterprises = enterprise_progress(frame)
    progress = progress_summary(frame).set_index("band")
    low = progress.loc[LOW_PROGRESS_LABEL]
    groups = stock_by_group(frame).set_index("group")["units"]
    sellable = int(groups.get("Em comercialização", 0))

    _headline(kpis, low, len(enterprises), sellable)

    cols = st.columns(3)
    with cols[0]:
        kpi_card("Vendido", br_pct(kpis["consumption"]), f"{br_int(kpis['sold'])} de {br_int(kpis['total'])} unidades", "consumption")
    with cols[1]:
        kpi_card("Em estoque", br_int(kpis["stock"]), f"{br_int(sellable)} em comercialização agora", "stock")
    with cols[2]:
        share = br_pct(low["stock_share"], 0) if kpis["stock"] else "n.d."
        kpi_card(
            "Empreendimentos com menos de 50% vendido",
            br_int(low["enterprises"]),
            f"de {br_int(len(enterprises))} · reúnem {share} do estoque",
            "attention" if low["enterprises"] else "",
        )

    if kpis["stock"]:
        left, right = st.columns([1.25, 0.75], gap="large")
        with left:
            section("Onde está o estoque", "Os 10 empreendimentos com mais unidades a vender.")
            _top_stock_chart(enterprises)
        with right:
            section("O que é esse estoque", "Nem toda unidade não vendida pode ser vendida hoje.")
            stock_composition(frame)

    _floor_section(frame, kpis["consumption"])
    _enterprise_table(enterprises, snapshot_date)
