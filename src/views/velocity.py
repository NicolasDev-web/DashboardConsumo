from __future__ import annotations

import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..constants import COLORS
from ..exports import csv_bytes
from ..metrics import portfolio_kpis, snapshot_timeline, transition_metrics
from ..ui import br_int, br_pct, insight, kpi_card, plotly_layout, section, strong, summary_strip


def render(all_snapshots: pd.DataFrame) -> None:
    if all_snapshots.empty or all_snapshots["snapshot_date"].nunique() < 2:
        if all_snapshots.empty:
            st.info("Importe a primeira base para começar a acompanhar as vendas a partir de agora.")
            return

        latest_date = pd.to_datetime(all_snapshots["snapshot_date"]).max()
        current = all_snapshots.loc[pd.to_datetime(all_snapshots["snapshot_date"]).eq(latest_date)]
        kpis = portfolio_kpis(current)
        date_label = latest_date.strftime("%d/%m/%Y")
        insight(
            f"Ainda não dá para medir o ritmo, mas a primeira foto já está guardada: {strong(date_label)}.",
            "Você não precisa procurar uma base anterior. Na próxima atualização, importe o novo arquivo com a data em que ele foi extraído.",
        )
        summary_strip(
            [
                (br_int(kpis["sold"]), "vendidas nesta foto"),
                (br_int(kpis["stock"]), "ainda não vendidas"),
                (br_pct(kpis["consumption"]), "percentual vendido"),
            ]
        )
        section("Como a velocidade será calculada")
        st.markdown(
            "1. O dashboard compara a unidade pelo **ID da Unidade** nas duas fotos.\n"
            "2. Conta como nova venda quando o status muda de **não vendido** para **VENDIDO**.\n"
            "3. Divide as novas vendas pelos dias entre as fotos e calcula o equivalente para 30 dias.\n"
            "4. Unidades adicionadas ou removidas da planilha não são tratadas automaticamente como venda."
        )
        st.success(
            f"Próximo passo: quando receber a próxima atualização, importe-a em “Importar snapshot”. "
            f"A comparação começará em {date_label}."
        )
        with st.expander("Por que não usar as datas que já existem na planilha?"):
            st.markdown(
                "Na base inicial, **Pré Soluto** aparece em unidades vendidas e não vendidas e possui datas "
                "entre 2012 e 2029; portanto, não representa de forma segura a data da venda.\n\n"
                "A coluna **Data Base** aparece em apenas **571 unidades vendidas**, concentradas em "
                "**3 empreendimentos**. Isso cobre aproximadamente **1,2% das vendas** e o nome da coluna "
                "não confirma que seja a data de venda. Usá-la para medir o portfólio inteiro seria enganoso."
            )
        return

    timeline = snapshot_timeline(all_snapshots)
    transitions = transition_metrics(all_snapshots)
    latest = transitions.iloc[-1]
    velocity = None if pd.isna(latest["monthly_velocity"]) else int(round(latest["monthly_velocity"]))
    previous = latest["previous_date"].strftime("%d/%m")
    current = latest["snapshot_date"].strftime("%d/%m/%Y")

    headline = (
        f"Entre {html.escape(previous)} e {html.escape(current)} foram {strong(br_int(latest['new_sales']))} novas vendas"
        + (f", um ritmo de {strong(br_int(velocity))} por mês." if velocity is not None else ".")
    )
    detail = ""
    if latest["reversals"]:
        detail = f"{html.escape(br_int(latest['reversals']))} vendas foram desfeitas no período, resultando em {html.escape(br_int(latest['net_sales']))} vendas líquidas."
    insight(headline, detail, tone="attention" if latest["net_sales"] <= 0 else "positive")

    cols = st.columns(3)
    with cols[0]:
        kpi_card("Ritmo mensal", "n.d." if velocity is None else br_int(velocity), "Novas vendas a cada 30 dias", "consumption")
    with cols[1]:
        kpi_card("Novas vendas", br_int(latest["new_sales"]), f"Em {br_int(latest['days'])} dias")
    with cols[2]:
        kpi_card("Vendas desfeitas", br_int(latest["reversals"]), "Eram vendidas e voltaram ao estoque", "stock")

    section("Evolução do % vendido", "Cada ponto é uma importação da base.")
    fig = go.Figure(
        go.Scatter(
            x=timeline["snapshot_date"], y=timeline["consumption"], mode="lines+markers+text",
            text=timeline["consumption"], texttemplate="%{text:.1%}", textposition="top center",
            line={"color": COLORS["green_900"], "width": 3},
            marker={"color": COLORS["green_500"], "size": 10},
            customdata=timeline[["total", "sold", "stock"]],
            hovertemplate="%{x|%d/%m/%Y}<br>%{y:.1%} vendido<br>%{customdata[1]:,.0f} de %{customdata[0]:,.0f} unidades<extra></extra>",
        )
    )
    fig.update_yaxes(title="", tickformat=".0%", range=[0, min(1.05, max(1, timeline["consumption"].max() + .08))])
    fig.update_xaxes(title="")
    plotly_layout(fig, height=340)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    section("Vendas em cada período")
    fig = go.Figure()
    fig.add_bar(x=transitions["snapshot_date"], y=transitions["new_sales"], name="Novas vendas", marker_color=COLORS["green_900"])
    fig.add_bar(x=transitions["snapshot_date"], y=transitions["reversals"], name="Vendas desfeitas", marker_color=COLORS["error"])
    fig.update_layout(barmode="group")
    fig.update_yaxes(title="Unidades")
    plotly_layout(fig, height=340)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with st.expander("Ver todos os períodos e exportar"):
        st.caption("Unidades adicionadas ou removidas da base mudam o total, mas não contam como venda nem como venda desfeita.")
        display = transitions.rename(columns={
            "previous_date": "Data anterior", "snapshot_date": "Data atual", "days": "Dias",
            "new_sales": "Novas vendas", "reversals": "Vendas desfeitas", "net_sales": "Vendas líquidas",
            "monthly_velocity": "Ritmo mensal", "consumption_change_pp": "Variação do % vendido (p.p.)",
            "added_units": "Unidades adicionadas", "removed_units": "Unidades removidas",
        })
        st.dataframe(display, hide_index=True, use_container_width=True)
        st.download_button("Exportar períodos em CSV", csv_bytes(transitions), file_name="transicoes_snapshots.csv", mime="text/csv")
